from rest_framework import serializers
from django.contrib.auth.models import User
from .models import News, Category, UserProfile


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para Category"""
    news_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'news_count']
        read_only_fields = ['id', 'created_at', 'news_count']
    
    def get_news_count(self, obj):
        return obj.news.filter(is_active=True).count()


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para UserProfile"""
    user = UserSerializer(read_only=True)
    preferred_categories = CategorySerializer(many=True, read_only=True)
    preferred_category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_type', 'preferred_categories', 
            'preferred_category_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_user_type(self, value):
        """
        Impede que leitores se promovam a administradores.
        Apenas administradores podem alterar user_type.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                current_user_profile = request.user.profile
                # Se o usuário atual não é admin, não pode alterar user_type
                if not current_user_profile.is_admin:
                    # Se está tentando alterar para admin, bloquear
                    if value == 'admin':
                        raise serializers.ValidationError(
                            "Você não tem permissão para se promover a administrador."
                        )
                    # Se está tentando alterar o próprio tipo (mesmo que seja reader), bloquear
                    if self.instance and self.instance.user == request.user:
                        if value != self.instance.user_type:
                            raise serializers.ValidationError(
                                "Você não pode alterar seu próprio tipo de usuário."
                            )
            except UserProfile.DoesNotExist:
                # Se não tem perfil, não pode alterar user_type
                if value == 'admin':
                    raise serializers.ValidationError(
                        "Você não tem permissão para se promover a administrador."
                    )
        return value
    
    def update(self, instance, validated_data):
        preferred_category_ids = validated_data.pop('preferred_category_ids', None)
        
        # Atualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Atualizar categorias preferidas se fornecidas
        if preferred_category_ids is not None:
            categories = Category.objects.filter(id__in=preferred_category_ids)
            instance.preferred_categories.set(categories)
        
        return instance


class NewsListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de notícias (campos resumidos)"""
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'summary', 'source', 'category', 
            'author', 'published_at', 'created_at'
        ]
        read_only_fields = ['id', 'author', 'created_at']


class NewsDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes completos da notícia"""
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'summary', 'source', 
            'category', 'category_id', 'author', 'published_at', 
            'created_at', 'updated_at', 'is_active',
            'sentiment_score', 'sentiment_label', 'sentiment_confidence',
            'entities_data', 'analysis_contexts', 'analysis_timestamp'
        ]
        read_only_fields = [
            'id', 'author', 'created_at', 'updated_at',
            'sentiment_score', 'sentiment_label', 'sentiment_confidence',
            'entities_data', 'analysis_contexts', 'analysis_timestamp'
        ]
    
    def create(self, validated_data):
        # O autor será definido na view baseado no usuário autenticado
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Categoria não encontrada.")
        return value


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de notícias (apenas admins)"""
    category_id = serializers.IntegerField()
    
    class Meta:
        model = News
        fields = [
            'title', 'content', 'summary', 'source', 
            'category_id', 'published_at', 'is_active'
        ]
    
    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Categoria não encontrada.")
        return value
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        validated_data['category'] = category
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            category = Category.objects.get(id=category_id)
            validated_data['category'] = category
        return super().update(instance, validated_data)


class NewsUploadSerializer(serializers.Serializer):
    """Serializer para upload de arquivo JSON com notícias no novo formato simplificado"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Valida o arquivo JSON enviado no novo formato"""
        # Verificar extensão do arquivo
        if not value.name.endswith('.json'):
            raise serializers.ValidationError("Apenas arquivos JSON são permitidos.")
        
        # Verificar tamanho do arquivo (máximo 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Arquivo muito grande. Tamanho máximo: 10MB.")
        
        # Tentar fazer parse do JSON
        try:
            import json
            content = value.read()
            value.seek(0)  # Reset file pointer
            data = json.loads(content.decode('utf-8'))
            
            # Verificar se é uma lista
            if not isinstance(data, list):
                raise serializers.ValidationError("O arquivo JSON deve conter uma lista de notícias.")
            
            # Verificar se não está vazio
            if len(data) == 0:
                raise serializers.ValidationError("O arquivo JSON não pode estar vazio.")
            
            # Validar estrutura básica de cada notícia no novo formato
            for i, news_item in enumerate(data):
                if not isinstance(news_item, dict):
                    raise serializers.ValidationError(f"Item {i+1}: deve ser um objeto JSON.")
                
                # Verificar campo obrigatório 'noticia'
                if 'noticia' not in news_item:
                    raise serializers.ValidationError(f"Item {i+1}: campo 'noticia' é obrigatório.")
                
                # Verificar se o campo 'noticia' não está vazio
                if not news_item['noticia'] or not news_item['noticia'].strip():
                    raise serializers.ValidationError(f"Item {i+1}: campo 'noticia' não pode estar vazio.")
                
                # Verificar se o conteúdo tem tamanho mínimo
                if len(news_item['noticia'].strip()) < 50:
                    raise serializers.ValidationError(f"Item {i+1}: conteúdo da notícia muito curto (mínimo 50 caracteres).")
            
        except json.JSONDecodeError as e:
            raise serializers.ValidationError(f"Arquivo JSON inválido: {str(e)}")
        except UnicodeDecodeError:
            raise serializers.ValidationError("Erro de codificação. Use UTF-8.")
        
        return value
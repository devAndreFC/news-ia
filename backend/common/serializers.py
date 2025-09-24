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
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
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
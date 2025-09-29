from django.shortcuts import render
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone
from datetime import timedelta
from .models import News, Category, UserProfile
from .serializers import (
    NewsListSerializer, NewsDetailSerializer, NewsCreateUpdateSerializer,
    CategorySerializer, UserProfileSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsAdminOrPublicReadOnly, IsSuperuserOrPublicReadOnly


@extend_schema(
    methods=['GET'],
    summary="Listar todas as categorias disponíveis",
    description="Retorna uma lista de todas as categorias disponíveis para preferências",
    tags=['Preferences'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'categories': {
                    'type': 'array',
                    'items': CategorySerializer
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories_for_preferences(request):
    """
    Lista todas as categorias disponíveis para seleção de preferências.
    
    Endpoint público que retorna todas as categorias que podem ser
    selecionadas como preferências pelos usuários.
    """
    categories = Category.objects.all().order_by('name')
    serializer = CategorySerializer(categories, many=True)
    return Response({
        'categories': serializer.data
    }, status=status.HTTP_200_OK)

@extend_schema(
    methods=['POST'],
    summary="Registrar usuário",
    description="Cadastra um novo usuário no sistema",
    tags=['Authentication'],
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'description': 'Nome de usuário único'},
            'password': {'type': 'string', 'description': 'Senha do usuário'}
        },
        'required': ['username', 'password'],
        'example': {
            'username': 'novo_usuario',
            'password': 'minhasenha123'
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
                'access_token': {'type': 'string'},
                'refresh_token': {'type': 'string'}
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Cadastra um novo usuário no sistema.
    
    Cria um novo usuário com username e senha, retornando tokens JWT para autenticação.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username e password são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username já existe'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.create(
            username=username,
            password=make_password(password)
        )
        
        # Gerar tokens JWT para o usuário recém-criado
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Usuário criado com sucesso',
            'user_id': user.id,
            'username': user.username,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': 'Erro ao criar usuário'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    methods=['POST'],
    summary="Login de usuário",
    description="Autentica um usuário no sistema usando Django sessions",
    tags=['Authentication'],
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'description': 'Nome de usuário'},
            'password': {'type': 'string', 'description': 'Senha do usuário'}
        },
        'required': ['username', 'password'],
        'example': {
            'username': 'usuario_exemplo',
            'password': 'senha123'
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
                'email': {'type': 'string'},
                'profile': {
                    'type': 'object',
                    'properties': {
                        'user_type': {'type': 'string'},
                        'is_admin': {'type': 'boolean'},
                        'is_superuser': {'type': 'boolean'}
                    }
                },
                'access': {'type': 'string'},
                'refresh': {'type': 'string'}
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        401: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Autentica um usuário no sistema usando Django sessions.
    
    Valida as credenciais e cria uma sessão para o usuário.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username e password são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # Buscar ou criar perfil do usuário
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Se não existe perfil, criar um
            user_type = 'admin' if user.is_superuser else 'reader'
            profile = UserProfile.objects.create(user=user, user_type=user_type)
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login realizado com sucesso',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'profile': {
                'user_type': profile.user_type,
                'is_admin': profile.is_admin,
                'is_superuser': user.is_superuser
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Credenciais inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    methods=['POST'],
    summary="Logout de usuário",
    description="Faz logout do usuário autenticado, encerrando a sessão",
    tags=['Authentication'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Faz logout do usuário autenticado.
    
    Encerra a sessão atual do usuário no sistema.
    """
    logout(request)
    return Response(
        {'message': 'Logout realizado com sucesso'}, 
        status=status.HTTP_200_OK
    )


@extend_schema_view(
    list=extend_schema(
        summary="Listar categorias",
        description="Retorna uma lista de todas as categorias disponíveis",
        tags=['Categories'],
        parameters=[
            OpenApiParameter(
                name='search',
                description='Buscar por nome ou descrição da categoria',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='ordering',
                description='Ordenar por: name, created_at, -name, -created_at',
                required=False,
                type=OpenApiTypes.STR
            ),
        ]
    ),
    create=extend_schema(
        summary="Criar categoria",
        description="Cria uma nova categoria (apenas superusers)",
        tags=['Categories']
    ),
    retrieve=extend_schema(
        summary="Obter categoria",
        description="Retorna os detalhes de uma categoria específica",
        tags=['Categories']
    ),
    update=extend_schema(
        summary="Atualizar categoria",
        description="Atualiza uma categoria existente (apenas superusers)",
        tags=['Categories']
    ),
    partial_update=extend_schema(
        summary="Atualizar categoria parcialmente",
        description="Atualiza parcialmente uma categoria existente (apenas superusers)",
        tags=['Categories']
    ),
    destroy=extend_schema(
        summary="Excluir categoria",
        description="Exclui uma categoria (apenas superusers)",
        tags=['Categories']
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias de notícias.
    
    Permite operações CRUD completas para categorias.
    Leitura pública (sem autenticação), apenas superusers podem modificar.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperuserOrPublicReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="Listar notícias",
        description="Retorna uma lista paginada de notícias ativas",
        tags=['News'],
        parameters=[
            OpenApiParameter(
                name='category',
                description='Filtrar por ID da categoria',
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='source',
                description='Filtrar por fonte da notícia',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='author',
                description='Filtrar por ID do autor',
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='period',
                description='Filtrar por período: day (último dia), week (última semana), month (último mês)',
                required=False,
                type=OpenApiTypes.STR,
                enum=['day', 'week', 'month']
            ),
            OpenApiParameter(
                name='search',
                description='Buscar no título, conteúdo ou resumo',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='ordering',
                description='Ordenar por: published_at, created_at, title (use - para ordem decrescente)',
                required=False,
                type=OpenApiTypes.STR
            ),
        ]
    ),
    create=extend_schema(
        summary="Criar notícia",
        description="Cria uma nova notícia (apenas administradores)",
        tags=['News']
    ),
    retrieve=extend_schema(
        summary="Obter notícia",
        description="Retorna os detalhes completos de uma notícia específica",
        tags=['News']
    ),
    update=extend_schema(
        summary="Atualizar notícia",
        description="Atualiza uma notícia existente (apenas administradores)",
        tags=['News']
    ),
    partial_update=extend_schema(
        summary="Atualizar notícia parcialmente",
        description="Atualiza parcialmente uma notícia existente (apenas administradores)",
        tags=['News']
    ),
    destroy=extend_schema(
        summary="Excluir notícia",
        description="Exclui uma notícia (apenas administradores)",
        tags=['News']
    ),
)
class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar notícias.
    
    Permite operações CRUD completas para notícias.
    Leitura pública (sem autenticação), apenas administradores podem modificar.
    Suporte a filtros por categoria, fonte, autor e busca textual.
    """
    queryset = News.objects.filter(is_active=True)
    permission_classes = [IsAdminOrPublicReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'source', 'author']
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at']
    
    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação
        """
        if self.action == 'list':
            return NewsListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NewsCreateUpdateSerializer
        else:
            return NewsDetailSerializer
    
    def get_queryset(self):
        """
        Filtra notícias baseado no tipo de usuário, preferências e período
        """
        queryset = News.objects.filter(is_active=True)
        
        # Aplicar filtro de período se especificado
        period = self.request.query_params.get('period')
        if period:
            now = timezone.now()
            if period == 'day':
                # Últimas 24 horas
                start_date = now - timedelta(days=1)
            elif period == 'week':
                # Últimos 7 dias
                start_date = now - timedelta(days=7)
            elif period == 'month':
                # Últimos 30 dias
                start_date = now - timedelta(days=30)
            else:
                # Período inválido, ignorar filtro
                start_date = None
            
            if start_date:
                queryset = queryset.filter(published_at__gte=start_date)
        
        # Se o usuário está autenticado
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
                
                # Administradores veem todas as notícias sem filtro de preferências
                if profile.is_admin:
                    queryset = queryset.order_by('-published_at')
                else:
                    # Usuários comuns seguem o filtro de preferências
                    # Se o usuário tem preferências e não está filtrando por categoria específica,
                    # mostra APENAS notícias das categorias preferidas
                    preferred_categories = profile.preferred_categories.all()
                    category_filter = self.request.query_params.get('category')
                    
                    if preferred_categories.exists() and not category_filter:
                        # Filtra apenas notícias das categorias preferidas
                        queryset = queryset.filter(category__in=preferred_categories)
                    
                    # Ordenação por data de publicação
                    queryset = queryset.order_by('-published_at')
                    
            except UserProfile.DoesNotExist:
                queryset = queryset.order_by('-published_at')
        else:
            # Usuário não autenticado vê todas as notícias
            queryset = queryset.order_by('-published_at')
        
        return queryset
    
    @extend_schema(
        summary="Minhas preferências de notícias",
        description="Retorna notícias baseadas nas categorias preferidas do usuário autenticado",
        tags=['News'],
        responses={200: NewsListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_preferences(self, request):
        """
        Retorna notícias baseadas nas preferências do usuário autenticado.
        
        Filtra as notícias pelas categorias marcadas como preferidas no perfil do usuário.
        Se o usuário não tiver preferências definidas, retorna todas as notícias.
        """
        try:
            profile = request.user.profile
            preferred_categories = profile.preferred_categories.all()
            
            if preferred_categories.exists():
                queryset = self.get_queryset().filter(category__in=preferred_categories)
            else:
                queryset = self.get_queryset()
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = NewsListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = NewsListSerializer(queryset, many=True)
            return Response(serializer.data)
            
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil do usuário não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Estatísticas administrativas",
        description="Retorna estatísticas gerais do sistema (apenas para administradores)",
        tags=['Admin'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_news': {'type': 'integer', 'description': 'Total de notícias no sistema'},
                    'total_categories': {'type': 'integer', 'description': 'Total de categorias'},
                    'total_users': {'type': 'integer', 'description': 'Total de usuários'},
                    'active_news': {'type': 'integer', 'description': 'Total de notícias ativas'},
                }
            }
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def admin_stats(self, request):
        """
        Retorna estatísticas gerais do sistema para administradores.
        
        Inclui contagem total de notícias, categorias e usuários no sistema.
        """
        # Verificar se o usuário é admin
        try:
            profile = request.user.profile
            if not profile.is_admin and not request.user.is_superuser:
                return Response(
                    {'error': 'Acesso negado. Apenas administradores podem acessar estas estatísticas.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except UserProfile.DoesNotExist:
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Acesso negado. Apenas administradores podem acessar estas estatísticas.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Calcular estatísticas
        total_news = News.objects.count()  # Todas as notícias, incluindo inativas
        active_news = News.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        total_users = User.objects.count()
        
        return Response({
            'total_news': total_news,
            'active_news': active_news,
            'total_categories': total_categories,
            'total_users': total_users,
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar perfis de usuário",
        description="Retorna perfis de usuário (apenas administradores veem todos, usuários comuns veem apenas o próprio)",
        tags=['User Profile']
    ),
    create=extend_schema(
        summary="Criar perfil de usuário",
        description="Cria um novo perfil de usuário",
        tags=['User Profile']
    ),
    retrieve=extend_schema(
        summary="Obter perfil de usuário",
        description="Retorna os detalhes de um perfil específico",
        tags=['User Profile']
    ),
    update=extend_schema(
        summary="Atualizar perfil de usuário",
        description="Atualiza um perfil de usuário existente",
        tags=['User Profile']
    ),
    partial_update=extend_schema(
        summary="Atualizar perfil parcialmente",
        description="Atualiza parcialmente um perfil de usuário existente",
        tags=['User Profile']
    ),
    destroy=extend_schema(
        summary="Excluir perfil de usuário",
        description="Exclui um perfil de usuário",
        tags=['User Profile']
    ),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar perfis de usuário.
    
    Permite operações CRUD para perfis de usuário.
    Usuários podem gerenciar apenas seu próprio perfil, administradores podem gerenciar todos.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """
        Usuários só podem ver seu próprio perfil, admins veem todos
        """
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
                if profile.is_admin:
                    return UserProfile.objects.all()
            except UserProfile.DoesNotExist:
                pass
        
        return UserProfile.objects.filter(user=self.request.user)
    
    @extend_schema(
        methods=['GET'],
        summary="Obter meu perfil",
        description="Retorna o perfil do usuário autenticado",
        tags=['User Profile'],
        responses={200: UserProfileSerializer}
    )
    @extend_schema(
        methods=['PATCH'],
        summary="Atualizar meu perfil",
        description="Atualiza parcialmente o perfil do usuário autenticado",
        tags=['User Profile'],
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retorna ou atualiza o perfil do usuário autenticado.
        
        GET: Retorna os dados do perfil atual
        PATCH: Atualiza parcialmente os dados do perfil
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Criar perfil se não existir
            profile = UserProfile.objects.create(user=request.user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=['GET'],
        summary="Obter minhas preferências",
        description="Retorna as categorias preferidas do usuário autenticado",
        tags=['User Preferences'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'preferred_categories': {
                        'type': 'array',
                        'items': CategorySerializer
                    }
                }
            }
        }
    )
    @extend_schema(
        methods=['PUT'],
        summary="Atualizar minhas preferências",
        description="Atualiza as categorias preferidas do usuário autenticado",
        tags=['User Preferences'],
        request={
            'type': 'object',
            'properties': {
                'preferred_categories': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'Lista de IDs das categorias preferidas'
                }
            },
            'required': ['preferred_categories'],
            'example': {
                'preferred_categories': [1, 2, 3]
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'preferred_categories': {
                        'type': 'array',
                        'items': CategorySerializer
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated], url_path='me/preferences')
    def preferences(self, request):
        """
        Gerencia as preferências de categorias do usuário autenticado.
        
        GET: Retorna as categorias preferidas do usuário
        PUT: Atualiza as categorias preferidas do usuário
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Criar perfil se não existir
            profile = UserProfile.objects.create(user=request.user)
        
        if request.method == 'GET':
            # Retorna as categorias preferidas do usuário
            preferred_categories = profile.preferred_categories.all()
            serializer = CategorySerializer(preferred_categories, many=True)
            return Response({
                'preferred_categories': serializer.data
            })
        
        elif request.method == 'PUT':
            # Atualiza as categorias preferidas do usuário
            category_ids = request.data.get('preferred_categories', [])
            
            if not isinstance(category_ids, list):
                return Response(
                    {'error': 'preferred_categories deve ser uma lista de IDs'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar se todas as categorias existem
            try:
                categories = Category.objects.filter(id__in=category_ids)
                if len(categories) != len(category_ids):
                    invalid_ids = set(category_ids) - set(categories.values_list('id', flat=True))
                    return Response(
                        {'error': f'Categorias não encontradas: {list(invalid_ids)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Atualizar as preferências
                profile.preferred_categories.set(categories)
                profile.save()
                
                # Retornar as categorias atualizadas
                serializer = CategorySerializer(categories, many=True)
                return Response({
                    'message': 'Preferências atualizadas com sucesso',
                    'preferred_categories': serializer.data
                })
                
            except Exception as e:
                return Response(
                    {'error': f'Erro ao atualizar preferências: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )


@extend_schema(
    methods=['GET'],
    summary="Estatísticas administrativas",
    description="Retorna estatísticas gerais do sistema (apenas para administradores)",
    tags=['Admin'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_news': {'type': 'integer', 'description': 'Total de notícias no sistema'},
                'total_categories': {'type': 'integer', 'description': 'Total de categorias'},
                'total_users': {'type': 'integer', 'description': 'Total de usuários'},
                'active_news': {'type': 'integer', 'description': 'Total de notícias ativas'},
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """
    Retorna estatísticas gerais do sistema para administradores.
    
    Inclui contagem total de notícias, categorias e usuários no sistema.
    """
    # Verificar se o usuário é admin
    try:
        profile = request.user.profile
        if not profile.is_admin and not request.user.is_superuser:
            return Response(
                {'error': 'Acesso negado. Apenas administradores podem acessar estas estatísticas.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return Response(
                {'error': 'Acesso negado. Apenas administradores podem acessar estas estatísticas.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Calcular estatísticas
    total_news = News.objects.count()  # Todas as notícias, incluindo inativas
    active_news = News.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    
    return Response({
        'total_news': total_news,
        'active_news': active_news,
        'total_categories': total_categories,
        'total_users': total_users,
    })


@extend_schema(
    methods=['POST'],
    summary="Upload de arquivo JSON com notícias",
    description="Endpoint para upload de arquivo JSON contendo múltiplas notícias para processamento automático",
    tags=['News'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Arquivo JSON com lista de notícias'
                }
            }
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'processed_count': {'type': 'integer'},
                'total_count': {'type': 'integer'},
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'status': {'type': 'string'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'},
                'details': {'type': 'object'}
            }
        },
        403: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_news_json(request):
    """
    Upload de arquivo JSON com múltiplas notícias para processamento automático.
    
    Apenas administradores podem usar este endpoint.
    O arquivo deve conter uma lista de objetos JSON com os campos:
    - title: título da notícia
    - content: conteúdo completo
    - source: fonte da notícia
    - published_at: data de publicação (ISO format)
    - author: nome do autor (opcional)
    - summary: resumo da notícia (opcional)
    
    NOTA: O campo 'category' é opcional. Se não fornecido, a IA classificará automaticamente
    a notícia em uma das 10 categorias fixas do sistema.
    """
    # Verificar se o usuário é admin
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        return Response(
            {'error': 'Apenas administradores podem fazer upload de notícias.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validar o arquivo enviado
    from .serializers import NewsUploadSerializer
    serializer = NewsUploadSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Arquivo inválido', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Processar o arquivo JSON
    try:
        import json
        from datetime import datetime
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        file = serializer.validated_data['file']
        content = file.read().decode('utf-8')
        news_data = json.loads(content)
        
        processed_count = 0
        total_count = len(news_data)
        results = []
        
        # Log inicial da fila de processamento
        logger.info(f"INICIANDO PROCESSAMENTO DE NOTÍCIAS")
        logger.info(f"Total de notícias na fila: {total_count}")
        logger.info(f"Usuário: {request.user.username}")
        logger.info(f"Arquivo: {file.name}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"=" * 60)
        
        for index, news_item in enumerate(news_data, 1):
            try:
                # Log do progresso atual
                logger.info(f"📰 Processando notícia {index}/{total_count}")
                
                # Extrair conteúdo completo da notícia no novo formato
                news_content = news_item['noticia'].strip()
                
                if not news_content:
                    logger.warning(f"Notícia {index}: Conteúdo vazio - PULANDO")
                    results.append({
                        'content_preview': 'Conteúdo vazio',
                        'status': 'error',
                        'message': 'Conteúdo da notícia está vazio'
                    })
                    continue
                
                logger.info(f"🔍 Notícia {index}: Extraindo informações com IA...")
                
                # Usar IA para extrair informações estruturadas do conteúdo
                from .services import extract_news_info_from_content
                extraction_result = extract_news_info_from_content(news_content)
                
                if not extraction_result['success']:
                    logger.error(f"Notícia {index}: Falha na extração - {extraction_result['error']}")
                    results.append({
                        'content_preview': news_content[:100] + '...',
                        'status': 'error',
                        'message': f'Erro na extração de informações: {extraction_result["error"]}'
                    })
                    continue
                
                # Extrair dados da resposta da IA
                extracted_data = extraction_result['data']
                title = extracted_data.get('title', 'Título não identificado').strip()
                content = extracted_data.get('content', news_content).strip()
                summary = extracted_data.get('summary', '').strip()
                source = extracted_data.get('source', 'Fonte não identificada').strip()
                
                logger.info(f"Notícia {index}: Informações extraídas - Título: '{title[:50]}...'")
                logger.info(f" Notícia {index}: Classificando categoria com IA...")
                
                # Classificar automaticamente usando IA
                from .services import classify_news_automatically
                classification_result = classify_news_automatically(title, content, summary)
                
                category = Category.objects.get(name=classification_result['category'])
                classification_info = f" (IA: {category.name}, confiança: {classification_result['confidence']:.2f})"
                
                logger.info(f"📂 Notícia {index}: Categoria classificada - {category.name} (confiança: {classification_result['confidence']:.2f})")
                
                # Usar data atual como padrão
                published_at = timezone.now()
                
                logger.info(f"💾 Notícia {index}: Criando registro no banco de dados...")
                
                # Criar a notícia
                news = News.objects.create(
                    title=title,
                    content=content,
                    summary=summary[:500] if summary else '',  # Limitar resumo
                    source=source,
                    category=category,
                    author=request.user,
                    published_at=published_at,
                    is_active=True
                )
                
                logger.info(f"🧠 Notícia {index}: Iniciando análise de sentimento...")
                
                # Realizar análise automática da notícia
                try:
                    from .services import analyze_single_news
                    analysis_result = analyze_single_news(news)
                    
                    if analysis_result['success']:
                        sentiment_label = analysis_result['sentiment']['label']
                        sentiment_score = analysis_result['sentiment']['score']
                        logger.info(f"😊 Notícia {index}: Sentimento analisado - {sentiment_label} (score: {sentiment_score:.2f})")
                        analysis_info = f" | Análise: {sentiment_label}"
                    else:
                        logger.error(f"❌ Notícia {index}: Erro na análise de sentimento")
                        analysis_info = " | Análise: erro"
                except Exception as analysis_error:
                    logger.error(f"❌ Notícia {index}: Falha na análise - {str(analysis_error)}")
                    analysis_info = f" | Análise: falhou - {str(analysis_error)}"
                
                processed_count += 1
                logger.info(f"✅ Notícia {index}: CONCLUÍDA - ID: {news.id}")
                logger.info(f"📊 Progresso: {processed_count}/{total_count} notícias processadas")
                
                results.append({
                    'title': news.title,
                    'status': 'success',
                    'message': f'Notícia criada com sucesso{classification_info}{analysis_info}'
                })
                
            except Exception as e:
                logger.error(f"💥 Notícia {index}: ERRO CRÍTICO - {str(e)}")
                results.append({
                    'content_preview': news_item.get('noticia', 'Conteúdo não disponível')[:100] + '...',
                    'status': 'error',
                    'message': f'Erro ao processar: {str(e)}'
                })
        
        # Log final do processamento
        logger.info(f"=" * 60)
        logger.info(f"🏁 PROCESSAMENTO FINALIZADO")
        logger.info(f"✅ Sucessos: {processed_count}")
        logger.info(f"❌ Falhas: {total_count - processed_count}")
        logger.info(f"📊 Total: {total_count}")
        logger.info(f"⏰ Concluído em: {datetime.now().isoformat()}")
        logger.info(f"=" * 60)
        
        return Response({
            'message': f'Processamento concluído. {processed_count} de {total_count} notícias foram criadas.',
            'processed_count': processed_count,
            'total_count': total_count,
            'results': results
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro interno no processamento: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    methods=['POST'],
    summary="Análise de sentimentos e entidades",
    description="Endpoint para análise manual de sentimentos e entidades de notícias existentes",
    tags=['News'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'news_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'Lista de IDs das notícias para análise (opcional - se vazio, analisa todas)'
                },
                'force_reanalysis': {
                    'type': 'boolean',
                    'description': 'Forçar re-análise mesmo se já foi analisada (padrão: false)'
                }
            }
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'total_processed': {'type': 'integer'},
                'success_count': {'type': 'integer'},
                'error_count': {'type': 'integer'},
                'errors': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'news_id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'error': {'type': 'string'}
                        }
                    }
                }
            }
        },
        403: {'description': 'Acesso negado - apenas administradores'},
        400: {'description': 'Dados inválidos'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_news(request):
    """
    Análise manual de sentimentos e entidades para notícias existentes.
    
    Apenas administradores podem usar este endpoint.
    """
    # Verificar se o usuário é admin
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        return Response(
            {'error': 'Apenas administradores podem executar análises.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .services import NewsAnalysisService
        
        # Obter parâmetros da requisição
        news_ids = request.data.get('news_ids', [])
        force_reanalysis = request.data.get('force_reanalysis', False)
        
        # Determinar quais notícias analisar
        if news_ids:
            # Analisar notícias específicas
            news_queryset = News.objects.filter(id__in=news_ids)
            if not news_queryset.exists():
                return Response(
                    {'error': 'Nenhuma notícia encontrada com os IDs fornecidos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Analisar todas as notícias
            if force_reanalysis:
                news_queryset = News.objects.all()
            else:
                # Apenas notícias que ainda não foram analisadas
                news_queryset = News.objects.filter(analysis_timestamp__isnull=True)
        
        if not news_queryset.exists():
            return Response({
                'message': 'Nenhuma notícia encontrada para análise.',
                'total_processed': 0,
                'success_count': 0,
                'error_count': 0,
                'errors': []
            })
        
        # Executar análise
        analysis_service = NewsAnalysisService()
        results = analysis_service.batch_analyze_news(news_queryset)
        
        return Response({
            'message': f'Análise concluída. {results["success_count"]} de {results["total_processed"]} notícias foram analisadas com sucesso.',
            'total_processed': results['total_processed'],
            'success_count': results['success_count'],
            'error_count': results['error_count'],
            'errors': results['errors']
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro interno na análise: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    methods=['POST'],
    summary="Classificação automática de categorias",
    description="Endpoint para classificação automática de categorias de notícias",
    tags=['News'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'news_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'Lista de IDs das notícias para classificar (opcional - se vazio, classifica todas)'
                },
                'auto_assign': {
                    'type': 'boolean',
                    'description': 'Atribuir automaticamente categorias com alta confiança (padrão: false)'
                },
                'confidence_threshold': {
                    'type': 'number',
                    'description': 'Limite de confiança para auto-atribuição (padrão: 0.3)'
                }
            }
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'total_processed': {'type': 'integer'},
                'high_confidence_count': {'type': 'integer'},
                'auto_assigned_count': {'type': 'integer'},
                'suggestions': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'news_id': {'type': 'integer'},
                            'news_title': {'type': 'string'},
                            'classification': {
                                'type': 'object',
                                'properties': {
                                    'category': {'type': 'string'},
                                    'confidence': {'type': 'number'}
                                }
                            },
                            'auto_assigned': {'type': 'boolean'}
                        }
                    }
                }
            }
        },
        403: {'description': 'Acesso negado - apenas administradores'},
        400: {'description': 'Dados inválidos'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def classify_news_categories(request):
    """
    Classificação automática de categorias para notícias.
    
    Apenas administradores podem usar este endpoint.
    """
    # Verificar se o usuário é admin
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        return Response(
            {'error': 'Apenas administradores podem executar classificações.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .services import NewsAnalysisService
        
        # Obter parâmetros da requisição
        news_ids = request.data.get('news_ids', [])
        auto_assign = request.data.get('auto_assign', False)
        confidence_threshold = request.data.get('confidence_threshold', 0.3)
        
        # Determinar quais notícias classificar
        if news_ids:
            news_queryset = News.objects.filter(id__in=news_ids)
            if not news_queryset.exists():
                return Response(
                    {'error': 'Nenhuma notícia encontrada com os IDs fornecidos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            news_queryset = News.objects.all()
        
        if not news_queryset.exists():
            return Response({
                'message': 'Nenhuma notícia encontrada para classificação.',
                'total_processed': 0,
                'suggestions': []
            })
        
        # Executar classificação
        analysis_service = NewsAnalysisService()
        suggestions = analysis_service.suggest_categories_for_news_batch(news_queryset)
        
        # Estatísticas
        total_processed = len(suggestions)
        auto_assigned = 0
        high_confidence = 0
        
        # Processar sugestões
        processed_suggestions = []
        for suggestion in suggestions:
            classification = suggestion['classification']
            
            # Contar estatísticas
            if classification['confidence'] >= confidence_threshold:
                high_confidence += 1
            
            # Auto-atribuir se solicitado e confiança suficiente
            if (auto_assign and 
                classification['confidence'] >= confidence_threshold and 
                suggestion['category_object']):
                
                try:
                    news = News.objects.get(id=suggestion['news_id'])
                    news.category = suggestion['category_object']
                    news.save()
                    auto_assigned += 1
                    suggestion['auto_assigned'] = True
                except Exception as e:
                    suggestion['auto_assigned'] = False
                    suggestion['assignment_error'] = str(e)
            else:
                suggestion['auto_assigned'] = False
            
            processed_suggestions.append(suggestion)
        
        return Response({
            'message': f'Classificação concluída. {total_processed} notícias processadas.',
            'total_processed': total_processed,
            'high_confidence_count': high_confidence,
            'auto_assigned_count': auto_assigned,
            'confidence_threshold': confidence_threshold,
            'suggestions': processed_suggestions
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro interno na classificação: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    methods=['GET'],
    summary="Sugestão de categoria para notícia",
    description="Obtém sugestão de categoria para uma notícia específica",
    tags=['News'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'news_id': {'type': 'integer'},
                'news_title': {'type': 'string'},
                'current_category': {'type': 'string'},
                'classification': {
                    'type': 'object',
                    'properties': {
                        'category': {'type': 'string'},
                        'confidence': {'type': 'number'}
                    }
                },
                'suggested_category_exists': {'type': 'boolean'}
            }
        },
        404: {'description': 'Notícia não encontrada'},
        500: {'description': 'Erro interno'}
    }
)
@api_view(['GET'])
def test_simple_view(request, news_id=None):
    """
    View de teste simples.
    """
    if news_id:
        return Response({'message': f'Test successful for news_id: {news_id}'})
    else:
        return Response({'message': 'Simple test successful'})

@api_view(['GET'])
def get_category_suggestions(request, news_id):
    """
    Obtém sugestão de categoria para uma notícia específica.
    """
    try:
        news = News.objects.get(id=news_id)
        
        # Executar classificação
        from .services import NewsAnalysisService
        analysis_service = NewsAnalysisService()
        result = analysis_service.classify_news_category(news)
        
        if result['success']:
            return Response({
                'news_id': news_id,
                'news_title': news.title,
                'current_category': news.category.name if news.category else None,
                'classification': result['classification'],
                'suggested_category_exists': result['category_object'] is not None
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except News.DoesNotExist:
        return Response(
            {'error': 'Notícia não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erro interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

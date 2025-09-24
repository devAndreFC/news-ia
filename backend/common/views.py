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
from .models import News, Category, UserProfile
from .serializers import (
    NewsListSerializer, NewsDetailSerializer, NewsCreateUpdateSerializer,
    CategorySerializer, UserProfileSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

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
        'required': ['username', 'password']
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
        'required': ['username', 'password']
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
                'email': {'type': 'string'}
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
        return Response({
            'message': 'Login realizado com sucesso',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
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
        description="Cria uma nova categoria (apenas administradores)",
        tags=['Categories']
    ),
    retrieve=extend_schema(
        summary="Obter categoria",
        description="Retorna os detalhes de uma categoria específica",
        tags=['Categories']
    ),
    update=extend_schema(
        summary="Atualizar categoria",
        description="Atualiza uma categoria existente (apenas administradores)",
        tags=['Categories']
    ),
    partial_update=extend_schema(
        summary="Atualizar categoria parcialmente",
        description="Atualiza parcialmente uma categoria existente (apenas administradores)",
        tags=['Categories']
    ),
    destroy=extend_schema(
        summary="Excluir categoria",
        description="Exclui uma categoria (apenas administradores)",
        tags=['Categories']
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias de notícias.
    
    Permite operações CRUD completas para categorias.
    Usuários autenticados podem visualizar, apenas administradores podem modificar.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
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
    Usuários autenticados podem visualizar, apenas administradores podem modificar.
    Suporte a filtros por categoria, fonte, autor e busca textual.
    """
    queryset = News.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
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
        Filtra notícias baseado no tipo de usuário
        """
        queryset = News.objects.filter(is_active=True)
        
        # Se o usuário não é admin, só mostra notícias ativas
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
                if not profile.is_admin:
                    queryset = queryset.filter(is_active=True)
            except UserProfile.DoesNotExist:
                queryset = queryset.filter(is_active=True)
        else:
            queryset = queryset.filter(is_active=True)
        
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

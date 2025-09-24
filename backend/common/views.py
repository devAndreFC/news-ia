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
from .models import News, Category, UserProfile
from .serializers import (
    NewsListSerializer, NewsDetailSerializer, NewsCreateUpdateSerializer,
    CategorySerializer, UserProfileSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Cadastra um novo usuário com username e senha
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


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Autentica um usuário usando Django sessions
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Faz logout do usuário
    """
    logout(request)
    return Response(
        {'message': 'Logout realizado com sucesso'}, 
        status=status.HTTP_200_OK
    )


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar notícias
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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_preferences(self, request):
        """
        Retorna notícias baseadas nas preferências do usuário
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


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar perfis de usuário
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
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retorna ou atualiza o perfil do usuário atual
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

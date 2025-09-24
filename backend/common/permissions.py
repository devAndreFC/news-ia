from rest_framework import permissions
from .models import UserProfile


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada que permite:
    - Leitura para todos os usuários autenticados
    - Escrita apenas para usuários administradores
    """
    
    def has_permission(self, request, view):
        # Permitir leitura para usuários autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Para operações de escrita, verificar se é admin
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                return profile.is_admin
            except UserProfile.DoesNotExist:
                return False
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Permitir leitura para usuários autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Para operações de escrita, verificar se é admin
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                return profile.is_admin
            except UserProfile.DoesNotExist:
                return False
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada que permite:
    - Leitura para todos os usuários autenticados
    - Escrita apenas para o proprietário do objeto ou admins
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Permitir leitura para usuários autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar se é o proprietário
        if hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        else:
            is_owner = obj == request.user
        
        # Verificar se é admin
        try:
            profile = request.user.profile
            is_admin = profile.is_admin
        except UserProfile.DoesNotExist:
            is_admin = False
        
        return is_owner or is_admin


class IsAdminUser(permissions.BasePermission):
    """
    Permissão que permite acesso apenas para usuários administradores
    """
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                return profile.is_admin
            except UserProfile.DoesNotExist:
                return False
        return False


class IsReaderUser(permissions.BasePermission):
    """
    Permissão que permite acesso apenas para usuários leitores
    """
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                return profile.is_reader
            except UserProfile.DoesNotExist:
                return True  # Usuários sem perfil são considerados leitores por padrão
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão que permite acesso apenas para o proprietário ou administradores
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Verificar se é o proprietário
        if hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        elif hasattr(obj, 'author'):
            is_owner = obj.author == request.user
        else:
            is_owner = obj == request.user
        
        # Verificar se é admin
        try:
            profile = request.user.profile
            is_admin = profile.is_admin
        except UserProfile.DoesNotExist:
            is_admin = False
        
        return is_owner or is_admin
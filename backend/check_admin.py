#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth.models import User
from common.models import UserProfile

# Verificar usuário admin
admin_user = User.objects.filter(username='admin').first()

print(f'Usuário admin existe: {admin_user is not None}')

if admin_user:
    print(f'ID: {admin_user.id}')
    print(f'Username: {admin_user.username}')
    print(f'É superuser: {admin_user.is_superuser}')
    print(f'É staff: {admin_user.is_staff}')
    print(f'Tem perfil: {hasattr(admin_user, "profile")}')
    
    if hasattr(admin_user, 'profile'):
        profile = admin_user.profile
        print(f'Tipo de usuário: {profile.user_type}')
        print(f'is_admin (property): {profile.is_admin}')
    else:
        print('Perfil não encontrado - criando...')
        user_type = 'admin' if admin_user.is_superuser else 'reader'
        profile = UserProfile.objects.create(user=admin_user, user_type=user_type)
        print(f'Perfil criado com tipo: {profile.user_type}')
        print(f'is_admin (property): {profile.is_admin}')
else:
    print('Usuário admin não encontrado - criando...')
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print(f'Usuário admin criado: {admin_user.username}')
    print(f'É superuser: {admin_user.is_superuser}')
    print(f'Perfil criado automaticamente: {hasattr(admin_user, "profile")}')
    if hasattr(admin_user, 'profile'):
        print(f'Tipo de usuário: {admin_user.profile.user_type}')
        print(f'is_admin (property): {admin_user.profile.is_admin}')
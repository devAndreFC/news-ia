#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth.models import User
from common.models import Category

def check_data():
    print("=== Verificação de Dados no Banco ===")
    
    # Verificar usuários
    users_count = User.objects.count()
    print(f"Usuários: {users_count}")
    
    if users_count > 0:
        print("Usuários cadastrados:")
        for user in User.objects.all()[:5]:  # Mostrar apenas os primeiros 5
            print(f"  - {user.username} (ID: {user.id}, Admin: {user.is_superuser})")
    
    # Verificar categorias
    categories_count = Category.objects.count()
    print(f"\nCategorias: {categories_count}")
    
    if categories_count > 0:
        print("Categorias cadastradas:")
        for category in Category.objects.all()[:5]:  # Mostrar apenas as primeiras 5
            print(f"  - {category.name} (ID: {category.id})")
    
    # Verificar se existe modelo News
    try:
        from common.models import News
        news_count = News.objects.count()
        print(f"\nNotícias: {news_count}")
        
        if news_count > 0:
            print("Notícias cadastradas:")
            for news in News.objects.all()[:5]:  # Mostrar apenas as primeiras 5
                print(f"  - {news.title[:50]}... (ID: {news.id})")
    except ImportError:
        print("\nModelo News não encontrado no sistema")
    except Exception as e:
        print(f"\nErro ao verificar notícias: {e}")

if __name__ == "__main__":
    check_data()
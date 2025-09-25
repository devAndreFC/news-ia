#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.text import slugify

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth.models import User
from common.models import Category, News, UserProfile

def create_categories():
    """Criar categorias de exemplo"""
    categories_data = [
        {
            'name': 'Tecnologia',
            'description': 'Notícias sobre tecnologia, inovação e ciência'
        },
        {
            'name': 'Política',
            'description': 'Notícias sobre política nacional e internacional'
        },
        {
            'name': 'Esportes',
            'description': 'Notícias sobre esportes e competições'
        },
        {
            'name': 'Economia',
            'description': 'Notícias sobre economia, mercado financeiro e negócios'
        },
        {
            'name': 'Saúde',
            'description': 'Notícias sobre saúde, medicina e bem-estar'
        },
        {
            'name': 'Entretenimento',
            'description': 'Notícias sobre cinema, música, TV e celebridades'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'slug': slugify(cat_data['name'])
            }
        )
        categories.append(category)
        if created:
            print(f"Categoria criada: {category.name}")
        else:
            print(f"Categoria já existe: {category.name}")
    
    return categories

def create_admin_user():
    """Criar usuário administrador"""
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@news.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Usuário admin criado: {admin_user.username}")
    else:
        print(f"Usuário admin já existe: {admin_user.username}")
    
    # Garantir que o perfil existe e é admin
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'user_type': 'admin'}
    )
    if not profile.is_admin:
        profile.user_type = 'admin'
        profile.save()
    
    return admin_user

def create_sample_news(categories, admin_user):
    """Criar notícias de exemplo"""
    news_data = [
        {
            'title': 'Nova Tecnologia de IA Revoluciona o Mercado',
            'summary': 'Empresa brasileira desenvolve inteligência artificial que promete transformar diversos setores.',
            'content': 'Uma startup brasileira anunciou hoje o desenvolvimento de uma nova tecnologia de inteligência artificial que promete revolucionar diversos setores da economia. A tecnologia, que utiliza algoritmos avançados de machine learning, já está sendo testada por grandes empresas do país.',
            'source': 'TechNews Brasil',
            'category': 'Tecnologia'
        },
        {
            'title': 'Eleições 2024: Pesquisa Mostra Cenário Acirrado',
            'summary': 'Nova pesquisa eleitoral revela empate técnico entre principais candidatos.',
            'content': 'A mais recente pesquisa eleitoral divulgada hoje mostra um cenário de empate técnico entre os principais candidatos às eleições de 2024. Os números indicam uma disputa acirrada que deve se estender até o segundo turno.',
            'source': 'Política Hoje',
            'category': 'Política'
        },
        {
            'title': 'Brasil Conquista Ouro no Mundial de Futebol',
            'summary': 'Seleção brasileira vence final por 2x1 e conquista o título mundial.',
            'content': 'A seleção brasileira de futebol conquistou hoje o título mundial após vencer a final por 2x1. O jogo foi disputado e emocionante, com gols nos últimos minutos da partida. Esta é a sexta conquista do Brasil na competição.',
            'source': 'Esporte Total',
            'category': 'Esportes'
        },
        {
            'title': 'Bolsa de Valores Atinge Novo Recorde Histórico',
            'summary': 'Ibovespa fecha em alta de 3,2% e bate novo recorde de pontuação.',
            'content': 'A bolsa de valores brasileira fechou hoje com alta de 3,2%, atingindo um novo recorde histórico de pontuação. O movimento foi impulsionado por bons resultados de empresas do setor tecnológico e expectativas positivas para a economia.',
            'source': 'Mercado Financeiro',
            'category': 'Economia'
        },
        {
            'title': 'Descoberta Revolucionária no Tratamento do Câncer',
            'summary': 'Pesquisadores brasileiros desenvolvem nova terapia que aumenta taxa de cura.',
            'content': 'Pesquisadores da Universidade de São Paulo anunciaram uma descoberta revolucionária no tratamento do câncer. A nova terapia, que combina imunoterapia com nanotecnologia, mostrou resultados promissores em testes clínicos, aumentando significativamente as taxas de cura.',
            'source': 'Saúde em Foco',
            'category': 'Saúde'
        },
        {
            'title': 'Festival de Cinema de Cannes Anuncia Vencedores',
            'summary': 'Filme brasileiro concorre à Palma de Ouro no prestigioso festival.',
            'content': 'O Festival de Cinema de Cannes anunciou hoje os vencedores de suas principais categorias. Um filme brasileiro está concorrendo à prestigiosa Palma de Ouro, marcando um momento histórico para o cinema nacional no cenário internacional.',
            'source': 'Cinema & Arte',
            'category': 'Entretenimento'
        }
    ]
    
    # Criar um dicionário de categorias por nome
    category_dict = {cat.name: cat for cat in categories}
    
    for i, news_item in enumerate(news_data):
        # Calcular data de publicação (últimos 7 dias)
        published_date = timezone.now() - timedelta(days=i)
        
        category = category_dict.get(news_item['category'])
        if not category:
            continue
        
        news, created = News.objects.get_or_create(
            title=news_item['title'],
            defaults={
                'summary': news_item['summary'],
                'content': news_item['content'],
                'source': news_item['source'],
                'category': category,
                'author': admin_user,
                'published_at': published_date,
                'is_active': True
            }
        )
        
        if created:
            print(f"Notícia criada: {news.title}")
        else:
            print(f"Notícia já existe: {news.title}")

def main():
    """Função principal"""
    print("Iniciando população do banco de dados...")
    
    # Criar categorias
    print("\n1. Criando categorias...")
    categories = create_categories()
    
    # Criar usuário admin
    print("\n2. Criando usuário administrador...")
    admin_user = create_admin_user()
    
    # Criar notícias de exemplo
    print("\n3. Criando notícias de exemplo...")
    create_sample_news(categories, admin_user)
    
    print("\n✅ Banco de dados populado com sucesso!")
    print(f"Total de categorias: {Category.objects.count()}")
    print(f"Total de notícias: {News.objects.count()}")
    print(f"Total de usuários: {User.objects.count()}")
    
    print("\n📝 Credenciais do administrador:")
    print("Usuário: admin")
    print("Senha: admin123")

if __name__ == '__main__':
    main()
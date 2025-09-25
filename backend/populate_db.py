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
        },
        {
            'title': 'Startup Brasileira Desenvolve App de Sustentabilidade',
            'summary': 'Aplicativo conecta consumidores a produtos ecológicos e sustentáveis.',
            'content': 'Uma startup de São Paulo lançou um aplicativo inovador que conecta consumidores conscientes a produtos sustentáveis. A plataforma já conta com mais de 500 empresas parceiras e promete revolucionar o consumo responsável no Brasil.',
            'source': 'EcoTech',
            'category': 'Tecnologia'
        },
        {
            'title': 'Reforma Tributária Aprovada no Congresso',
            'summary': 'Nova legislação simplifica sistema tributário brasileiro.',
            'content': 'O Congresso Nacional aprovou hoje a reforma tributária que promete simplificar o complexo sistema de impostos brasileiro. A medida deve entrar em vigor gradualmente nos próximos cinco anos, beneficiando empresas e consumidores.',
            'source': 'Política Nacional',
            'category': 'Política'
        },
        {
            'title': 'Olimpíadas de Paris: Brasil Garante 15 Medalhas',
            'summary': 'Delegação brasileira tem melhor desempenho dos últimos 20 anos.',
            'content': 'A delegação brasileira nas Olimpíadas de Paris conquistou 15 medalhas, sendo 5 de ouro, 4 de prata e 6 de bronze. Este é o melhor desempenho do país nos últimos 20 anos, superando as expectativas iniciais.',
            'source': 'Olimpíadas Brasil',
            'category': 'Esportes'
        },
        {
            'title': 'PIB Brasileiro Cresce 2,8% no Terceiro Trimestre',
            'summary': 'Economia mostra sinais de recuperação após período de instabilidade.',
            'content': 'O Produto Interno Bruto brasileiro registrou crescimento de 2,8% no terceiro trimestre, superando as expectativas dos analistas. O resultado é impulsionado pelo setor de serviços e pela retomada do consumo das famílias.',
            'source': 'Economia Brasil',
            'category': 'Economia'
        },
        {
            'title': 'Vacina Nacional Contra Dengue Aprovada pela Anvisa',
            'summary': 'Imunizante desenvolvido no Brasil mostra 95% de eficácia.',
            'content': 'A Anvisa aprovou hoje a primeira vacina contra dengue desenvolvida integralmente no Brasil. Os testes clínicos mostraram eficácia de 95% na prevenção da doença, representando um marco para a saúde pública nacional.',
            'source': 'Saúde Pública',
            'category': 'Saúde'
        },
        {
            'title': 'Série Brasileira Conquista Emmy Internacional',
            'summary': 'Produção nacional é reconhecida mundialmente pela qualidade.',
            'content': 'A série brasileira "Cidade Perdida" conquistou o Emmy Internacional na categoria Melhor Drama. Esta é a primeira vez que uma produção nacional recebe este prestigioso prêmio, colocando o Brasil no mapa da televisão mundial.',
            'source': 'TV & Cinema',
            'category': 'Entretenimento'
        },
        {
            'title': 'Robô Brasileiro Vence Competição Mundial de Robótica',
            'summary': 'Equipe de estudantes brasileiros supera 50 países na competição.',
            'content': 'Uma equipe de estudantes brasileiros venceu a competição mundial de robótica, superando equipes de mais de 50 países. O robô desenvolvido pelos jovens demonstrou inovação e precisão técnica excepcionais.',
            'source': 'Robótica News',
            'category': 'Tecnologia'
        },
        {
            'title': 'Ministro Anuncia Novo Programa de Habitação Popular',
            'summary': 'Governo promete construir 1 milhão de casas em 4 anos.',
            'content': 'O Ministro das Cidades anunciou hoje o lançamento de um novo programa habitacional que promete construir 1 milhão de casas populares nos próximos quatro anos. O investimento total será de R$ 200 bilhões.',
            'source': 'Governo Federal',
            'category': 'Política'
        },
        {
            'title': 'Flamengo Contrata Técnico Europeu Renomado',
            'summary': 'Clube carioca investe pesado para temporada 2025.',
            'content': 'O Flamengo anunciou a contratação do técnico português José Mourinho para comandar a equipe na temporada 2025. O investimento de R$ 50 milhões por ano marca a maior contratação da história do futebol brasileiro.',
            'source': 'Futebol Total',
            'category': 'Esportes'
        },
        {
            'title': 'Banco Central Reduz Taxa Selic para 8,5%',
            'summary': 'Decisão visa estimular crescimento econômico do país.',
            'content': 'O Comitê de Política Monetária do Banco Central decidiu reduzir a taxa Selic de 9,25% para 8,5%. A medida visa estimular o crescimento econômico e facilitar o acesso ao crédito para empresas e consumidores.',
            'source': 'BC Comunica',
            'category': 'Economia'
        },
        {
            'title': 'Hospital Brasileiro Realiza Primeiro Transplante de Face',
            'summary': 'Cirurgia pioneira marca avanço da medicina nacional.',
            'content': 'O Hospital das Clínicas de São Paulo realizou com sucesso o primeiro transplante de face do Brasil. A cirurgia durou 18 horas e envolveu uma equipe de 30 profissionais, marcando um avanço histórico da medicina nacional.',
            'source': 'Medicina Avançada',
            'category': 'Saúde'
        },
        {
            'title': 'Netflix Anuncia Produção de 20 Filmes Brasileiros',
            'summary': 'Plataforma investe R$ 500 milhões no cinema nacional.',
            'content': 'A Netflix anunciou um investimento de R$ 500 milhões para produzir 20 filmes brasileiros nos próximos dois anos. A iniciativa visa fortalecer o cinema nacional e levar produções brasileiras para o mundo.',
            'source': 'Streaming News',
            'category': 'Entretenimento'
        },
        {
            'title': 'Brasil Desenvolve Primeiro Satélite 100% Nacional',
            'summary': 'Tecnologia espacial brasileira atinge novo patamar.',
            'content': 'O Instituto Nacional de Pesquisas Espaciais anunciou o desenvolvimento do primeiro satélite 100% brasileiro. O equipamento será lançado no próximo ano e marcará a independência tecnológica do país no setor espacial.',
            'source': 'Espaço Brasil',
            'category': 'Tecnologia'
        },
        {
            'title': 'Supremo Tribunal Julga Marco Temporal das Terras Indígenas',
            'summary': 'Decisão histórica define futuro dos territórios indígenas.',
            'content': 'O Supremo Tribunal Federal iniciou hoje o julgamento do marco temporal das terras indígenas. A decisão será fundamental para definir os critérios de demarcação de territórios indígenas no Brasil.',
            'source': 'Justiça Hoje',
            'category': 'Política'
        },
        {
            'title': 'Seleção Feminina de Vôlei Conquista Mundial',
            'summary': 'Brasil vence final contra Estados Unidos por 3 sets a 1.',
            'content': 'A seleção brasileira feminina de vôlei conquistou o título mundial após vencer os Estados Unidos por 3 sets a 1 na final. Esta é a terceira conquista mundial da equipe, consolidando o Brasil como potência no esporte.',
            'source': 'Vôlei Brasil',
            'category': 'Esportes'
        },
        {
            'title': 'Inflação Brasileira Fica Abaixo da Meta pelo Terceiro Mês',
            'summary': 'IPCA acumula 3,2% em 12 meses, dentro do centro da meta.',
            'content': 'O Índice de Preços ao Consumidor Amplo ficou em 0,15% em novembro, acumulando 3,2% em 12 meses. Este é o terceiro mês consecutivo que a inflação fica abaixo do centro da meta de 3% estabelecida pelo governo.',
            'source': 'IBGE Informa',
            'category': 'Economia'
        },
        {
            'title': 'Pesquisadores Brasileiros Descobrem Cura para Doença Rara',
            'summary': 'Tratamento inovador oferece esperança para milhares de pacientes.',
            'content': 'Pesquisadores da UFRJ descobriram um tratamento eficaz para a síndrome de Machado-Joseph, doença rara que afeta o sistema nervoso. O tratamento já está sendo testado em pacientes e mostra resultados promissores.',
            'source': 'Pesquisa Médica',
            'category': 'Saúde'
        },
        {
            'title': 'Rock in Rio 2025 Anuncia Line-up com Artistas Nacionais',
            'summary': 'Festival valoriza música brasileira com 60% do line-up nacional.',
            'content': 'O Rock in Rio 2025 anunciou seu line-up com 60% de artistas brasileiros, valorizando a música nacional. O festival acontecerá em setembro e promete ser o maior evento musical do ano no país.',
            'source': 'Rock in Rio',
            'category': 'Entretenimento'
        },
        {
            'title': 'Inteligência Artificial Brasileira Detecta Fraudes Bancárias',
            'summary': 'Sistema nacional reduz fraudes em 85% nos bancos parceiros.',
            'content': 'Uma empresa brasileira desenvolveu um sistema de inteligência artificial que detecta fraudes bancárias com 99% de precisão. A tecnologia já reduziu as fraudes em 85% nos bancos que adotaram o sistema.',
            'source': 'FinTech Brasil',
            'category': 'Tecnologia'
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
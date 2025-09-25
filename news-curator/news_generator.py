"""
News Generator for creating fictitious news articles
"""
import random
from datetime import datetime, timedelta
from faker import Faker
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class NewsGenerator:
    """Generates fictitious news articles based on templates and categories"""
    
    def __init__(self):
        self.faker = Faker('pt_BR')  # Brazilian Portuguese
        self.news_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict]]:
        """Load news templates for different categories"""
        return {
            'Tecnologia': [
                {
                    'title_template': 'Nova tecnologia de {tech} promete revolucionar {area}',
                    'content_template': 'Pesquisadores desenvolveram uma nova tecnologia de {tech} que pode transformar completamente o setor de {area}. A inovação promete {benefit} e deve estar disponível em {timeframe}.',
                    'variables': {
                        'tech': ['inteligência artificial', 'blockchain', 'computação quântica', 'realidade virtual', 'IoT'],
                        'area': ['saúde', 'educação', 'transporte', 'comunicação', 'energia'],
                        'benefit': ['reduzir custos em 50%', 'aumentar a eficiência', 'melhorar a segurança', 'facilitar o acesso'],
                        'timeframe': ['2025', 'os próximos 2 anos', 'breve']
                    }
                },
                {
                    'title_template': 'Startup brasileira desenvolve {product} inovador',
                    'content_template': 'Uma startup sediada em {city} lançou um {product} que utiliza {technology}. O produto já atraiu investimentos de R$ {investment} milhões e planeja expandir para {market}.',
                    'variables': {
                        'product': ['aplicativo', 'plataforma', 'sistema', 'dispositivo'],
                        'city': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Florianópolis', 'Recife'],
                        'technology': ['machine learning', 'big data', 'cloud computing', 'APIs avançadas'],
                        'investment': ['5', '10', '15', '25', '50'],
                        'market': ['América Latina', 'mercado internacional', 'outros estados brasileiros']
                    }
                }
            ],
            'Economia': [
                {
                    'title_template': '{indicator} {direction} {percentage}% no último {period}',
                    'content_template': 'Segundo dados divulgados hoje, o {indicator} apresentou {direction_desc} de {percentage}% no último {period}. Especialistas atribuem o resultado a {reason} e projetam {forecast} para os próximos meses.',
                    'variables': {
                        'indicator': ['PIB', 'IPCA', 'taxa de desemprego', 'índice de confiança do consumidor'],
                        'direction': ['sobe', 'cai', 'cresce'],
                        'direction_desc': ['alta', 'queda', 'crescimento'],
                        'percentage': ['0.5', '1.2', '2.1', '3.5', '4.8'],
                        'period': ['trimestre', 'mês', 'semestre'],
                        'reason': ['políticas econômicas', 'cenário internacional', 'fatores sazonais'],
                        'forecast': ['estabilidade', 'melhora gradual', 'volatilidade']
                    }
                }
            ],
            'Política': [
                {
                    'title_template': 'Congresso aprova projeto sobre {topic}',
                    'content_template': 'O Congresso Nacional aprovou hoje o projeto de lei que trata de {topic}. A medida foi aprovada com {votes} votos favoráveis e agora segue para {next_step}. A proposta visa {objective}.',
                    'variables': {
                        'topic': ['educação digital', 'sustentabilidade', 'inovação tecnológica', 'saúde pública'],
                        'votes': ['250', '300', '350', '400'],
                        'next_step': ['sanção presidencial', 'análise do Senado', 'regulamentação'],
                        'objective': ['modernizar o setor', 'aumentar a transparência', 'melhorar os serviços públicos']
                    }
                }
            ],
            'Esportes': [
                {
                    'title_template': '{team} vence {opponent} por {score} em {competition}',
                    'content_template': 'Em partida disputada no {stadium}, o {team} derrotou o {opponent} pelo placar de {score}. O destaque da partida foi {player}, que {action}. Com o resultado, o time {position}.',
                    'variables': {
                        'team': ['Flamengo', 'Corinthians', 'Palmeiras', 'São Paulo', 'Santos'],
                        'opponent': ['Botafogo', 'Vasco', 'Fluminense', 'Grêmio', 'Internacional'],
                        'score': ['2-1', '3-0', '1-0', '2-2', '3-2'],
                        'competition': ['Brasileirão', 'Copa do Brasil', 'Libertadores'],
                        'stadium': ['Maracanã', 'Arena Corinthians', 'Allianz Parque'],
                        'player': ['atacante', 'meio-campista', 'zagueiro', 'goleiro'],
                        'action': ['marcou dois gols', 'fez assistência decisiva', 'defendeu pênalti'],
                        'position': ['assume a liderança', 'sobe na tabela', 'mantém a posição']
                    }
                }
            ],
            'Saúde': [
                {
                    'title_template': 'Pesquisa revela {discovery} sobre {condition}',
                    'content_template': 'Estudo realizado por {institution} descobriu {discovery} relacionado a {condition}. A pesquisa, que durou {duration}, analisou {sample} e pode levar ao desenvolvimento de {treatment}.',
                    'variables': {
                        'discovery': ['novo tratamento', 'fator de risco', 'método de prevenção'],
                        'condition': ['diabetes', 'hipertensão', 'câncer', 'Alzheimer', 'depressão'],
                        'institution': ['USP', 'Fiocruz', 'Hospital Albert Einstein', 'UNIFESP'],
                        'duration': ['2 anos', '18 meses', '3 anos'],
                        'sample': ['1000 pacientes', '500 voluntários', '2000 participantes'],
                        'treatment': ['novos medicamentos', 'terapias inovadoras', 'protocolos de prevenção']
                    }
                }
            ]
        }
    
    def generate_news(self, category: str, category_id: int, author_id: int = 1) -> Dict:
        """Generate a single news article for the given category"""
        if category not in self.news_templates:
            # Fallback for categories without templates
            return self._generate_generic_news(category, category_id, author_id)
        
        template = random.choice(self.news_templates[category])
        
        # Fill template variables
        filled_vars = {}
        for var_name, options in template['variables'].items():
            filled_vars[var_name] = random.choice(options)
        
        # Generate title and content
        title = template['title_template'].format(**filled_vars)
        content = template['content_template'].format(**filled_vars)
        
        # Generate summary (first 150 characters of content)
        summary = content[:150] + "..." if len(content) > 150 else content
        
        # Generate publication date (within last 24 hours)
        published_at = self.faker.date_time_between(
            start_date='-1d',
            end_date='now'
        )
        
        return {
            'title': title,
            'content': content,
            'summary': summary,
            'source': f'Agente Curador - {category}',
            'published_at': published_at,
            'category_id': category_id,
            'author_id': author_id
        }
    
    def _generate_generic_news(self, category: str, category_id: int, author_id: int) -> Dict:
        """Generate generic news for categories without specific templates"""
        title = f"{self.faker.catch_phrase()} em {category}"
        content = f"{self.faker.text(max_nb_chars=500)} Esta notícia foi gerada automaticamente pelo sistema de curadoria."
        summary = content[:150] + "..." if len(content) > 150 else content
        
        published_at = self.faker.date_time_between(
            start_date='-1d',
            end_date='now'
        )
        
        return {
            'title': title,
            'content': content,
            'summary': summary,
            'source': f'Agente Curador - {category}',
            'published_at': published_at,
            'category_id': category_id,
            'author_id': author_id
        }
    
    def generate_batch(self, categories: List[Dict], news_per_category: int = 1, author_id: int = 1) -> List[Dict]:
        """Generate a batch of news articles across different categories"""
        news_batch = []
        
        for category_data in categories:
            category_name = category_data['name']
            category_id = category_data['id']
            
            for _ in range(news_per_category):
                try:
                    news = self.generate_news(category_name, category_id, author_id)
                    news_batch.append(news)
                    logger.info(f"Generated news for category {category_name}: {news['title']}")
                except Exception as e:
                    logger.error(f"Failed to generate news for category {category_name}: {e}")
        
        return news_batch
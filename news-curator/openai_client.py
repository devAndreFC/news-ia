"""
OpenAI Client for News Generation
"""
from openai import OpenAI
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from config import OPENAI_CONFIG

logger = logging.getLogger(__name__)

class OpenAINewsGenerator:
    """OpenAI-powered news generator"""
    
    def __init__(self):
        if not OPENAI_CONFIG['api_key'] or OPENAI_CONFIG['api_key'] == 'your_openai_api_key_here':
            logger.warning("OPENAI_API_KEY não configurada. Usando gerador mock.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=OPENAI_CONFIG['api_key'])
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente OpenAI: {e}")
                self.client = None
        
        self.model = OPENAI_CONFIG['model']
        self.max_tokens = OPENAI_CONFIG['max_tokens']
        self.temperature = OPENAI_CONFIG['temperature']
    
    def generate_news_article(self, category: str, category_id: int, author_id: int = 1) -> Optional[Dict]:
        """Generate a single news article using OpenAI or mock data"""
        try:
            if self.client is None:
                # Generate mock news when OpenAI is not available
                return self._generate_mock_news(category, category_id, author_id)
            
            prompt = self._create_prompt(category)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um jornalista especializado em criar notícias realistas e envolventes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            
            try:
                # Try to parse as JSON first
                news_data = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, extract from text
                lines = content.strip().split('\n')
                title = lines[0] if lines else f"Notícia sobre {category}"
                content_text = '\n'.join(lines[1:]) if len(lines) > 1 else content
                news_data = {
                    'title': title.strip(),
                    'content': content_text.strip(),
                    'summary': content_text.strip()[:150]
                }
            
            return self._format_news_response(news_data, category, category_id, author_id)
            
        except Exception as e:
            logger.error(f"Erro ao gerar notícia com OpenAI para categoria {category}: {e}")
            return self._generate_mock_news(category, category_id, author_id)
    
    def _create_prompt(self, category: str) -> str:
        """Create a prompt for news generation based on category"""
        prompts = {
            'Tecnologia': """
            Gere uma notícia fictícia sobre tecnologia no Brasil. A notícia deve ser realista e atual.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: IA, startups, inovação, aplicativos, cibersegurança, 5G, blockchain.
            """,
            
            'Economia': """
            Gere uma notícia fictícia sobre economia brasileira. A notícia deve ser realista e atual.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: PIB, inflação, mercado de trabalho, investimentos, bolsa de valores, moeda.
            """,
            
            'Política': """
            Gere uma notícia fictícia sobre política brasileira. A notícia deve ser realista e imparcial.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: projetos de lei, políticas públicas, eleições, governo federal, congresso.
            """,
            
            'Esportes': """
            Gere uma notícia fictícia sobre esportes no Brasil. A notícia deve ser realista e atual.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: futebol brasileiro, olimpíadas, campeonatos, atletas brasileiros, modalidades.
            """,
            
            'Saúde': """
            Gere uma notícia fictícia sobre saúde no Brasil. A notícia deve ser realista e informativa.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: pesquisas médicas, SUS, campanhas de vacinação, descobertas científicas, saúde pública.
            """,
            
            'Educação': """
            Gere uma notícia fictícia sobre educação no Brasil. A notícia deve ser realista e atual.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: ensino superior, educação básica, tecnologia na educação, ENEM, políticas educacionais.
            """,
            
            'Entretenimento': """
            Gere uma notícia fictícia sobre entretenimento no Brasil. A notícia deve ser realista e atual.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: cinema brasileiro, música, televisão, streaming, festivais, cultura.
            """,
            
            'Ciência': """
            Gere uma notícia fictícia sobre ciência no Brasil. A notícia deve ser realista e informativa.
            Retorne um JSON com os seguintes campos:
            {
                "title": "título da notícia (máximo 100 caracteres)",
                "content": "conteúdo completo da notícia (300-500 palavras)",
                "summary": "resumo da notícia (máximo 150 caracteres)"
            }
            
            Temas sugeridos: pesquisas brasileiras, descobertas científicas, meio ambiente, astronomia, biotecnologia.
            """
        }
        
        return prompts.get(category, prompts['Tecnologia'])
    
    def _generate_mock_news(self, category: str, category_id: int, author_id: int) -> Dict:
        """Generate mock news when OpenAI is not available"""
        mock_news = {
            'Tecnologia': {
                'title': 'Nova startup brasileira desenvolve IA para agricultura',
                'content': 'Uma startup brasileira acaba de lançar uma solução inovadora de inteligência artificial voltada para o agronegócio. A tecnologia promete revolucionar a forma como os produtores rurais monitoram suas plantações, oferecendo análises preditivas sobre clima, pragas e produtividade. A empresa já recebeu investimentos significativos e planeja expandir para outros países da América Latina.',
                'summary': 'Startup brasileira lança IA para agricultura com análises preditivas.'
            },
            'Economia': {
                'title': 'PIB brasileiro cresce acima das expectativas no trimestre',
                'content': 'O Produto Interno Bruto (PIB) do Brasil registrou crescimento superior às projeções dos analistas no último trimestre. O resultado foi impulsionado pelo setor de serviços e pelo aumento do consumo das famílias. Especialistas apontam que a recuperação econômica está se consolidando, mas alertam para os desafios inflacionários que ainda persistem.',
                'summary': 'PIB brasileiro supera expectativas com crescimento do setor de serviços.'
            },
            'Política': {
                'title': 'Congresso aprova nova lei de incentivo à inovação tecnológica',
                'content': 'O Congresso Nacional aprovou por unanimidade uma nova legislação que estabelece incentivos fiscais para empresas que investem em pesquisa e desenvolvimento tecnológico. A medida visa fortalecer o ecossistema de inovação brasileiro e atrair mais investimentos para o setor. A lei entra em vigor no próximo ano.',
                'summary': 'Nova lei oferece incentivos fiscais para P&D tecnológico.'
            },
            'Esportes': {
                'title': 'Atleta brasileiro conquista medalha em campeonato mundial',
                'content': 'O Brasil conquistou mais uma medalha em competição internacional, desta vez no atletismo. O atleta brasileiro superou adversários de diversos países e garantiu o pódio em prova disputada. O resultado representa um marco importante para o esporte nacional e aumenta as expectativas para as próximas competições internacionais.',
                'summary': 'Atleta brasileiro conquista medalha no atletismo mundial.'
            },
            'Saúde': {
                'title': 'Pesquisadores brasileiros desenvolvem novo tratamento inovador',
                'content': 'Uma equipe de pesquisadores de universidades brasileiras desenvolveu um tratamento inovador que promete melhorar significativamente a qualidade de vida dos pacientes. O estudo, publicado em revista científica internacional, demonstrou resultados promissores em testes clínicos. A descoberta pode revolucionar o tratamento da condição estudada.',
                'summary': 'Pesquisadores brasileiros criam tratamento inovador com resultados promissores.'
            },
            'Educação': {
                'title': 'Universidade brasileira lança programa de ensino digital',
                'content': 'Uma das principais universidades do país anunciou o lançamento de um programa pioneiro de ensino digital. A iniciativa combina tecnologias avançadas com metodologias pedagógicas inovadoras para oferecer uma experiência educacional diferenciada. O programa já recebeu reconhecimento internacional e serve como modelo para outras instituições.',
                'summary': 'Universidade lança programa pioneiro de ensino digital.'
            },
            'Entretenimento': {
                'title': 'Filme brasileiro ganha destaque em festival internacional',
                'content': 'Uma produção cinematográfica brasileira conquistou reconhecimento em prestigioso festival internacional de cinema. O filme, dirigido por cineasta nacional, aborda temas contemporâneos da sociedade brasileira e foi elogiado pela crítica especializada. O sucesso internacional abre novas oportunidades para o cinema nacional.',
                'summary': 'Filme brasileiro recebe reconhecimento em festival internacional.'
            },
            'Ciência': {
                'title': 'Descoberta científica brasileira é publicada em revista internacional',
                'content': 'Cientistas brasileiros fizeram uma descoberta importante que foi publicada em uma das principais revistas científicas do mundo. A pesquisa, conduzida em parceria com instituições nacionais e internacionais, pode ter impactos significativos em diversas áreas do conhecimento. O trabalho representa um marco para a ciência brasileira.',
                'summary': 'Cientistas brasileiros fazem descoberta publicada internacionalmente.'
            }
        }
        
        news_data = mock_news.get(category, mock_news['Tecnologia'])
        return self._format_news_response(news_data, category, category_id, author_id)
    
    def _format_news_response(self, news_data: Dict, category: str, category_id: int, author_id: int) -> Dict:
        """Format the OpenAI response into the expected database format"""
        return {
            'title': news_data.get('title', 'Título não disponível')[:100],
            'content': news_data.get('content', 'Conteúdo não disponível'),
            'summary': news_data.get('summary', 'Resumo não disponível')[:150],
            'source': f'Agente Curador GPT - {category}',
            'published_at': datetime.now(),
            'category_id': category_id,
            'author_id': author_id,
            'is_active': True
        }
    
    def generate_batch(self, categories: List[Dict], news_per_category: int = 1, author_id: int = 1) -> List[Dict]:
        """Generate a batch of news articles using OpenAI"""
        news_batch = []
        
        for category_data in categories:
            category_name = category_data['name']
            category_id = category_data['id']
            
            for _ in range(news_per_category):
                try:
                    news = self.generate_news_article(category_name, category_id, author_id)
                    if news:
                        news_batch.append(news)
                        logger.info(f"Notícia gerada com OpenAI para categoria {category_name}: {news['title']}")
                    else:
                        logger.warning(f"Falha ao gerar notícia para categoria {category_name}")
                except Exception as e:
                    logger.error(f"Erro ao gerar notícia para categoria {category_name}: {e}")
        
        return news_batch
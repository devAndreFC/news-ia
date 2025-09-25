"""
OpenAI Client for News Generation
"""
import openai
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from config import OPENAI_CONFIG

logger = logging.getLogger(__name__)

class OpenAINewsGenerator:
    """OpenAI-powered news generator"""
    
    def __init__(self):
        if not OPENAI_CONFIG['api_key']:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        openai.api_key = OPENAI_CONFIG['api_key']
        self.model = OPENAI_CONFIG['model']
        self.max_tokens = OPENAI_CONFIG['max_tokens']
        self.temperature = OPENAI_CONFIG['temperature']
    
    def generate_news_article(self, category: str, category_id: int, author_id: int = 1) -> Optional[Dict]:
        """Generate a single news article using OpenAI"""
        try:
            prompt = self._create_prompt(category)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um jornalista experiente que escreve notícias fictícias realistas em português brasileiro. Sempre retorne um JSON válido com os campos solicitados."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            news_data = json.loads(content)
            
            # Validate and format the response
            return self._format_news_response(news_data, category, category_id, author_id)
            
        except Exception as e:
            logger.error(f"Erro ao gerar notícia com OpenAI para categoria {category}: {e}")
            return None
    
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
    
    def _format_news_response(self, news_data: Dict, category: str, category_id: int, author_id: int) -> Dict:
        """Format the OpenAI response into the expected database format"""
        return {
            'title': news_data.get('title', 'Título não disponível')[:100],
            'content': news_data.get('content', 'Conteúdo não disponível'),
            'summary': news_data.get('summary', 'Resumo não disponível')[:150],
            'source': f'Agente Curador GPT - {category}',
            'published_at': datetime.now(),
            'category_id': category_id,
            'author_id': author_id
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
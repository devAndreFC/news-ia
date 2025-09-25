"""
Serviço de Análise de Sentimentos e Identificação de Entidades
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analisador de sentimentos para notícias"""
    
    def __init__(self):
        # Palavras-chave para análise de sentimento em português
        self.positive_words = {
            'excelente', 'ótimo', 'bom', 'positivo', 'sucesso', 'vitória', 'conquista',
            'melhoria', 'progresso', 'avanço', 'crescimento', 'desenvolvimento', 'inovação',
            'benefício', 'vantagem', 'oportunidade', 'esperança', 'otimismo', 'alegria',
            'felicidade', 'satisfação', 'aprovação', 'elogio', 'reconhecimento', 'prêmio',
            'ganho', 'lucro', 'aumento', 'alta', 'subida', 'recuperação', 'melhora',
            'solução', 'resolução', 'acordo', 'paz', 'harmonia', 'união', 'cooperação'
        }
        
        self.negative_words = {
            'ruim', 'péssimo', 'terrível', 'negativo', 'fracasso', 'derrota', 'perda',
            'declínio', 'queda', 'redução', 'diminuição', 'crise', 'problema', 'dificuldade',
            'obstáculo', 'barreira', 'conflito', 'guerra', 'violência', 'crime', 'roubo',
            'corrupção', 'escândalo', 'polêmica', 'controversia', 'crítica', 'condenação',
            'prejuízo', 'dano', 'destruição', 'catástrofe', 'desastre', 'tragédia',
            'morte', 'doença', 'epidemia', 'pandemia', 'recessão', 'desemprego', 'inflação'
        }
        
        self.neutral_words = {
            'informação', 'dados', 'estatística', 'relatório', 'estudo', 'pesquisa',
            'análise', 'investigação', 'levantamento', 'censo', 'enquete', 'entrevista',
            'declaração', 'comunicado', 'anúncio', 'divulgação', 'publicação', 'lançamento'
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analisa o sentimento de um texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Dict com score, label e confiança
        """
        try:
            # Normalizar texto
            normalized_text = self._normalize_text(text)
            words = normalized_text.split()
            
            # Contar palavras por categoria
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            neutral_count = sum(1 for word in words if word in self.neutral_words)
            
            total_sentiment_words = positive_count + negative_count + neutral_count
            
            # Calcular score (-1 a 1)
            if total_sentiment_words == 0:
                score = 0.0
                label = 'neutro'
                confidence = 0.5
            else:
                score = (positive_count - negative_count) / len(words)
                
                # Determinar label
                if score > 0.02:
                    label = 'positivo'
                elif score < -0.02:
                    label = 'negativo'
                else:
                    label = 'neutro'
                
                # Calcular confiança baseada na densidade de palavras de sentimento
                confidence = min(total_sentiment_words / len(words) * 2, 1.0)
            
            return {
                'score': round(score, 3),
                'label': label,
                'confidence': round(confidence, 3),
                'word_counts': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count,
                    'total_words': len(words)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {
                'score': 0.0,
                'label': 'neutro',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para análise"""
        # Converter para minúsculas
        text = text.lower()
        
        # Remover pontuação e caracteres especiais
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text


class EntityExtractor:
    """Extrator de entidades nomeadas"""
    
    def __init__(self):
        # Padrões regex para diferentes tipos de entidades
        self.patterns = {
            'pessoa': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',  # Nome Sobrenome
                r'\b(?:Sr\.|Sra\.|Dr\.|Dra\.)\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',  # Títulos
            ],
            'organizacao': [
                r'\b[A-Z][A-Za-z]*(?:\s[A-Z][A-Za-z]*)*\s(?:S\.A\.|Ltda\.|Inc\.|Corp\.|Ltd\.)\b',
                r'\b(?:Ministério|Secretaria|Prefeitura|Governo|Empresa|Companhia)\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',
                r'\b[A-Z]{2,}\b',  # Siglas
            ],
            'local': [
                r'\b(?:São Paulo|Rio de Janeiro|Brasília|Salvador|Fortaleza|Belo Horizonte|Manaus|Curitiba|Recife|Porto Alegre)\b',
                r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s-\s[A-Z]{2})?\b',  # Cidade - Estado
            ],
            'data': [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # DD/MM/YYYY
                r'\b\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}\b',
            ],
            'valor_monetario': [
                r'R\$\s*\d+(?:\.\d{3})*(?:,\d{2})?\b',
                r'\b\d+(?:\.\d{3})*(?:,\d{2})?\s*(?:reais|milhões|bilhões)\b',
            ],
            'porcentagem': [
                r'\b\d+(?:,\d+)?%\b',
            ]
        }
        
        # Palavras-chave para contexto
        self.context_keywords = {
            'economia': ['economia', 'mercado', 'bolsa', 'investimento', 'pib', 'inflação', 'juros'],
            'politica': ['governo', 'presidente', 'ministro', 'deputado', 'senador', 'eleição', 'votação'],
            'tecnologia': ['tecnologia', 'internet', 'software', 'aplicativo', 'digital', 'inovação'],
            'saude': ['saúde', 'hospital', 'médico', 'doença', 'tratamento', 'vacina', 'medicina'],
            'esportes': ['futebol', 'basquete', 'vôlei', 'olimpíadas', 'copa', 'campeonato', 'atleta'],
            'educacao': ['educação', 'escola', 'universidade', 'professor', 'aluno', 'ensino', 'curso']
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrai entidades nomeadas do texto
        
        Args:
            text: Texto para extração
            
        Returns:
            Dict com entidades por categoria
        """
        try:
            entities = {}
            
            for entity_type, patterns in self.patterns.items():
                found_entities = set()
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    found_entities.update(matches)
                
                # Filtrar e limpar entidades
                cleaned_entities = []
                for entity in found_entities:
                    entity = entity.strip()
                    if len(entity) > 2 and entity not in cleaned_entities:
                        cleaned_entities.append(entity)
                
                entities[entity_type] = cleaned_entities[:10]  # Limitar a 10 por tipo
            
            return entities
            
        except Exception as e:
            logger.error(f"Erro na extração de entidades: {e}")
            return {}
    
    def identify_context(self, text: str) -> List[str]:
        """
        Identifica o contexto/domínio do texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de contextos identificados
        """
        try:
            text_lower = text.lower()
            contexts = []
            
            for context, keywords in self.context_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score >= 2:  # Pelo menos 2 palavras-chave
                    contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Erro na identificação de contexto: {e}")
            return []


class NewsAnalysisService:
    """Serviço principal de análise de notícias"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
    
    def analyze_news(self, title: str, content: str, summary: str = "") -> Dict[str, any]:
        """
        Análise completa de uma notícia
        
        Args:
            title: Título da notícia
            content: Conteúdo da notícia
            summary: Resumo da notícia (opcional)
            
        Returns:
            Dict com todas as análises
        """
        try:
            # Combinar textos para análise
            full_text = f"{title} {summary} {content}"
            
            # Análise de sentimento
            sentiment = self.sentiment_analyzer.analyze_sentiment(full_text)
            
            # Extração de entidades
            entities = self.entity_extractor.extract_entities(full_text)
            
            # Identificação de contexto
            contexts = self.entity_extractor.identify_context(full_text)
            
            # Análise específica do título
            title_sentiment = self.sentiment_analyzer.analyze_sentiment(title)
            
            return {
                'sentiment': sentiment,
                'title_sentiment': title_sentiment,
                'entities': entities,
                'contexts': contexts,
                'analysis_timestamp': datetime.now().isoformat(),
                'text_stats': {
                    'title_length': len(title),
                    'content_length': len(content),
                    'summary_length': len(summary),
                    'total_words': len(full_text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na análise completa: {e}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def batch_analyze(self, news_list: List[Dict]) -> List[Dict]:
        """
        Análise em lote de múltiplas notícias
        
        Args:
            news_list: Lista de dicionários com notícias
            
        Returns:
            Lista com análises
        """
        results = []
        
        for i, news in enumerate(news_list):
            try:
                title = news.get('title', '')
                content = news.get('content', '')
                summary = news.get('summary', '')
                
                analysis = self.analyze_news(title, content, summary)
                analysis['news_index'] = i
                analysis['news_id'] = news.get('id')
                
                results.append(analysis)
                
            except Exception as e:
                logger.error(f"Erro na análise da notícia {i}: {e}")
                results.append({
                    'news_index': i,
                    'news_id': news.get('id'),
                    'error': str(e),
                    'analysis_timestamp': datetime.now().isoformat()
                })
        
        return results


# Função utilitária para uso direto
def analyze_single_news(title: str, content: str, summary: str = "") -> Dict[str, any]:
    """
    Função utilitária para análise rápida de uma notícia
    
    Args:
        title: Título da notícia
        content: Conteúdo da notícia
        summary: Resumo da notícia (opcional)
        
    Returns:
        Dict com análise completa
    """
    service = NewsAnalysisService()
    return service.analyze_news(title, content, summary)


if __name__ == "__main__":
    # Teste básico
    service = NewsAnalysisService()
    
    test_news = {
        'title': 'Economia brasileira cresce 2,5% no último trimestre',
        'content': 'O PIB brasileiro registrou crescimento de 2,5% no último trimestre, superando as expectativas dos analistas. O resultado foi impulsionado pelo setor de serviços e pela recuperação do mercado de trabalho.',
        'summary': 'PIB cresce acima do esperado com recuperação do emprego'
    }
    
    result = service.analyze_news(
        test_news['title'],
        test_news['content'],
        test_news['summary']
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
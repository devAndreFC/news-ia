"""
Serviços para análise de notícias
"""
import os
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from django.utils import timezone

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
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analisa o sentimento de um texto"""
        try:
            # Normalizar texto
            normalized_text = self._normalize_text(text)
            words = normalized_text.split()
            
            # Contar palavras por categoria
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            total_words = len(words)
            if total_words == 0:
                return {'score': 0.0, 'label': 'neutro', 'confidence': 0.0}
            
            # Calcular score (-1 a 1)
            score = (positive_count - negative_count) / total_words
            
            # Determinar label
            if score > 0.02:
                label = 'positivo'
            elif score < -0.02:
                label = 'negativo'
            else:
                label = 'neutro'
            
            # Calcular confiança
            sentiment_words = positive_count + negative_count
            confidence = min(sentiment_words / total_words * 2, 1.0)
            
            return {
                'score': round(score, 3),
                'label': label,
                'confidence': round(confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {'score': 0.0, 'label': 'neutro', 'confidence': 0.0}
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para análise"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class EntityExtractor:
    """Extrator de entidades nomeadas"""
    
    def __init__(self):
        self.patterns = {
            'pessoa': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',
                r'\b(?:Sr\.|Sra\.|Dr\.|Dra\.)\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',
            ],
            'organizacao': [
                r'\b[A-Z][A-Za-z]*(?:\s[A-Z][A-Za-z]*)*\s(?:S\.A\.|Ltda\.|Inc\.|Corp\.)\b',
                r'\b(?:Ministério|Secretaria|Prefeitura|Governo)\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',
                r'\b[A-Z]{2,}\b',
            ],
            'local': [
                r'\b(?:São Paulo|Rio de Janeiro|Brasília|Salvador|Fortaleza|Belo Horizonte)\b',
                r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s-\s[A-Z]{2})?\b',
            ],
            'valor_monetario': [
                r'R\$\s*\d+(?:\.\d{3})*(?:,\d{2})?\b',
                r'\b\d+(?:\.\d{3})*(?:,\d{2})?\s*(?:reais|milhões|bilhões)\b',
            ],
            'porcentagem': [
                r'\b\d+(?:,\d+)?%\b',
            ]
        }
        
        self.context_keywords = {
            'economia': ['economia', 'mercado', 'bolsa', 'investimento', 'pib', 'inflação'],
            'politica': ['governo', 'presidente', 'ministro', 'deputado', 'eleição'],
            'tecnologia': ['tecnologia', 'internet', 'software', 'digital', 'inovação'],
            'saude': ['saúde', 'hospital', 'médico', 'doença', 'tratamento', 'vacina'],
            'esportes': ['futebol', 'basquete', 'olimpíadas', 'copa', 'campeonato'],
            'educacao': ['educação', 'escola', 'universidade', 'professor', 'ensino']
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades nomeadas do texto"""
        try:
            entities = {}
            
            for entity_type, patterns in self.patterns.items():
                found_entities = set()
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    found_entities.update(matches)
                
                cleaned_entities = []
                for entity in found_entities:
                    entity = entity.strip()
                    if len(entity) > 2:
                        cleaned_entities.append(entity)
                
                entities[entity_type] = cleaned_entities[:5]  # Limitar a 5 por tipo
            
            return entities
            
        except Exception as e:
            logger.error(f"Erro na extração de entidades: {e}")
            return {}
    
    def identify_context(self, text: str) -> List[str]:
        """Identifica o contexto/domínio do texto"""
        try:
            text_lower = text.lower()
            contexts = []
            
            for context, keywords in self.context_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score >= 1:  # Pelo menos 1 palavra-chave
                    contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Erro na identificação de contexto: {e}")
            return []


class CategoryClassifier:
    """Classificador automático de categorias para notícias"""
    
    def __init__(self):
        # Palavras-chave para cada categoria
        self.category_keywords = {
            'Tecnologia': {
                'primary': [
                    'tecnologia', 'software', 'hardware', 'internet', 'digital', 'computador',
                    'smartphone', 'aplicativo', 'app', 'inteligência artificial', 'ia', 'machine learning',
                    'blockchain', 'criptomoeda', 'bitcoin', 'startup', 'inovação', 'tech',
                    'programação', 'desenvolvimento', 'código', 'sistema', 'plataforma',
                    'google', 'apple', 'microsoft', 'facebook', 'meta', 'amazon', 'netflix'
                ],
                'secondary': [
                    'dados', 'nuvem', 'cloud', 'segurança', 'cyber', 'robô', 'automação',
                    'virtual', 'realidade', 'gaming', 'game', 'eletrônico', 'chip'
                ]
            },
            'Economia': {
                'primary': [
                    'economia', 'mercado', 'bolsa', 'ações', 'investimento', 'financeiro',
                    'banco', 'dinheiro', 'real', 'dólar', 'moeda', 'inflação', 'pib',
                    'juros', 'taxa', 'selic', 'ipca', 'economia', 'empresas', 'negócios',
                    'lucro', 'prejuízo', 'receita', 'faturamento', 'vendas'
                ],
                'secondary': [
                    'comércio', 'varejo', 'indústria', 'setor', 'crescimento', 'recessão',
                    'crise', 'recuperação', 'exportação', 'importação', 'balança'
                ]
            },
            'Política': {
                'primary': [
                    'política', 'governo', 'presidente', 'ministro', 'deputado', 'senador',
                    'congresso', 'senado', 'câmara', 'eleição', 'voto', 'partido',
                    'democracia', 'lei', 'projeto', 'reforma', 'constituição',
                    'brasília', 'planalto', 'palácio', 'supremo', 'stf'
                ],
                'secondary': [
                    'municipal', 'estadual', 'federal', 'prefeito', 'governador',
                    'política', 'campanha', 'candidato', 'coligação', 'aliança'
                ]
            },
            'Esportes': {
                'primary': [
                    'futebol', 'basquete', 'vôlei', 'tênis', 'natação', 'atletismo',
                    'olimpíadas', 'copa', 'mundial', 'campeonato', 'jogo', 'partida',
                    'time', 'clube', 'jogador', 'atleta', 'técnico', 'treinador',
                    'gol', 'vitória', 'derrota', 'empate', 'resultado'
                ],
                'secondary': [
                    'estádio', 'arena', 'ginásio', 'campo', 'quadra', 'piscina',
                    'medalha', 'troféu', 'prêmio', 'recorde', 'performance'
                ]
            },
            'Saúde': {
                'primary': [
                    'saúde', 'medicina', 'médico', 'hospital', 'clínica', 'paciente',
                    'doença', 'tratamento', 'cura', 'remédio', 'medicamento',
                    'vacina', 'vacinação', 'epidemia', 'pandemia', 'vírus',
                    'covid', 'coronavirus', 'sus', 'ministério da saúde'
                ],
                'secondary': [
                    'sintoma', 'diagnóstico', 'exame', 'cirurgia', 'terapia',
                    'prevenção', 'cuidado', 'bem-estar', 'qualidade de vida'
                ]
            },
            'Educação': {
                'primary': [
                    'educação', 'escola', 'universidade', 'faculdade', 'ensino',
                    'professor', 'aluno', 'estudante', 'curso', 'aula',
                    'mec', 'ministério da educação', 'enem', 'vestibular',
                    'graduação', 'pós-graduação', 'mestrado', 'doutorado'
                ],
                'secondary': [
                    'aprendizagem', 'conhecimento', 'pesquisa', 'ciência',
                    'bolsa', 'financiamento', 'fies', 'prouni', 'sisu'
                ]
            },
            'Entretenimento': {
                'primary': [
                    'entretenimento', 'cinema', 'filme', 'série', 'tv', 'televisão',
                    'música', 'cantor', 'banda', 'show', 'concerto', 'festival',
                    'teatro', 'peça', 'ator', 'atriz', 'artista', 'celebridade',
                    'famoso', 'netflix', 'globo', 'sbt', 'record'
                ],
                'secondary': [
                    'cultura', 'arte', 'livro', 'autor', 'escritor', 'literatura',
                    'exposição', 'museu', 'galeria', 'evento', 'lançamento'
                ]
            },
            'Ciência': {
                'primary': [
                    'ciência', 'pesquisa', 'estudo', 'descoberta', 'experimento',
                    'cientista', 'pesquisador', 'laboratório', 'universidade',
                    'cnpq', 'fapesp', 'capes', 'nasa', 'espaço', 'astronomia',
                    'física', 'química', 'biologia', 'matemática'
                ],
                'secondary': [
                    'inovação', 'tecnologia', 'desenvolvimento', 'teoria',
                    'método', 'análise', 'resultado', 'conclusão', 'hipótese'
                ]
            }
        }
    
    def classify_category(self, text: str, existing_categories=None) -> Dict[str, any]:
        """
        Classifica automaticamente a categoria de um texto
        
        Args:
            text: Texto para classificação
            existing_categories: Lista de categorias existentes no sistema
            
        Returns:
            Dict com categoria sugerida e confiança
        """
        try:
            # Normalizar texto
            normalized_text = self._normalize_text(text)
            words = normalized_text.split()
            
            # Calcular scores para cada categoria
            category_scores = {}
            
            for category, keywords in self.category_keywords.items():
                score = 0
                
                # Palavras-chave primárias (peso 2)
                for keyword in keywords['primary']:
                    if keyword in normalized_text:
                        score += 2
                
                # Palavras-chave secundárias (peso 1)
                for keyword in keywords['secondary']:
                    if keyword in normalized_text:
                        score += 1
                
                # Normalizar score pelo tamanho do texto
                if len(words) > 0:
                    category_scores[category] = score / len(words) * 100
                else:
                    category_scores[category] = 0
            
            # Encontrar categoria com maior score
            if not category_scores or max(category_scores.values()) == 0:
                return {
                    'suggested_category': None,
                    'confidence': 0.0,
                    'scores': category_scores,
                    'message': 'Nenhuma categoria identificada automaticamente'
                }
            
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            # Calcular confiança (0-1)
            confidence = min(best_score / 10, 1.0)  # Normalizar para 0-1
            
            # Verificar se a categoria existe no sistema
            category_exists = True
            if existing_categories:
                category_exists = any(
                    cat.name.lower() == best_category.lower() 
                    for cat in existing_categories
                )
            
            return {
                'suggested_category': best_category,
                'confidence': round(confidence, 3),
                'scores': {k: round(v, 2) for k, v in category_scores.items()},
                'category_exists': category_exists,
                'message': f'Categoria sugerida: {best_category} (confiança: {confidence:.1%})'
            }
            
        except Exception as e:
            logger.error(f"Erro na classificação de categoria: {e}")
            return {
                'suggested_category': None,
                'confidence': 0.0,
                'scores': {},
                'message': f'Erro na classificação: {str(e)}'
            }
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para classificação"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def suggest_categories_batch(self, news_list, existing_categories=None) -> List[Dict]:
        """
        Sugere categorias para uma lista de notícias
        
        Args:
            news_list: Lista de notícias (objetos ou dicts)
            existing_categories: Categorias existentes no sistema
            
        Returns:
            Lista com sugestões para cada notícia
        """
        results = []
        
        for news in news_list:
            # Extrair texto da notícia
            if hasattr(news, 'title'):
                # Objeto News
                full_text = f"{news.title} {getattr(news, 'summary', '')} {getattr(news, 'content', '')}"
                news_id = news.id
                news_title = news.title
            else:
                # Dict
                full_text = f"{news.get('title', '')} {news.get('summary', '')} {news.get('content', '')}"
                news_id = news.get('id', 'N/A')
                news_title = news.get('title', 'Sem título')
            
            # Classificar
            classification = self.classify_category(full_text, existing_categories)
            
            results.append({
                'news_id': news_id,
                'news_title': news_title,
                'classification': classification
            })
        
        return results


class NewsAnalysisService:
    """Serviço principal de análise de notícias"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.category_classifier = CategoryClassifier()
    
    def analyze_news(self, news_instance):
        """
        Análise completa de uma instância de notícia
        
        Args:
            news_instance: Instância do modelo News
            
        Returns:
            Dict com análise completa
        """
        try:
            # Combinar textos para análise
            full_text = f"{news_instance.title} {news_instance.summary} {news_instance.content}"
            
            # Análise de sentimento
            sentiment = self.sentiment_analyzer.analyze_sentiment(full_text)
            
            # Extração de entidades
            entities = self.entity_extractor.extract_entities(full_text)
            
            # Identificação de contexto
            contexts = self.entity_extractor.identify_context(full_text)
            
            # Atualizar campos da instância
            news_instance.sentiment_score = sentiment['score']
            news_instance.sentiment_label = sentiment['label']
            news_instance.sentiment_confidence = sentiment['confidence']
            news_instance.entities_data = entities
            news_instance.analysis_contexts = contexts
            news_instance.analysis_timestamp = timezone.now()
            
            # Salvar alterações
            news_instance.save(update_fields=[
                'sentiment_score', 'sentiment_label', 'sentiment_confidence',
                'entities_data', 'analysis_contexts', 'analysis_timestamp'
            ])
            
            return {
                'success': True,
                'sentiment': sentiment,
                'entities': entities,
                'contexts': contexts,
                'analysis_timestamp': news_instance.analysis_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise da notícia {news_instance.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_analyze_news(self, news_list, force_reanalyze=False):
        """
        Analisa múltiplas notícias em lote
        
        Args:
            news_list: Lista ou QuerySet de notícias
            force_reanalyze: Se True, reanalisa mesmo notícias já analisadas
            
        Returns:
            Dict com estatísticas do processamento
        """
        results = {
            'total': 0,
            'processed': 0,
            'errors': 0,
            'skipped': 0,
            'error_details': []
        }
        
        # Converter para lista se for queryset
        if hasattr(news_list, 'filter') and hasattr(news_list, 'model'):
            # É um queryset
            if not force_reanalyze:
                from django.db import models
                news_list = news_list.filter(
                    models.Q(sentiment_score__isnull=True) | 
                    models.Q(sentiment_label__isnull=True)
                )
            news_list = list(news_list)
        else:
            # Já é uma lista, filtrar notícias já analisadas se não for reanalise forçada
            if not force_reanalyze:
                news_list = [
                    news for news in news_list 
                    if news.sentiment_score is None or news.sentiment_label is None
                ]
        
        results['total'] = len(news_list)
        
        for news in news_list:
            try:
                analysis_result = self.analyze_news(news)
                if analysis_result['success']:
                    results['processed'] += 1
                else:
                    results['errors'] += 1
                    results['error_details'].append({
                        'news_id': news.id,
                        'title': news.title,
                        'error': analysis_result.get('error', 'Erro desconhecido')
                    })
            except Exception as e:
                results['errors'] += 1
                results['error_details'].append({
                    'news_id': news.id,
                    'title': news.title,
                    'error': str(e)
                })
                logger.error(f"Erro ao analisar notícia {news.id}: {e}")
        
        return results
    
    def classify_news_category(self, news_instance):
        """
        Classifica automaticamente a categoria de uma notícia
        
        Args:
            news_instance: Instância do modelo News
            
        Returns:
            Dict com resultado da classificação
        """
        try:
            # Importar aqui para evitar import circular
            from .models import Category
            
            # Obter categorias existentes
            existing_categories = Category.objects.all()
            
            # Combinar título, resumo e conteúdo para análise
            full_text = f"{news_instance.title} {news_instance.summary or ''} {news_instance.content or ''}"
            
            # Classificar
            classification = self.category_classifier.classify_category(
                full_text, 
                existing_categories
            )
            
            # Tentar encontrar categoria no banco
            suggested_category_obj = None
            if classification['suggested_category']:
                try:
                    suggested_category_obj = Category.objects.get(
                        name__iexact=classification['suggested_category']
                    )
                except Category.DoesNotExist:
                    pass
            
            return {
                'success': True,
                'classification': classification,
                'category_object': suggested_category_obj,
                'message': classification['message']
            }
            
        except Exception as e:
            logger.error(f"Erro na classificação de categoria para notícia {news_instance.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'classification': None,
                'category_object': None
            }
    
    def suggest_categories_for_news_batch(self, news_list):
        """
        Sugere categorias para múltiplas notícias
        
        Args:
            news_list: Lista ou QuerySet de notícias
            
        Returns:
            Lista com sugestões para cada notícia
        """
        try:
            # Importar aqui para evitar import circular
            from .models import Category
            
            # Obter categorias existentes
            existing_categories = Category.objects.all()
            
            # Converter para lista se for queryset
            if hasattr(news_list, 'filter') and hasattr(news_list, 'model'):
                news_list = list(news_list)
            
            # Usar o método batch do classificador
            suggestions = self.category_classifier.suggest_categories_batch(
                news_list, 
                existing_categories
            )
            
            # Enriquecer com objetos de categoria
            for suggestion in suggestions:
                classification = suggestion['classification']
                if classification['suggested_category']:
                    try:
                        category_obj = Category.objects.get(
                            name__iexact=classification['suggested_category']
                        )
                        suggestion['category_object'] = category_obj
                    except Category.DoesNotExist:
                        suggestion['category_object'] = None
                else:
                    suggestion['category_object'] = None
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro na sugestão de categorias em lote: {e}")
            return []


class AINewsClassifier:
    """Classificador de notícias usando OpenAI para as 10 categorias fixas"""
    
    def __init__(self):
        self.fixed_categories = [
            'Política', 'Economia', 'Tecnologia', 'Esportes', 'Saúde',
            'Educação', 'Meio Ambiente', 'Cultura', 'Segurança', 'Internacional'
        ]
        
        # Configuração do OpenAI
        import os
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                timeout=120.0  # Timeout de 30 segundos para evitar travamentos
            )
        else:
            self.client = None
            logger.warning("OpenAI API key não encontrada. Usando classificação por palavras-chave.")
    
    def classify_news_content(self, title: str, content: str, summary: str = "") -> dict:
        """
        Classifica uma notícia usando IA ou fallback para palavras-chave
        
        Args:
            title: Título da notícia
            content: Conteúdo da notícia
            summary: Resumo da notícia (opcional)
            
        Returns:
            Dict com categoria sugerida e confiança
        """
        try:
            if self.client:
                return self._classify_with_openai(title, content, summary)
            else:
                return self._classify_with_keywords(title, content, summary)
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return self._classify_with_keywords(title, content, summary)
    
    def _classify_with_openai(self, title: str, content: str, summary: str = "") -> dict:
        """Classifica usando OpenAI"""
        try:
            # Preparar o texto para análise
            full_text = f"Título: {title}\n"
            if summary:
                full_text += f"Resumo: {summary}\n"
            full_text += f"Conteúdo: {content[:1000]}"  # Limitar para não exceder tokens
            
            # Prompt para classificação
            prompt = f"""
Analise o seguinte texto de notícia e classifique-o em UMA das seguintes categorias:

Categorias disponíveis:
1. Política - Notícias sobre política nacional e internacional
2. Economia - Notícias sobre economia, mercado financeiro e negócios
3. Tecnologia - Notícias sobre tecnologia, inovação e ciência
4. Esportes - Notícias sobre esportes nacionais e internacionais
5. Saúde - Notícias sobre saúde, medicina e bem-estar
6. Educação - Notícias sobre educação e ensino
7. Meio Ambiente - Notícias sobre meio ambiente e sustentabilidade
8. Cultura - Notícias sobre cultura, arte e entretenimento
9. Segurança - Notícias sobre segurança pública e criminalidade
10. Internacional - Notícias internacionais e relações exteriores

Texto da notícia:
{full_text}

Responda APENAS com o nome exato da categoria (ex: "Tecnologia") e um número de 0 a 1 indicando sua confiança na classificação, separados por vírgula.
Formato: Categoria,Confiança
Exemplo: Tecnologia,0.95
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em classificação de notícias. Seja preciso e objetivo."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parsear resposta
            if ',' in result:
                category, confidence_str = result.split(',', 1)
                category = category.strip()
                try:
                    confidence = float(confidence_str.strip())
                except ValueError:
                    confidence = 0.5
            else:
                category = result.strip()
                confidence = 0.5
            
            # Validar categoria
            if category not in self.fixed_categories:
                # Tentar encontrar categoria similar
                category = self._find_similar_category(category)
                confidence = max(0.3, confidence - 0.2)  # Reduzir confiança
            
            return {
                'category': category,
                'confidence': confidence,
                'method': 'openai'
            }
            
        except Exception as e:
            logger.error(f"Erro na classificação OpenAI: {e}")
            return self._classify_with_keywords(title, content, summary)
    
    def _classify_with_keywords(self, title: str, content: str, summary: str = "") -> dict:
        """Classificação usando palavras-chave como fallback"""
        full_text = f"{title} {summary} {content}".lower()
        
        # Palavras-chave para cada categoria
        keywords = {
            'Tecnologia': ['tecnologia', 'software', 'app', 'digital', 'internet', 'ia', 'inteligência artificial', 'startup', 'inovação'],
            'Política': ['política', 'governo', 'eleição', 'presidente', 'ministro', 'congresso', 'senado', 'deputado'],
            'Economia': ['economia', 'mercado', 'bolsa', 'investimento', 'banco', 'dinheiro', 'inflação', 'pib', 'juros'],
            'Esportes': ['futebol', 'esporte', 'jogador', 'time', 'campeonato', 'copa', 'olimpíadas', 'atleta'],
            'Saúde': ['saúde', 'medicina', 'hospital', 'médico', 'doença', 'tratamento', 'vacina', 'covid'],
            'Educação': ['educação', 'escola', 'universidade', 'ensino', 'professor', 'aluno', 'enem', 'vestibular'],
            'Meio Ambiente': ['meio ambiente', 'sustentabilidade', 'clima', 'aquecimento global', 'poluição', 'natureza'],
            'Cultura': ['cultura', 'arte', 'música', 'cinema', 'teatro', 'festival', 'artista', 'entretenimento'],
            'Segurança': ['segurança', 'crime', 'violência', 'polícia', 'prisão', 'roubo', 'homicídio'],
            'Internacional': ['internacional', 'mundo', 'país', 'exterior', 'global', 'guerra', 'diplomacia']
        }
        
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in full_text)
            if score > 0:
                scores[category] = score / len(words)  # Normalizar
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(0.8, scores[best_category] * 2)  # Máximo 0.8 para keywords
            return {
                'category': best_category,
                'confidence': confidence,
                'method': 'keywords'
            }
        else:
            # Categoria padrão
            return {
                'category': 'Internacional',
                'confidence': 0.1,
                'method': 'default'
            }
    
    def _find_similar_category(self, category: str) -> str:
        """Encontra categoria similar na lista fixa"""
        category_lower = category.lower()
        
        # Mapeamento de sinônimos
        synonyms = {
            'tech': 'Tecnologia',
            'politica': 'Política',
            'sports': 'Esportes',
            'health': 'Saúde',
            'environment': 'Meio Ambiente',
            'education': 'Educação',
            'security': 'Segurança',
            'culture': 'Cultura',
            'economy': 'Economia',
            'international': 'Internacional'
        }
        
        for synonym, fixed_category in synonyms.items():
            if synonym in category_lower:
                return fixed_category
        
        # Se não encontrar, retornar a primeira categoria como padrão
        return self.fixed_categories[0]


# Função utilitária para análise rápida
def analyze_single_news(news_instance):
    """
    Função utilitária para análise rápida de uma notícia
    
    Args:
        news_instance: Instância do modelo News
        
    Returns:
        Dict com análise completa
    """
    service = NewsAnalysisService()
    return service.analyze_news(news_instance)


# Função utilitária para classificação automática
def classify_news_automatically(title: str, content: str, summary: str = "") -> dict:
    """
    Função utilitária para classificação automática de notícias
    
    Args:
        title: Título da notícia
        content: Conteúdo da notícia
        summary: Resumo da notícia (opcional)
        
    Returns:
        Dict com categoria sugerida e confiança
    """
    classifier = AINewsClassifier()
    return classifier.classify_news_content(title, content, summary)


# Função para extrair informações estruturadas do conteúdo bruto
def extract_news_info_from_content(news_content: str) -> dict:
    """
    Extrai informações estruturadas (título, conteúdo, resumo, fonte) de um texto bruto de notícia
    
    Args:
        news_content: Conteúdo bruto da notícia
        
    Returns:
        Dict com informações extraídas ou erro
    """
    try:
        # Configuração do OpenAI
        import os
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback: extrair informações básicas sem IA
            return _extract_info_fallback(news_content)
        
        client = OpenAI(
            api_key=api_key,
            timeout=30.0  # Timeout de 30 segundos para evitar travamentos
        )
        
        # Limitar o conteúdo para não exceder tokens
        content_preview = news_content[:2000] if len(news_content) > 2000 else news_content
        
        # Prompt para extração de informações
        prompt = f"""
Analise o seguinte texto de notícia e extraia as seguintes informações estruturadas:

1. Título: Um título claro e conciso para a notícia
2. Conteúdo: O texto principal da notícia (pode ser o texto original se já estiver bem formatado)
3. Resumo: Um resumo de 1-2 frases da notícia
4. Fonte: A fonte da notícia (se mencionada no texto)

Texto da notícia:
{content_preview}

Responda APENAS em formato JSON válido com as chaves: title, content, summary, source.
Se alguma informação não estiver disponível, use uma string vazia.

Exemplo de resposta:
{{
    "title": "Título extraído da notícia",
    "content": "Conteúdo principal da notícia...",
    "summary": "Resumo da notícia em 1-2 frases.",
    "source": "Nome da fonte"
}}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em extração de informações de notícias. Responda sempre em JSON válido."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Tentar parsear o JSON
        import json
        try:
            extracted_data = json.loads(result)
            
            # Validar campos obrigatórios
            if not extracted_data.get('title'):
                extracted_data['title'] = _extract_title_fallback(news_content)
            
            if not extracted_data.get('content'):
                extracted_data['content'] = news_content
            
            if not extracted_data.get('source'):
                extracted_data['source'] = 'Fonte não identificada'
                
            return {
                'success': True,
                'data': extracted_data,
                'method': 'openai'
            }
            
        except json.JSONDecodeError:
            logger.error(f"Erro ao parsear JSON da resposta OpenAI: {result}")
            return _extract_info_fallback(news_content)
            
    except Exception as e:
        logger.error(f"Erro na extração de informações com OpenAI: {e}")
        return _extract_info_fallback(news_content)


def _extract_info_fallback(news_content: str) -> dict:
    """
    Extração de informações usando métodos simples como fallback
    """
    try:
        lines = news_content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Tentar extrair título (primeira linha não vazia)
        title = lines[0] if lines else 'Título não identificado'
        
        # Limitar título a um tamanho razoável
        if len(title) > 150:
            title = title[:147] + '...'
        
        # Conteúdo é o texto original
        content = news_content
        
        # Resumo: primeiras 2 frases ou primeiros 200 caracteres
        summary = _create_summary_fallback(news_content)
        
        return {
            'success': True,
            'data': {
                'title': title,
                'content': content,
                'summary': summary,
                'source': 'Fonte não identificada'
            },
            'method': 'fallback'
        }
        
    except Exception as e:
        logger.error(f"Erro no fallback de extração: {e}")
        return {
            'success': False,
            'error': f'Erro na extração de informações: {str(e)}',
            'data': None
        }


def _extract_title_fallback(content: str) -> str:
    """Extrai título usando método simples"""
    lines = content.strip().split('\n')
    first_line = lines[0].strip() if lines else 'Título não identificado'
    
    # Limitar tamanho
    if len(first_line) > 150:
        first_line = first_line[:147] + '...'
    
    return first_line


def _create_summary_fallback(content: str) -> str:
    """Cria resumo usando método simples"""
    # Pegar primeiras 2 frases ou primeiros 200 caracteres
    sentences = content.split('.')
    if len(sentences) >= 2:
        summary = f"{sentences[0].strip()}.{sentences[1].strip()}."
    else:
        summary = content[:200] + '...' if len(content) > 200 else content
    
    return summary.strip()
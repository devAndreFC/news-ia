"""
RabbitMQ Messaging System for News Curator
"""
import pika
import json
import logging
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class RabbitMQManager:
    """RabbitMQ connection and messaging manager"""
    
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.username = os.getenv('RABBITMQ_USER', 'admin')
        self.password = os.getenv('RABBITMQ_PASSWORD', 'admin')
        self.connection = None
        self.channel = None
        
        # Queue names
        self.NEWS_QUEUE = 'news_generation'
        self.NEWSLETTER_QUEUE = 'newsletter_processing'
        self.SUMMARY_QUEUE = 'summary_generation'
        
        self._connect()
        self._setup_queues()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                logger.info(f"Conectado ao RabbitMQ em {self.host}:{self.port}")
                return
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} de conexão falhou: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Falha ao conectar ao RabbitMQ após todas as tentativas")
                    raise
    
    def _setup_queues(self):
        """Setup all required queues"""
        queues = [
            {
                'name': self.NEWS_QUEUE,
                'durable': True,
                'description': 'Queue for news generation requests'
            },
            {
                'name': self.NEWSLETTER_QUEUE,
                'durable': True,
                'description': 'Queue for newsletter processing'
            },
            {
                'name': self.SUMMARY_QUEUE,
                'durable': True,
                'description': 'Queue for summary generation'
            }
        ]
        
        for queue_config in queues:
            try:
                self.channel.queue_declare(
                    queue=queue_config['name'],
                    durable=queue_config['durable']
                )
                logger.info(f"Queue '{queue_config['name']}' configurada: {queue_config['description']}")
            except Exception as e:
                logger.error(f"Erro ao configurar queue {queue_config['name']}: {e}")
    
    def publish_news_generation_request(self, categories: List[Dict], news_per_category: int = 1) -> bool:
        """Publish a news generation request"""
        try:
            message = {
                'type': 'news_generation',
                'timestamp': datetime.now().isoformat(),
                'categories': categories,
                'news_per_category': news_per_category,
                'request_id': f"news_{int(time.time())}"
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.NEWS_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Solicitação de geração de notícias publicada: {message['request_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar solicitação de geração: {e}")
            return False
    
    def publish_newsletter_processing(self, user_id: int, newsletter_data: Dict) -> bool:
        """Publish newsletter processing request"""
        try:
            message = {
                'type': 'newsletter_processing',
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'newsletter_data': newsletter_data,
                'request_id': f"newsletter_{user_id}_{int(time.time())}"
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.NEWSLETTER_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Solicitação de processamento de newsletter publicada: {message['request_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar processamento de newsletter: {e}")
            return False
    
    def publish_summary_generation(self, news_articles: List[Dict], user_preferences: Dict) -> bool:
        """Publish summary generation request"""
        try:
            message = {
                'type': 'summary_generation',
                'timestamp': datetime.now().isoformat(),
                'news_articles': news_articles,
                'user_preferences': user_preferences,
                'request_id': f"summary_{int(time.time())}"
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.SUMMARY_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Solicitação de geração de resumo publicada: {message['request_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar geração de resumo: {e}")
            return False
    
    def consume_messages(self, queue_name: str, callback: Callable, auto_ack: bool = False):
        """Start consuming messages from a queue"""
        try:
            def wrapper(ch, method, properties, body):
                try:
                    message = json.loads(body.decode('utf-8'))
                    logger.info(f"Mensagem recebida da queue {queue_name}: {message.get('request_id', 'unknown')}")
                    
                    # Call the callback function
                    result = callback(message)
                    
                    if not auto_ack:
                        if result:
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            logger.info(f"Mensagem processada com sucesso: {message.get('request_id', 'unknown')}")
                        else:
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                            logger.warning(f"Falha no processamento, mensagem recolocada na fila: {message.get('request_id', 'unknown')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar mensagem JSON: {e}")
                    if not auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
                except Exception as e:
                    logger.error(f"Erro no processamento da mensagem: {e}")
                    if not auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=wrapper,
                auto_ack=auto_ack
            )
            
            logger.info(f"Iniciando consumo da queue: {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Erro ao consumir mensagens da queue {queue_name}: {e}")
    
    def get_queue_info(self, queue_name: str) -> Optional[Dict]:
        """Get information about a queue"""
        try:
            method = self.channel.queue_declare(queue=queue_name, passive=True)
            return {
                'name': queue_name,
                'message_count': method.method.message_count,
                'consumer_count': method.method.consumer_count
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações da queue {queue_name}: {e}")
            return None
    
    def purge_queue(self, queue_name: str) -> bool:
        """Purge all messages from a queue"""
        try:
            self.channel.queue_purge(queue=queue_name)
            logger.info(f"Queue {queue_name} limpa com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar queue {queue_name}: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Conexão RabbitMQ fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão RabbitMQ: {e}")

class NewsMessageHandler:
    """Handler for news-related messages"""
    
    def __init__(self, news_generator, db_manager):
        self.news_generator = news_generator
        self.db_manager = db_manager
    
    def handle_news_generation(self, message: Dict) -> bool:
        """Handle news generation request"""
        try:
            categories = message.get('categories', [])
            news_per_category = message.get('news_per_category', 1)
            request_id = message.get('request_id', 'unknown')
            
            logger.info(f"Processando geração de notícias: {request_id}")
            
            # Generate news using OpenAI
            news_batch = self.news_generator.generate_batch(categories, news_per_category)
            
            if not news_batch:
                logger.warning(f"Nenhuma notícia gerada para request: {request_id}")
                return False
            
            # Save to database
            saved_count = 0
            for news in news_batch:
                if self.db_manager.save_news(news):
                    saved_count += 1
            
            logger.info(f"Request {request_id}: {saved_count}/{len(news_batch)} notícias salvas")
            return saved_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao processar geração de notícias: {e}")
            return False
    
    def handle_newsletter_processing(self, message: Dict) -> bool:
        """Handle newsletter processing request"""
        try:
            user_id = message.get('user_id')
            newsletter_data = message.get('newsletter_data', {})
            request_id = message.get('request_id', 'unknown')
            
            logger.info(f"Processando newsletter para usuário {user_id}: {request_id}")
            
            # Here you would implement newsletter processing logic
            # For now, just log the processing
            logger.info(f"Newsletter processada para usuário {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar newsletter: {e}")
            return False
    
    def handle_summary_generation(self, message: Dict) -> bool:
        """Handle summary generation request"""
        try:
            news_articles = message.get('news_articles', [])
            user_preferences = message.get('user_preferences', {})
            request_id = message.get('request_id', 'unknown')
            
            logger.info(f"Processando geração de resumo: {request_id}")
            
            # Here you would implement AI-powered summary generation
            # For now, just log the processing
            logger.info(f"Resumo gerado para {len(news_articles)} artigos")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            return False
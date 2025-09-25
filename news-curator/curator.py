"""
News Curator Agent - Main Application
Generates fictitious news articles periodically
"""
import logging
import time
import schedule
import signal
import sys
from datetime import datetime
from typing import List, Dict

from config import CURATOR_CONFIG, LOGGING_CONFIG, RABBITMQ_CONFIG
from database import DatabaseManager
from openai_client import OpenAINewsGenerator
from messaging import RabbitMQManager, NewsMessageHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

class NewsCurator:
    """Main News Curator Agent class"""
    
    def __init__(self):
        self.db_manager = None
        self.news_generator = None
        self.rabbitmq_manager = None
        self.message_handler = None
        self.running = True
        self.messaging_enabled = RABBITMQ_CONFIG['enable_messaging']
        
        try:
            self.db_manager = DatabaseManager()
            self.news_generator = OpenAINewsGenerator()
            
            # Initialize messaging system if enabled
            if self.messaging_enabled:
                self.rabbitmq_manager = RabbitMQManager()
                self.message_handler = NewsMessageHandler(self.news_generator, self.db_manager)
                logger.info("News Curator Agent inicializado com sucesso (OpenAI GPT + RabbitMQ)")
            else:
                logger.info("News Curator Agent inicializado com sucesso (OpenAI GPT)")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar News Curator Agent: {e}")
            raise
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def initialize(self):
        """Initialize the curator agent"""
        try:
            logger.info("Initializing News Curator Agent...")
            self.db_manager = DatabaseManager()
            logger.info("News Curator Agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize News Curator Agent: {e}")
            return False
    
    def generate_news_batch(self):
        """Generate a batch of news articles"""
        try:
            logger.info("Starting news generation batch...")
            
            # Get categories from database
            categories = self.db_manager.get_categories()
            if not categories:
                logger.warning("No categories found in database")
                return
            
            # Generate news for each category using OpenAI
            news_batch = self.news_generator.generate_batch(
                categories=categories,
                news_per_category=1,  # Generate 1 news per category per batch
                author_id=1  # Default system author
            )
            
            # Save news to database
            saved_count = 0
            for news in news_batch:
                # Check for duplicates
                if not self.db_manager.check_duplicate_news(news['title']):
                    if self.db_manager.save_news(news):
                        saved_count += 1
                else:
                    logger.info(f"Skipping duplicate news: {news['title']}")
            
            logger.info(f"News generation batch completed. Saved {saved_count}/{len(news_batch)} articles")
            
        except Exception as e:
            logger.error(f"Error during news generation batch: {e}")
    
    def run_scheduler(self):
        """Run the news generation scheduler"""
        try:
            # Schedule news generation
            interval_minutes = CURATOR_CONFIG['generation_interval'] // 60
            schedule.every(interval_minutes).minutes.do(self.generate_news_batch)
            
            logger.info(f"News generation scheduled every {interval_minutes} minutes")
            
            # Generate initial batch
            logger.info("Generating initial news batch...")
            self.generate_news_batch()
            
            # Run scheduler
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
        finally:
            self.cleanup()
    
    def run_as_consumer(self):
        """Run as RabbitMQ message consumer"""
        if not self.messaging_enabled or not self.rabbitmq_manager:
            logger.error("Sistema de mensageria não está habilitado")
            return
        
        logger.info("Iniciando News Curator como consumidor de mensagens")
        
        try:
            # Start consuming news generation messages
            self.rabbitmq_manager.consume_messages(
                queue_name=self.rabbitmq_manager.NEWS_QUEUE,
                callback=self.message_handler.handle_news_generation,
                auto_ack=False
            )
        except KeyboardInterrupt:
            logger.info("Consumidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no consumidor de mensagens: {e}")
        finally:
            self.cleanup()
    
    def publish_news_generation_request(self, categories: List[Dict] = None, news_per_category: int = None):
        """Publish a news generation request to RabbitMQ"""
        if not self.messaging_enabled or not self.rabbitmq_manager:
            logger.warning("Sistema de mensageria não está habilitado")
            return False
        
        if categories is None:
            categories = self.db_manager.get_categories()
        
        if news_per_category is None:
            news_per_category = CURATOR_CONFIG['news_per_batch']
        
        return self.rabbitmq_manager.publish_news_generation_request(categories, news_per_category)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.rabbitmq_manager:
                self.rabbitmq_manager.close()
            if self.db_manager:
                self.db_manager.close()
            logger.info("Recursos limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}")
    
    def run_once(self):
        """Run news generation once (for testing)"""
        try:
            if self.initialize():
                self.generate_news_batch()
                self.cleanup()
            else:
                logger.error("Failed to initialize curator")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error running curator once: {e}")
            sys.exit(1)

def main():
    """Main function"""
    curator = NewsCurator()
    
    # Check for different execution modes
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == '--test':
            logger.info("Executando em modo de teste")
            curator.run_once()
        elif mode == '--consumer':
            logger.info("Executando em modo consumidor RabbitMQ")
            curator.run_as_consumer()
        elif mode == '--publish':
            logger.info("Publicando solicitação de geração de notícias")
            success = curator.publish_news_generation_request()
            if success:
                logger.info("Solicitação publicada com sucesso")
            else:
                logger.error("Falha ao publicar solicitação")
        else:
            logger.warning(f"Modo desconhecido: {mode}. Usando modo padrão.")
            curator.run_scheduler()
    else:
        logger.info("Iniciando News Curator Agent em modo contínuo")
        curator.run_scheduler()

if __name__ == "__main__":
    main()
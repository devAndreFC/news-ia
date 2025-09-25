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

from config import CURATOR_CONFIG, LOGGING_CONFIG
from database import DatabaseManager
from openai_client import OpenAINewsGenerator

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
        self.running = True
        
        try:
            self.db_manager = DatabaseManager()
            self.news_generator = OpenAINewsGenerator()
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
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.db_manager:
                self.db_manager.disconnect()
            logger.info("News Curator Agent shutdown completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
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
    """Main entry point"""
    curator = NewsCurator()
    
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        logger.info("Running in test mode (single execution)")
        curator.run_once()
    else:
        logger.info("Starting News Curator Agent in continuous mode")
        if curator.initialize():
            curator.run_scheduler()
        else:
            logger.error("Failed to initialize News Curator Agent")
            sys.exit(1)

if __name__ == "__main__":
    main()
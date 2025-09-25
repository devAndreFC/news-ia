"""
Database connection and operations for News Curator Agent
"""
import psycopg2
import psycopg2.extras
import logging
from typing import Dict, List, Optional
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations for the news curator"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['name'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password']
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def get_categories(self) -> List[Dict]:
        """Fetch all news categories from database"""
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT id, name FROM common_category ORDER BY name")
                categories = cursor.fetchall()
                return [dict(category) for category in categories]
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return []
    
    def get_users(self) -> List[Dict]:
        """Fetch all users from database"""
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT id, username FROM auth_user WHERE is_active = true")
                users = cursor.fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            return []
    
    def save_news(self, news_data: Dict) -> bool:
        """Save a news article to the database"""
        try:
            with self.connection.cursor() as cursor:
                insert_query = """
                INSERT INTO common_news (title, content, summary, source, published_at, category_id, author_id, is_active, created_at, updated_at)
                VALUES (%(title)s, %(content)s, %(summary)s, %(source)s, %(published_at)s, %(category_id)s, %(author_id)s, %(is_active)s, NOW(), NOW())
                """
                cursor.execute(insert_query, news_data)
                self.connection.commit()
                logger.info(f"News article saved: {news_data['title']}")
                return True
        except Exception as e:
            logger.error(f"Failed to save news article: {e}")
            self.connection.rollback()
            return False
    
    def check_duplicate_news(self, title: str) -> bool:
        """Check if news with similar title already exists"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM common_news WHERE title = %s",
                    (title,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Failed to check for duplicate news: {e}")
            return False
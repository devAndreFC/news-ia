"""
Configuration settings for News Curator Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'name': os.getenv('DB_NAME', 'newsdb'),
    'user': os.getenv('DB_USER', 'newsuser'),
    'password': os.getenv('DB_PASSWORD', 'newspass'),
}

# Curator Configuration
CURATOR_CONFIG = {
    'generation_interval': int(os.getenv('GENERATION_INTERVAL', '300')),  # 5 minutes
    'news_per_batch': int(os.getenv('NEWS_PER_BATCH', '3')),
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '60')),  # 1 minute
}

# OpenAI Configuration
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
    'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
    'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
}

# News Categories
NEWS_CATEGORIES = [
    'Tecnologia',
    'Economia',
    'Política',
    'Esportes',
    'Saúde',
    'Educação',
    'Entretenimento',
    'Ciência'
]

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
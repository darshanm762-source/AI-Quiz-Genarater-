import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-quiz-generator-secret-key-super-secure-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Quiz Settings
    DEFAULT_NUM_QUESTIONS = 20
    MIN_QUESTIONS = 5
    MAX_QUESTIONS = 50
    TIMER_SECONDS_PER_QUESTION = 30

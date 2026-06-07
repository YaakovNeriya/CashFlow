import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-fallback-key')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

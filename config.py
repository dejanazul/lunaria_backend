import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'railway-dev-secret'
    
    # Supabase Configuration - menggunakan environment variables Railway
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    # Database Configuration
    SUPABASE_DB_URL = os.environ.get('POSTGRES_URL_NON_POOLING') or os.environ.get('POSTGRES_URL')
    
    # JWT Configuration - gunakan Supabase JWT secret
    JWT_SECRET_KEY = os.environ.get('SUPABASE_JWT_SECRET') or 'jwt-dev-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Password Hashing
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS - Allow all atau specify frontend domain
    CORS_ORIGINS = ['*']  # Update dengan domain frontend production
    
    # Railway specific
    PORT = int(os.environ.get('PORT', 5000))
    RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', 'production')

class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class ProductionConfig(Config):
    DEBUG = False
    # Update dengan domain frontend production Anda
    CORS_ORIGINS = [
        'https://your-frontend-domain.com',
        'https://your-frontend-domain.vercel.app'
    ]

class TestingConfig(Config):
    TESTING = True
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}

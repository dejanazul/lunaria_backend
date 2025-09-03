import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-dev'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')  # For admin operations
    
    # Database Configuration (Multiple options)
    SUPABASE_DB_URL = os.environ.get('POSTGRES_URL_NON_POOLING')  # Direct connection
    SUPABASE_DB_URL_POOLED = os.environ.get('POSTGRES_URL')  # Pooled connection
    SUPABASE_DB_URL_PRISMA = os.environ.get('POSTGRES_PRISMA_URL')  # Prisma format
    
    # Individual Database Components
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_DATABASE = os.environ.get('POSTGRES_DATABASE', 'postgres')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('SUPABASE_JWT_SECRET') or os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-dev'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Password Hashing
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    
    # CORS
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://127.0.0.1:3000',
        'http://localhost:3001',  # Add if using different port
        'https://your-frontend-domain.com'  # Add your production domain
    ]
    
    # Connection Pool Settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }

class DevelopmentConfig(Config):
    DEBUG = True
    # Use non-pooled connection for development
    DATABASE_URL = Config.SUPABASE_DB_URL or Config.SUPABASE_DB_URL_POOLED

class ProductionConfig(Config):
    DEBUG = False
    # Use pooled connection for production
    DATABASE_URL = Config.SUPABASE_DB_URL_POOLED or Config.SUPABASE_DB_URL
    
    # Production-specific settings
    CORS_ORIGINS = [
        'https://your-production-frontend.com',
        'https://your-app-domain.com'
    ]

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Use direct connection for testing
    DATABASE_URL = Config.SUPABASE_DB_URL or Config.SUPABASE_DB_URL_POOLED

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Helper function to get the right database URL based on environment
def get_database_url(environment='development'):
    """
    Get appropriate database URL based on environment
    
    Args:
        environment (str): 'development', 'production', or 'testing'
    
    Returns:
        str: Database connection URL
    """
    if environment == 'production':
        # Use pooled connection for production (better for concurrent connections)
        return os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_PRISMA_URL')
    else:
        # Use direct connection for development/testing
        return os.environ.get('POSTGRES_URL_NON_POOLING') or os.environ.get('POSTGRES_URL')

# Validation function to check if all required environment variables are set
def validate_config():
    """
    Validate that all required environment variables are present
    
    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'POSTGRES_PASSWORD',
        'POSTGRES_HOST'
    ]
    
    missing_vars = []
    for var in required_vars:
        # Check multiple possible variable names
        if var == 'SUPABASE_URL':
            if not (os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL')):
                missing_vars.append(var)
        elif var == 'SUPABASE_ANON_KEY':
            if not (os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')):
                missing_vars.append(var)
        else:
            if not os.environ.get(var):
                missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

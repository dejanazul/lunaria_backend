import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import modules dari struktur project
from config import config
from utils.database import init_supabase
from middleware.error_handler import register_error_handlers

def create_app(config_name='production'):
    """Create Flask application for Railway deployment"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Override with Railway-specific settings
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'railway-secret-key'),
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_KEY': os.environ.get('SUPABASE_ANON_KEY'),
        'SUPABASE_SERVICE_ROLE_KEY': os.environ.get('SUPABASE_SERVICE_ROLE_KEY'),
        'JWT_SECRET_KEY': os.environ.get('SUPABASE_JWT_SECRET'),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
        'DEBUG': False,  # Always False in production
        'CORS_ORIGINS': ['*']  # Atau specify frontend domain Anda
    })
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # Initialize Supabase
    try:
        init_supabase(app)
        app.logger.info("✅ Supabase connection successful")
    except Exception as e:
        app.logger.error(f"❌ Supabase connection failed: {e}")
        print(f"Supabase Error: {e}")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Import dan register blueprints
    try:
        from routes.auth import auth_bp
        # from routes.users import users_bp
        from routes.cycles import cycles_bp
        from routes.activities import activities_bp
        from routes.communities import communities_bp
        from routes.cookies import cookies_bp
        
        # Register blueprints dengan prefix
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        # app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(cycles_bp, url_prefix='/api/cycles')
        app.register_blueprint(activities_bp, url_prefix='/api/activities')
        app.register_blueprint(communities_bp, url_prefix='/api/communities')
        app.register_blueprint(cookies_bp, url_prefix='/api/cookies')
        
        app.logger.info("✅ All blueprints registered successfully")
    except Exception as e:
        app.logger.error(f"❌ Blueprint registration failed: {e}")
        print(f"Blueprint Error: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'period-tracker-api',
            'platform': 'railway',
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
            'supabase_connected': hasattr(app, 'supabase_client')
        }
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'message': 'Period Tracker API on Railway',
            'version': '1.0.0',
            'health': '/api/health',
            'docs': 'https://your-docs-url.com',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'cycles': '/api/cycles',
                'activities': '/api/activities',
                'communities': '/api/communities',
                'cookies': '/api/cookies'
            }
        }
    
    return app

# Create app instance
app = create_app()

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

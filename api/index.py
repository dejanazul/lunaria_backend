import os
import sys

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'app'))

# Import everything needed
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import your existing modules from app/ folder
from app.config import config
from app.utils.database import init_supabase
from app.middleware.error_handler import register_error_handlers

def create_app():
    """Create Flask app - All-in-one function for Vercel Hobby"""
    app = Flask(__name__)
    
    # Configuration untuk Vercel
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret'),
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_KEY': os.environ.get('SUPABASE_ANON_KEY'),
        'JWT_SECRET_KEY': os.environ.get('SUPABASE_JWT_SECRET', 'jwt-dev'),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
        'DEBUG': False,
        'CORS_ORIGINS': ['*']
    })
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # Initialize database
    try:
        init_supabase(app)
        print("Supabase initialized successfully")
    except Exception as e:
        print(f"Supabase init error: {e}")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Import dan register ALL blueprints dalam function ini
    try:
        from app.routes.auth import auth_bp
        # from app.routes.users import users_bp
        from app.routes.cycles import cycles_bp
        from app.routes.activities import activities_bp
        from app.routes.communities import communities_bp
        from app.routes.cookies import cookies_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        # app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(cycles_bp, url_prefix='/api/cycles')
        app.register_blueprint(activities_bp, url_prefix='/api/activities')
        app.register_blueprint(communities_bp, url_prefix='/api/communities')
        app.register_blueprint(cookies_bp, url_prefix='/api/cookies')
        
        print("All blueprints registered successfully")
    except Exception as e:
        print(f"Blueprint registration error: {e}")
    
    # Health check
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'period-tracker-api',
            'platform': 'vercel-hobby',
            'functions_used': 1
        }
    
    @app.route('/')
    def root():
        return {
            'message': 'Period Tracker API - Single Function',
            'health': '/api/health',
            'plan': 'vercel-hobby'
        }
    
    return app

# Create single app instance untuk Vercel
app = create_app()

# For local testing
if __name__ == '__main__':
    app.run(debug=False, port=5000)

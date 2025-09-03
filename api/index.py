import os
import sys
from datetime import timedelta

# Add api directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing create_app dari __init__.py yang sudah ada
from __init__ import create_app

def create_vercel_app():
    """Create Flask app for Vercel serverless"""
    # Override environment for Vercel
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # Use existing app factory dengan production config
    app = create_app('production')
    
    # Vercel-specific overrides
    app.config.update({
        'DEBUG': False,
        'CORS_ORIGINS': ['*']  # Allow all untuk serverless
    })
    
    return app

# Create app instance untuk Vercel
app = create_vercel_app()

# For local testing
if __name__ == '__main__':
    app.run(debug=False, port=5000)

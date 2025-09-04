import os
from flask import Flask

def create_app(config_object: str | None = None) -> Flask:
    app = Flask(__name__)

    # Load konfigurasi
    if config_object:
        app.config.from_object(config_object)
    else:
        # Konfigurasi minimal via environment variables
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-change-in-production")
        app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
        app.config["ENV"] = os.getenv("FLASK_ENV", "development")

    from app.routes.main import main_bp
    from app.routes.health import health_bp

    app.register_blueprint(main_bp)                 # /
    app.register_blueprint(health_bp, url_prefix="/api")  # /api/health, /api/health/simple, dll.

    return app

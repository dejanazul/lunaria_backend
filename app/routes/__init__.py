from typing import Any

def register_blueprints(app: Any) -> None:
    from .main import main_bp
    from .health import health_bp

    
    app.register_blueprint(main_bp)
    app.register_blueprint(health_bp, url_prefix="/api") 
from flask import Flask, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config, validate_config
from utils.database import init_supabase, close_db_connection, check_database_health
from middleware.error_handler import register_error_handlers


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Validate configuration
    try:
        validate_config()
        app.logger.info("Configuration validation successful")
    except ValueError as e:
        app.logger.error(f"Configuration validation failed: {e}")
        raise e

    # Initialize extensions
    CORS(app, origins=app.config["CORS_ORIGINS"])
    jwt = JWTManager(app)

    # Initialize Supabase connection
    try:
        init_supabase(app)
        app.logger.info("Supabase initialization successful")
    except Exception as e:
        app.logger.error(f"Supabase initialization failed: {e}")
        raise e

    # Register error handlers
    register_error_handlers(app)

    # Register teardown handlers
    @app.teardown_appcontext
    def close_db(error):
        close_db_connection()

    # Register blueprints
    from routes.auth import auth_bp

    # from app.routes.users import users_bp
    from routes.cycles import cycles_bp
    from routes.activities import activities_bp
    from routes.communities import communities_bp
    from routes.cookies import cookies_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    # app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(cycles_bp, url_prefix="/api/cycles")
    app.register_blueprint(activities_bp, url_prefix="/api/activities")
    app.register_blueprint(communities_bp, url_prefix="/api/communities")
    app.register_blueprint(cookies_bp, url_prefix="/api/cookies")

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_health = check_database_health()

        return {
            "status": "healthy" if all(db_health.values()) else "degraded",
            "service": "Lunaria-API",
            "database": db_health,
        }

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        return {"message": "Lunaria", "docs": "/api/health"}

    app.logger.info("Flask application initialized successfully")
    return app

import os
from typing import Dict, Type, Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


class Config:
    # Core
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
    TESTING: bool = False

    # App metadata
    APP_NAME: str = os.getenv("APP_NAME", "Flask Railway Simple")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    # CORS origins (bisa diolah di create_app jika pakai Flask-CORS)
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if o.strip()]

    # JSON behavior
    JSON_SORT_KEYS: bool = False
    JSONIFY_PRETTYPRINT_REGULAR: bool = False

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def from_env(cls) -> "Config":
        """
        Helper untuk memilih config class berdasarkan FLASK_ENV.
        """
        env = os.getenv("FLASK_ENV", "development").lower()
        mapping: Dict[str, Type[Config]] = {
            "development": DevelopmentConfig,
            "production": ProductionConfig,
            "testing": TestingConfig,
        }
        return mapping.get(env, DevelopmentConfig)()


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = "testing"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


# Opsional: peta nama → class untuk dipakai di factory (app.config.from_object)
config_by_name: Dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

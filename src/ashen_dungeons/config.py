import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JSON_SORT_KEYS = False
    TEMPLATES_AUTO_RELOAD = True

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/ashen_dungeons",
    )
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
    CONTENT_ROOT = os.getenv("CONTENT_ROOT", "content")

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/ashen_dungeons_test",
    )


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config(config_name: str | None = None):
    name = (config_name or os.getenv("FLASK_ENV") or "development").lower()

    mapping = {
        "development": DevelopmentConfig,
        "test": TestingConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    return mapping.get(name, DevelopmentConfig)
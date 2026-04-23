import os
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JSON_SORT_KEYS = False
    TEMPLATES_AUTO_RELOAD = True
    CONTENT_ROOT = os.getenv("CONTENT_ROOT", "content")
    LOCAL_DATA_ROOT = os.getenv("LOCAL_DATA_ROOT", "local_data")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


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

from flask import Flask

from .config import get_config
from .extensions import init_extensions
from .web.blueprints import register_blueprints


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    init_extensions(app)
    register_blueprints(app)

    return app
from flask import Flask

from .admin import bp as admin_bp
from .api import bp as api_bp
from .game import bp as game_bp
from .site import bp as site_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(site_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
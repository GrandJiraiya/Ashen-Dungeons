from flask import Flask

from .content.loader import load_content
from .services.game_service import GameService


def init_extensions(app: Flask) -> None:
    app.extensions["content_registry"] = load_content(app.config["CONTENT_ROOT"])
    app.extensions["game_service"] = GameService(
        content=app.extensions["content_registry"],
        data_root=app.config["LOCAL_DATA_ROOT"],
    )

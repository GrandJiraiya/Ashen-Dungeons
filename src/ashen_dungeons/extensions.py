from flask import Flask

from .content.loader import load_content
from .db.session import init_db


def init_extensions(app: Flask) -> None:
    init_db(app)
    app.extensions["content_registry"] = load_content(
        app.config.get("CONTENT_ROOT", "content")
    )
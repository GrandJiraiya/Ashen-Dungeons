from flask import Flask

from .db.session import init_db


def init_extensions(app: Flask) -> None:
    init_db(app)
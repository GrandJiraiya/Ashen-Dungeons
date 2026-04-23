from __future__ import annotations

from flask import Flask, g, current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def init_db(app: Flask) -> None:
    engine = create_engine(
        app.config["DATABASE_URL"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        future=True,
        pool_pre_ping=True,
    )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )

    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = session_factory

    @app.teardown_appcontext
    def shutdown_session(exception: BaseException | None = None) -> None:
        session = g.pop("db_session", None)
        if session is None:
            return

        try:
            if exception is not None:
                session.rollback()
        finally:
            session.close()


def get_db_session() -> Session:
    if "db_session" not in g:
        factory = current_app.extensions["db_session_factory"]
        g.db_session = factory()
    return g.db_session
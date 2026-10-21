from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from app.core.config import get_settings


class IntegrationUnavailable(Exception):
    pass


@lru_cache
def get_engine() -> Engine:
    secret = get_settings().database_url
    if not secret:
        raise IntegrationUnavailable()
    url = secret.get_secret_value()
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    return create_engine(
        url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 5},
    )


@contextmanager
def transaction(*, readonly: bool = False):
    with get_engine().begin() as connection:
        if readonly:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        connection.exec_driver_sql("SET LOCAL statement_timeout = '5000ms'")
        yield connection


def set_actor(connection: Connection, actor_id: str) -> None:
    from sqlalchemy import text

    connection.execute(text("SELECT set_config('acs.actor_id', :id, true)"), {"id": actor_id})

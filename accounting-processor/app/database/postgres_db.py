import contextlib
import os
from typing import Any, Generator

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

db_config = {
    "host": "postgres",
    "port": 5432,
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "minconn": 5,
    "maxconn": 10
}


def __get_postgres_connection_pool():
    return psycopg2.pool.ThreadedConnectionPool(**db_config)


@contextlib.contextmanager
def __get_connection() -> Generator[Any, None, None]:
    connection_pool = __get_postgres_connection_pool()
    connection = None

    try:
        connection = connection_pool.getconn()
        yield connection
        connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection_pool.putconn(connection)


@contextlib.contextmanager
def get_cursor() -> Generator[Any, None, None]:
    with __get_connection() as connection:
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            yield cursor
        finally:
            if cursor:
                cursor.close()

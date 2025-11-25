import os
from flask import g
import psycopg
import psycopg.rows

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    """
    Returns a Postgres connection stored in Flask's g context.
    Connection uses dict_row so rows behave like sqlite3.Row.
    """
    if "db" not in g:
        g.db = psycopg.connect(
            DATABASE_URL,
            row_factory=psycopg.rows.dict_row
        )
    return g.db

def execute(query, params=None):
    """
    Helper that automatically opens a cursor, executes, and returns rows.
    Matches sqlite `db.execute()` behavior.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(query, params or [])
        try:
            return cur.fetchall()
        except psycopg.ProgrammingError:
            # No results to fetch (INSERT, UPDATE, DELETE)
            return None

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()



import os
from flask import g
import psycopg
import psycopg.rows

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    """
    Returns Postgres connection stored in Flask's g context.
    """
    if "db" not in g:
        g.db = psycopg.connect(
            DATABASE_URL,
            row_factory=psycopg.rows.dict_row
        )
    return g.db


def execute(query, params=None):
    """
    Safe helper that:
      - converts SQLite-style '?' placeholders to Postgres '%s'
      - automatically opens/closes a cursor
      - returns list-of-dicts for SELECT queries
      - returns None for INSERT/UPDATE/DELETE
    """
    conn = get_db()

    # Convert SQLite-style "?" placeholders → Postgres "%s"
    q = query.replace("?", "%s")

    with conn.cursor() as cur:
        cur.execute(q, params or [])
        try:
            return cur.fetchall()
        except psycopg.ProgrammingError:
            # no rows to fetch (INSERT/UPDATE/DELETE)
            return None


def close_db(e=None):
    """
    Closes database connection at end of request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()



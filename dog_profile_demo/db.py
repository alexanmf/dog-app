import os
import sqlite3
from flask import g

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# --------------------------
# SQLite connection (local)
# --------------------------
def _sqlite_connect():
    conn = sqlite3.connect("dogs.db")
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------
# PostgreSQL connection (Render, psycopg v3)
# --------------------------
_pg_conn = None

def _pg_connect():
    global _pg_conn
    if _pg_conn is not None:
        return _pg_conn

    import psycopg
    from psycopg.rows import dict_row

    _pg_conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return _pg_conn

# Convert SQLite-style '?' placeholders → PostgreSQL '%s'
def _qmark_to_pg(sql: str) -> str:
    parts = sql.split("?")
    return sql if len(parts) == 1 else "%s".join(parts)

# Wrapper class to make psycopg behave like sqlite3 for your app
class _PgWrapper:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=()):
        sql = _qmark_to_pg(sql)
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                return cur.fetchall()
        return None

    def executemany(self, sql, seq):
        sql = _qmark_to_pg(sql)
        with self._conn.cursor() as cur:
            cur.executemany(sql, seq)

    def executescript(self, script):
        statements = [s.strip() for s in script.split(";") if s.strip()]
        with self._conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

# --------------------------
# Public Flask DB functions
# --------------------------
def get_db():
    """Return a database connection wrapped appropriately."""
    if "db" in g:
        return g.db

    if DATABASE_URL:
        g.db = _PgWrapper(_pg_connect())
    else:
        g.db = _sqlite_connect()

    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    # Close SQLite connection per request
    if db and not DATABASE_URL:
        try:
            db.close()
        except Exception:
            pass


import os
import sqlite3
from flask import g

# If DATABASE_URL is set (Render), we use Postgres; otherwise SQLite (local dev)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# ---------- SQLite helpers ----------
def _sqlite_connect():
    conn = sqlite3.connect("dogs.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Postgres helpers ----------
_pg_conn = None
def _pg_connect():
    global _pg_conn
    if _pg_conn is not None:
        return _pg_conn
    import psycopg2
    import psycopg2.extras
    _pg_conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return _pg_conn

def _qmark_to_pg(sql: str) -> str:
    """
    Convert SQLite-style '?' placeholders to Postgres '%s'.
    Handles the common simple cases used in this app.
    """
    parts = sql.split("?")
    if len(parts) == 1:
        return sql
    return ("%s".join(parts))  # replace every ? with %s

class _PgWrapper:
    """
    Tiny wrapper to give a SQLite-like API on psycopg2:
    - .execute(sql, params)
    - .executemany(sql, seq_of_params)
    - .executescript(sql)  (basic splitter on ';')
    - .commit()
    - .cursor() (raw access if you ever need it)
    """
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

    def executescript(self, sql_script):
        # Very simple splitter; fine for our small schema
        statements = [s.strip() for s in sql_script.split(";") if s.strip()]
        with self._conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

# ---------- Public API ----------
def get_db():
    """
    Returns a connection-like object with SQLite-ish methods.
    Stores it on flask.g for the current request context.
    """
    if "db" in g:
        return g.db

    if DATABASE_URL:
        conn = _pg_connect()
        g.db = _PgWrapper(conn)
    else:
        g.db = _sqlite_connect()
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    # For SQLite, close the connection per request
    if db and not DATABASE_URL:
        try:
            db.close()
        except Exception:
            pass
    # For Postgres, we keep a global pooled connection; nothing to do here

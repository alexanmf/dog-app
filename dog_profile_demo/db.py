import os
from flask import g
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def execute(sql, params=None):
    """
    Unified execute() function that:
    - Converts SQLite-style ? placeholders → %s
    - Returns rows (list of dicts) for SELECT
    - Returns [] for non-select
    """
    conn = get_db()
    cur = conn.cursor()

    # Convert ? placeholders → %s for psycopg3
    sql = sql.replace("?", "%s")

    cur.execute(sql, params or [])

    if cur.description:  # SELECT returns rows
        return cur.fetchall()
    return []






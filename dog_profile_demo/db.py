import os
from flask import g
import psycopg
from psycopg.rows import dict_row

def get_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    if "db" not in g:
        g.db = psycopg.connect(database_url, row_factory=dict_row)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def execute(sql, params=None):
    conn = get_db()
    cur = conn.cursor()
    sql = sql.replace("?", "%s")
    cur.execute(sql, params or [])

    if cur.description:
        return cur.fetchall()
    return []






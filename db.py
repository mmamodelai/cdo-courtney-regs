"""DB helper for the compliance scraper.

Loads DATABASE_URL from .env and connects with the scoped `compliance_intern`
role. Everything you touch lives in the `compliance` schema.
"""
import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]


@contextmanager
def get_conn():
    """Yields a connection; commits on success, rolls back on error."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_tables():
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "select table_name from information_schema.tables "
            "where table_schema = 'compliance' order by 1"
        )
        return [r[0] for r in cur.fetchall()]


def columns(table: str):
    """Introspect a compliance table's columns — handy for Claude Code."""
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "select column_name, data_type from information_schema.columns "
            "where table_schema='compliance' and table_name=%s order by ordinal_position",
            (table,),
        )
        return cur.fetchall()


if __name__ == "__main__":
    print("compliance tables:", list_tables())

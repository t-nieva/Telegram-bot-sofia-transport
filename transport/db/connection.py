"""
Database connection module.
Provides a reusable function to get a PostgreSQL connection.
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))  # default port if missing
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_db_connection():
    if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        raise RuntimeError(
            "Database configuration is incomplete. Check your .env file."
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=DictCursor,
    )

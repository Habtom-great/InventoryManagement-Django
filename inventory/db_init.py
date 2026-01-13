# inventory/db_init.py
from django.db import connection

def force_utc():
    """Force PostgreSQL session timezone to UTC for Django connections."""
    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'UTC';")

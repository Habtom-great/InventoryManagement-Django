from django.db import connection

def force_utc():
    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'UTC';")

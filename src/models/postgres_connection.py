import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from flask import current_app
import os

@contextmanager
def get_postgres_connection():
    """Context manager para conexão com PostgreSQL"""
    conn = None
    try:
        # Construir URL de conexão
        host = current_app.config.get('POSTGRES_HOST', 'localhost')
        port = current_app.config.get('POSTGRES_PORT', '5432')
        database = current_app.config.get('POSTGRES_DB', 'dashboard_suporte')
        user = current_app.config.get('POSTGRES_USER', 'postgres')
        password = current_app.config.get('POSTGRES_PASSWORD', 'password')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            cursor_factory=RealDictCursor
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def test_postgres_connection():
    """Testa a conexão com PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Erro na conexão PostgreSQL: {e}")
        return False


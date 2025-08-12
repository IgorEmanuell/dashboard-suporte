#!/usr/bin/env python3
"""
Script para testar a conexão com o Supabase
Execute este script para verificar se a conexão está funcionando
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    try:
        print("🔍 Testando conexão com Supabase...")
        
        # Dados de conexão
        conn = psycopg2.connect(
            host="db.shfgplhdwwgdgltorren.supabase.co",
            port=5432,
            database="postgres",
            user="postgres",
            password="M@e92634664",
            cursor_factory=RealDictCursor
        )
        
        cursor = conn.cursor()
        
        # Teste básico
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexão OK! PostgreSQL Version: {version['version']}")
        
        # Testar se as tabelas existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('tickets', 'ticket_types', 'ticket_history')
        """)
        tables = cursor.fetchall()
        
        if len(tables) >= 3:
            print("✅ Tabelas do sistema encontradas!")
            for table in tables:
                print(f"   - {table['table_name']}")
        else:
            print("⚠️  Tabelas não encontradas. Execute o script init-supabase.sql")
        
        # Testar dados
        cursor.execute("SELECT COUNT(*) as count FROM ticket_types")
        count = cursor.fetchone()
        print(f"✅ Tipos de tickets cadastrados: {count['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM tickets")
        count = cursor.fetchone()
        print(f"✅ Tickets cadastrados: {count['count']}")
        
        conn.close()
        print("\n🎉 Conexão com Supabase funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
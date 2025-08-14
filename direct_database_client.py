#!/usr/bin/env python3
"""
Cliente Direto para Banco PostgreSQL/Supabase
Cria tickets diretamente no banco, sem passar pela API
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid

class DirectDatabaseClient:
    def __init__(self, host, port, database, user, password):
        """
        Inicializa conexão direta com PostgreSQL/Supabase
        
        Args:
            host: Host do banco (ex: db.xxx.supabase.co)
            port: Porta (geralmente 5432)
            database: Nome do banco
            user: Usuário do banco
            password: Senha do banco
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            print(f"🔗 Conectando ao banco {self.host}:{self.port}...")
            
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor,
                connect_timeout=30
            )
            
            # Testar conexão
            cursor = self.conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conectado! PostgreSQL: {version['version'][:50]}...")
            cursor.close()
            
            return True
            
        except psycopg2.OperationalError as e:
            print(f"❌ Erro de conexão: {e}")
            print("   Verifique host, porta, usuário e senha")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def get_ticket_types(self):
        """Busca tipos de tickets disponíveis"""
        if not self.conn:
            print("❌ Erro: Conecte ao banco primeiro")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM ticket_types WHERE is_active = true ORDER BY name")
            types = cursor.fetchall()
            cursor.close()
            
            print("\n📋 Tipos de tickets disponíveis:")
            for ticket_type in types:
                print(f"  - {ticket_type['name']}: {ticket_type['description']}")
            
            return types
            
        except Exception as e:
            print(f"❌ Erro ao buscar tipos: {e}")
            return []
    
    def create_ticket_direct(self, ticket_data):
        """
        Cria ticket diretamente no banco
        
        Args:
            ticket_data: Dicionário com dados do ticket
                - type: Nome do tipo (obrigatório)
                - title: Título (obrigatório)
                - description: Descrição (obrigatório)
                - requester: Nome do solicitante (obrigatório)
                - requester_email: Email (opcional)
                - urgency: low/medium/high (opcional, padrão: medium)
                - created_by: Quem criou (opcional, padrão: 'external')
        """
        if not self.conn:
            print("❌ Erro: Conecte ao banco primeiro")
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # 1. Buscar ID do tipo
            cursor.execute("SELECT id FROM ticket_types WHERE name = %s", (ticket_data['type'],))
            type_result = cursor.fetchone()
            
            if not type_result:
                print(f"❌ Erro: Tipo '{ticket_data['type']}' não encontrado")
                cursor.close()
                return None
            
            type_id = type_result['id']
            
            # 2. Inserir ticket (o trigger vai gerar o ticket_number automaticamente)
            insert_query = """
                INSERT INTO tickets (
                    type_id, title, description, requester, requester_email, 
                    urgency, status, created_by, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'pending', %s, %s
                ) RETURNING *
            """
            
            cursor.execute(insert_query, (
                type_id,
                ticket_data['title'],
                ticket_data['description'],
                ticket_data['requester'],
                ticket_data.get('requester_email', ''),
                ticket_data.get('urgency', 'medium'),
                ticket_data.get('created_by', 'external'),
                datetime.utcnow()
            ))
            
            # 3. Obter ticket criado
            new_ticket = cursor.fetchone()
            
            # 4. Confirmar transação
            self.conn.commit()
            cursor.close()
            
            print(f"✅ Ticket criado diretamente no banco!")
            print(f"   Número: {new_ticket['ticket_number']}")
            print(f"   ID: {new_ticket['id']}")
            print(f"   Título: {new_ticket['title']}")
            print(f"   Status: {new_ticket['status']}")
            print(f"   Criado em: {new_ticket['created_at']}")
            
            return dict(new_ticket)
            
        except Exception as e:
            print(f"❌ Erro ao criar ticket: {e}")
            if self.conn:
                self.conn.rollback()
            return None
    
    def get_tickets(self, limit=10):
        """Lista tickets do banco"""
        if not self.conn:
            print("❌ Erro: Conecte ao banco primeiro")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.*, tt.name as type_name 
                FROM tickets t 
                LEFT JOIN ticket_types tt ON t.type_id = tt.id 
                ORDER BY t.created_at DESC 
                LIMIT %s
            """, (limit,))
            
            tickets = cursor.fetchall()
            cursor.close()
            
            print(f"\n📊 Últimos {len(tickets)} tickets:")
            for ticket in tickets:
                status_icon = "✅" if ticket['status'] == 'completed' else "⏳"
                urgency_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(ticket['urgency'], "⚪")
                
                print(f"  {status_icon} #{ticket['ticket_number']}: {ticket['title']}")
                print(f"     👤 {ticket['requester']} | {urgency_icon} {ticket['urgency']} | 📅 {ticket['created_at'].strftime('%d/%m/%Y %H:%M')}")
            
            return [dict(t) for t in tickets]
            
        except Exception as e:
            print(f"❌ Erro ao buscar tickets: {e}")
            return []
    
    def close(self):
        """Fecha conexão com o banco"""
        if self.conn:
            self.conn.close()
            print("🔌 Conexão fechada")

def main():
    """Exemplo de uso do cliente direto"""
    
    # ========================================
    # CONFIGURAÇÕES DO SUPABASE - ALTERE AQUI
    # ========================================
    HOST = "db.shfgplhdwwgdgltorren.supabase.co"
    PORT = 5432
    DATABASE = "postgres"
    USER = "postgres"
    PASSWORD = "M@e92634664"
    
    # Inicializar cliente
    client = DirectDatabaseClient(HOST, PORT, DATABASE, USER, PASSWORD)
    
    # Conectar
    if not client.connect():
        return
    
    try:
        # Buscar tipos disponíveis
        client.get_ticket_types()
        
        # Criar ticket diretamente no banco
        print("\n🎫 Criando ticket diretamente no banco...")
        ticket_data = {
            "type": "Software",
            "title": "Sistema de vendas com erro 500",
            "description": "O sistema de vendas está apresentando erro 500 ao tentar finalizar pedidos. Erro começou após a atualização de ontem. Clientes não conseguem concluir compras.",
            "requester": "Carlos Vendas",
            "requester_email": "carlos@empresa.com",
            "urgency": "high",
            "created_by": "sistema_externo"
        }
        
        ticket = client.create_ticket_direct(ticket_data)
        
        # Listar tickets
        print("\n📋 Listando tickets do banco...")
        client.get_tickets(5)
        
    finally:
        # Sempre fechar conexão
        client.close()

if __name__ == "__main__":
    main()
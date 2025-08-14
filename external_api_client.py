#!/usr/bin/env python3
"""
Cliente API Externo - Criar tickets de qualquer lugar
Execute este script de qualquer máquina para criar tickets via API
"""

import requests
import json
from datetime import datetime

class ExternalTicketAPI:
    def __init__(self, server_url, username, password):
        """
        Inicializa cliente para servidor externo
        
        Args:
            server_url: URL completa do servidor (ex: http://192.168.1.100:5000)
            username: Usuário para login
            password: Senha do usuário
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # Configurar timeout e retry
        self.session.timeout = 30
    
    def login(self):
        """Faz login e obtém token de autenticação"""
        try:
            print(f"🔐 Conectando em {self.server_url}...")
            
            response = self.session.post(
                f"{self.server_url}/api/auth/login",
                json={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                print(f"✅ Login realizado! Usuário: {data['user']['username']}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Erro no login: {error_data.get('message', 'Erro desconhecido')}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro: Não foi possível conectar ao servidor {self.server_url}")
            print("   Verifique se o servidor está rodando e o IP/porta estão corretos")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ Erro: Timeout ao conectar com {self.server_url}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def create_ticket(self, ticket_data):
        """
        Cria um novo ticket
        
        Args:
            ticket_data: Dicionário com dados do ticket
                - type: Tipo do ticket (obrigatório)
                - title: Título (obrigatório)  
                - description: Descrição (obrigatório)
                - requester: Nome do solicitante (obrigatório)
                - requester_email: Email (opcional)
                - urgency: low/medium/high (opcional, padrão: medium)
        """
        if not self.token:
            print("❌ Erro: Faça login primeiro")
            return None
            
        try:
            response = self.session.post(
                f"{self.server_url}/api/tickets/",
                json=ticket_data,
                timeout=30
            )
            
            if response.status_code == 201:
                ticket = response.json()
                print(f"✅ Ticket criado com sucesso!")
                print(f"   Número: {ticket.get('ticket_number', 'N/A')}")
                print(f"   ID: {ticket['id']}")
                print(f"   Título: {ticket.get('title', 'N/A')}")
                print(f"   Status: {ticket['status']}")
                print(f"   Criado em: {ticket.get('created_at', 'N/A')}")
                return ticket
            else:
                error_data = response.json()
                print(f"❌ Erro ao criar ticket: {error_data.get('message', 'Erro desconhecido')}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def get_ticket_types(self):
        """Busca tipos de tickets disponíveis"""
        if not self.token:
            print("❌ Erro: Faça login primeiro")
            return []
            
        try:
            response = self.session.get(f"{self.server_url}/api/tickets/types")
            
            if response.status_code == 200:
                types = response.json()
                print("\n📋 Tipos de tickets disponíveis:")
                for ticket_type in types:
                    print(f"  - {ticket_type['name']}: {ticket_type['description']}")
                return types
            else:
                print(f"❌ Erro ao buscar tipos: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return []
    
    def get_tickets(self):
        """Lista todos os tickets"""
        if not self.token:
            print("❌ Erro: Faça login primeiro")
            return []
            
        try:
            response = self.session.get(f"{self.server_url}/api/tickets/")
            
            if response.status_code == 200:
                tickets = response.json()
                print(f"\n📊 Total de tickets: {len(tickets)}")
                
                for ticket in tickets[:10]:  # Mostra apenas os 10 primeiros
                    status_icon = "✅" if ticket['status'] == 'completed' else "⏳"
                    urgency_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(ticket['urgency'], "⚪")
                    
                    print(f"  {status_icon} #{ticket.get('ticket_number', ticket['id'])}: {ticket.get('title', 'Sem título')}")
                    print(f"     👤 {ticket['requester']} | {urgency_icon} {ticket['urgency']} | 📅 {ticket.get('created_at', '')[:10]}")
                
                if len(tickets) > 10:
                    print(f"  ... e mais {len(tickets) - 10} tickets")
                
                return tickets
            else:
                print(f"❌ Erro ao buscar tickets: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return []

def main():
    """Exemplo de uso do cliente externo"""
    
    # ========================================
    # CONFIGURAÇÕES - ALTERE AQUI
    # ========================================
    SERVER_URL = "http://192.168.1.100:5000"  # IP da sua VPS + porta
    USERNAME = "admin"                          # Seu usuário
    PASSWORD = "123456"                         # Sua senha
    
    # Inicializar cliente
    client = ExternalTicketAPI(SERVER_URL, USERNAME, PASSWORD)
    
    # Fazer login
    if not client.login():
        return
    
    # Buscar tipos disponíveis
    client.get_ticket_types()
    
    # Criar ticket de exemplo
    print("\n🎫 Criando ticket de exemplo...")
    ticket_data = {
        "type": "Hardware",
        "title": "Computador não liga - Urgente",
        "description": "O computador da recepção não está ligando desde esta manhã. LED da fonte acende mas não dá boot. Já tentei trocar cabo de força e verificar conexões.",
        "requester": "Maria Recepcionista",
        "requester_email": "maria@empresa.com",
        "urgency": "high"
    }
    
    ticket = client.create_ticket(ticket_data)
    
    # Listar tickets existentes
    print("\n📋 Listando tickets...")
    client.get_tickets()

if __name__ == "__main__":
    main()
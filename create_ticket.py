#!/usr/bin/env python3
"""
Script para criar tickets via API
Execute este script para criar um novo ticket no sistema
"""

import requests
import json

class TicketAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def login(self, username, password):
        """Faz login e obtém o token de autenticação"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print(f"✅ Login realizado com sucesso! Usuário: {data['user']['username']}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Erro no login: {error_data.get('message', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def get_ticket_types(self):
        """Busca os tipos de tickets disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/tickets/types")
            
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
            print(f"❌ Erro na conexão: {e}")
            return []
    
    def create_ticket(self, ticket_data):
        """Cria um novo ticket"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/tickets/",
                json=ticket_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                ticket = response.json()
                print(f"✅ Ticket criado com sucesso!")
                print(f"   Número: {ticket.get('ticket_number', 'N/A')}")
                print(f"   ID: {ticket['id']}")
                print(f"   Título: {ticket.get('title', 'N/A')}")
                print(f"   Status: {ticket['status']}")
                return ticket
            else:
                error_data = response.json()
                print(f"❌ Erro ao criar ticket: {error_data.get('message', 'Erro desconhecido')}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def get_tickets(self):
        """Busca todos os tickets"""
        try:
            response = self.session.get(f"{self.base_url}/api/tickets/")
            
            if response.status_code == 200:
                tickets = response.json()
                print(f"\n📊 Total de tickets: {len(tickets)}")
                
                for ticket in tickets[:5]:  # Mostra apenas os 5 primeiros
                    print(f"  - #{ticket.get('ticket_number', ticket['id'])}: {ticket.get('title', 'Sem título')} ({ticket['status']})")
                
                if len(tickets) > 5:
                    print(f"  ... e mais {len(tickets) - 5} tickets")
                
                return tickets
            else:
                print(f"❌ Erro ao buscar tickets: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return []

def main():
    """Função principal - exemplo de uso"""
    
    # Configurações
    API_URL = "http://localhost:5000"  # Altere para o IP da sua VPS se necessário
    USERNAME = "admin"
    PASSWORD = "123456"  # Altere para sua senha real
    
    # Inicializar API
    api = TicketAPI(API_URL)
    
    # Fazer login
    print("🔐 Fazendo login...")
    if not api.login(USERNAME, PASSWORD):
        return
    
    # Buscar tipos disponíveis
    types = api.get_ticket_types()
    
    # Exemplo 1: Criar ticket simples
    print("\n🎫 Criando ticket de exemplo...")
    ticket_data = {
        "type": "Hardware",  # Deve ser um dos tipos disponíveis
        "title": "Computador com problema na inicialização",
        "description": "O computador da sala 205 não está ligando. LED de energia acende mas não dá boot.",
        "requester": "João Silva",
        "requester_email": "joao.silva@empresa.com",
        "urgency": "high"  # low, medium, high
    }
    
    ticket = api.create_ticket(ticket_data)
    
    # Exemplo 2: Criar outro ticket
    print("\n🎫 Criando segundo ticket...")
    ticket_data2 = {
        "type": "Software",
        "title": "Excel travando ao abrir planilhas grandes",
        "description": "O Microsoft Excel trava sempre que tento abrir arquivos com mais de 10MB. Erro de memória insuficiente.",
        "requester": "Maria Santos",
        "requester_email": "maria.santos@empresa.com",
        "urgency": "medium"
    }
    
    ticket2 = api.create_ticket(ticket_data2)
    
    # Listar tickets
    print("\n📋 Listando tickets existentes...")
    api.get_tickets()

if __name__ == "__main__":
    main()
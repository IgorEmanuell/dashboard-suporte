#!/usr/bin/env python3
"""
Gerenciador de Tickets - Interface mais amigável
Execute este script para uma interface interativa
"""

import requests
import json
from datetime import datetime

class TicketManager:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.ticket_types = []
    
    def login(self, username=None, password=None):
        """Login interativo ou com credenciais fornecidas"""
        if not username:
            username = input("👤 Usuário: ")
        if not password:
            password = input("🔒 Senha: ")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                print(f"✅ Login realizado! Bem-vindo, {data['user']['username']}")
                self._load_ticket_types()
                return True
            else:
                print(f"❌ Erro no login: {response.json().get('message')}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def _load_ticket_types(self):
        """Carrega os tipos de tickets disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/tickets/types")
            if response.status_code == 200:
                self.ticket_types = response.json()
        except:
            pass
    
    def show_menu(self):
        """Mostra o menu principal"""
        print("\n" + "="*50)
        print("🎫 GERENCIADOR DE TICKETS")
        print("="*50)
        print("1. 📝 Criar novo ticket")
        print("2. 📋 Listar tickets")
        print("3. 📊 Ver estatísticas")
        print("4. 🔄 Atualizar ticket")
        print("5. 🚪 Sair")
        print("="*50)
    
    def create_ticket_interactive(self):
        """Cria ticket de forma interativa"""
        print("\n📝 CRIAR NOVO TICKET")
        print("-" * 30)
        
        # Mostrar tipos disponíveis
        if self.ticket_types:
            print("Tipos disponíveis:")
            for i, t in enumerate(self.ticket_types, 1):
                print(f"  {i}. {t['name']} - {t['description']}")
            
            try:
                choice = int(input("\nEscolha o tipo (número): ")) - 1
                if 0 <= choice < len(self.ticket_types):
                    ticket_type = self.ticket_types[choice]['name']
                else:
                    print("❌ Opção inválida")
                    return
            except ValueError:
                print("❌ Digite um número válido")
                return
        else:
            ticket_type = input("Tipo do ticket: ")
        
        # Coletar dados
        title = input("Título: ")
        description = input("Descrição: ")
        requester = input("Solicitante: ")
        requester_email = input("Email do solicitante (opcional): ")
        
        print("\nUrgência:")
        print("1. Baixa (low)")
        print("2. Média (medium)")
        print("3. Alta (high)")
        
        urgency_map = {"1": "low", "2": "medium", "3": "high"}
        urgency_choice = input("Escolha a urgência (1-3): ")
        urgency = urgency_map.get(urgency_choice, "medium")
        
        # Criar ticket
        ticket_data = {
            "type": ticket_type,
            "title": title,
            "description": description,
            "requester": requester,
            "requester_email": requester_email,
            "urgency": urgency
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/tickets/", json=ticket_data)
            
            if response.status_code == 201:
                ticket = response.json()
                print(f"\n✅ Ticket criado com sucesso!")
                print(f"   Número: {ticket.get('ticket_number')}")
                print(f"   ID: {ticket['id']}")
                print(f"   Status: {ticket['status']}")
            else:
                print(f"❌ Erro: {response.json().get('message')}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def list_tickets(self):
        """Lista todos os tickets"""
        try:
            response = self.session.get(f"{self.base_url}/api/tickets/")
            
            if response.status_code == 200:
                tickets = response.json()
                
                if not tickets:
                    print("\n📋 Nenhum ticket encontrado")
                    return
                
                print(f"\n📋 TICKETS ({len(tickets)} total)")
                print("-" * 80)
                
                for ticket in tickets:
                    status_icon = "✅" if ticket['status'] == 'completed' else "⏳"
                    urgency_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(ticket['urgency'], "⚪")
                    
                    print(f"{status_icon} #{ticket.get('ticket_number', ticket['id'])} - {ticket.get('title', 'Sem título')}")
                    print(f"   👤 {ticket['requester']} | {urgency_icon} {ticket['urgency']} | 📅 {ticket['created_at'][:10]}")
                    print(f"   📝 {ticket['description'][:100]}{'...' if len(ticket['description']) > 100 else ''}")
                    print()
            else:
                print(f"❌ Erro ao buscar tickets: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def show_stats(self):
        """Mostra estatísticas"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats/dashboard")
            
            if response.status_code == 200:
                stats = response.json()
                
                print(f"\n📊 ESTATÍSTICAS")
                print("-" * 30)
                print(f"⏳ Pendentes: {stats['pending']}")
                print(f"✅ Finalizados hoje: {len(stats.get('completed_today', []))}")
                print(f"🟢 Baixa urgência: {stats['urgency']['low']}")
                print(f"🟡 Média urgência: {stats['urgency']['medium']}")
                print(f"🔴 Alta urgência: {stats['urgency']['high']}")
            else:
                print(f"❌ Erro ao buscar estatísticas: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def run(self):
        """Executa o gerenciador"""
        print("🎫 Bem-vindo ao Gerenciador de Tickets!")
        
        # Login
        if not self.login():
            return
        
        # Menu principal
        while True:
            self.show_menu()
            choice = input("\nEscolha uma opção: ")
            
            if choice == "1":
                self.create_ticket_interactive()
            elif choice == "2":
                self.list_tickets()
            elif choice == "3":
                self.show_stats()
            elif choice == "4":
                print("🔄 Funcionalidade em desenvolvimento...")
            elif choice == "5":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida")
            
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    # Configurar URL da API
    API_URL = "http://localhost:5000"  # Altere para IP da sua VPS se necessário
    
    manager = TicketManager(API_URL)
    manager.run()
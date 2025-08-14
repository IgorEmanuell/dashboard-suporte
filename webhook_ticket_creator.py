#!/usr/bin/env python3
"""
Criador de Tickets via Webhook/Integração
Para integrar com outros sistemas (formulários web, chatbots, etc.)
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional

class WebhookTicketCreator:
    def __init__(self, api_url: str, username: str, password: str):
        """
        Inicializa criador para webhooks/integrações
        
        Args:
            api_url: URL da API (ex: http://192.168.1.100:5000)
            username: Usuário para autenticação
            password: Senha do usuário
        """
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica e obtém token"""
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=30
            )
            
            if response.status_code == 200:
                self.token = response.json()['access_token']
                return True
            else:
                print(f"❌ Erro na autenticação: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def create_from_form(self, form_data: Dict) -> Optional[Dict]:
        """
        Cria ticket a partir de dados de formulário web
        
        Args:
            form_data: Dados do formulário
                - problema: Descrição do problema
                - nome: Nome do solicitante
                - email: Email do solicitante
                - urgencia: baixa/media/alta
                - categoria: Categoria do problema
        """
        if not self.token:
            return None
        
        # Mapear dados do formulário para formato da API
        urgency_map = {
            'baixa': 'low',
            'media': 'medium', 
            'alta': 'high',
            'low': 'low',
            'medium': 'medium',
            'high': 'high'
        }
        
        category_map = {
            'computador': 'Hardware',
            'programa': 'Software',
            'internet': 'Rede',
            'impressora': 'Impressora',
            'email': 'Email',
            'sistema': 'Sistema',
            'outro': 'Outros'
        }
        
        ticket_data = {
            "type": category_map.get(form_data.get('categoria', '').lower(), 'Outros'),
            "title": f"Solicitação via formulário - {form_data.get('categoria', 'Geral')}",
            "description": form_data.get('problema', 'Sem descrição'),
            "requester": form_data.get('nome', 'Usuário Anônimo'),
            "requester_email": form_data.get('email', ''),
            "urgency": urgency_map.get(form_data.get('urgencia', '').lower(), 'medium')
        }
        
        return self._create_ticket(ticket_data)
    
    def create_from_email(self, email_data: Dict) -> Optional[Dict]:
        """
        Cria ticket a partir de email
        
        Args:
            email_data: Dados do email
                - subject: Assunto do email
                - body: Corpo do email
                - from_email: Email do remetente
                - from_name: Nome do remetente
        """
        if not self.token:
            return None
        
        # Determinar tipo baseado no assunto
        subject = email_data.get('subject', '').lower()
        ticket_type = 'Outros'
        
        if any(word in subject for word in ['computador', 'pc', 'hardware']):
            ticket_type = 'Hardware'
        elif any(word in subject for word in ['programa', 'software', 'sistema']):
            ticket_type = 'Software'
        elif any(word in subject for word in ['internet', 'rede', 'wifi']):
            ticket_type = 'Rede'
        elif any(word in subject for word in ['impressora', 'imprimir']):
            ticket_type = 'Impressora'
        elif any(word in subject for word in ['email', 'outlook']):
            ticket_type = 'Email'
        
        ticket_data = {
            "type": ticket_type,
            "title": email_data.get('subject', 'Email sem assunto'),
            "description": email_data.get('body', 'Email sem conteúdo'),
            "requester": email_data.get('from_name', 'Usuário'),
            "requester_email": email_data.get('from_email', ''),
            "urgency": "medium"
        }
        
        return self._create_ticket(ticket_data)
    
    def create_from_chatbot(self, chat_data: Dict) -> Optional[Dict]:
        """
        Cria ticket a partir de conversa de chatbot
        
        Args:
            chat_data: Dados do chat
                - user_message: Mensagem do usuário
                - user_name: Nome do usuário
                - user_email: Email do usuário
                - category: Categoria identificada pelo bot
                - urgency: Urgência identificada pelo bot
        """
        if not self.token:
            return None
        
        ticket_data = {
            "type": chat_data.get('category', 'Outros'),
            "title": f"Solicitação via chatbot - {chat_data.get('category', 'Geral')}",
            "description": f"Mensagem do usuário: {chat_data.get('user_message', 'Sem mensagem')}",
            "requester": chat_data.get('user_name', 'Usuário Chatbot'),
            "requester_email": chat_data.get('user_email', ''),
            "urgency": chat_data.get('urgency', 'medium')
        }
        
        return self._create_ticket(ticket_data)
    
    def _create_ticket(self, ticket_data: Dict) -> Optional[Dict]:
        """Cria ticket via API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/api/tickets/",
                json=ticket_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                ticket = response.json()
                print(f"✅ Ticket criado: #{ticket.get('ticket_number')} - {ticket.get('title')}")
                return ticket
            else:
                print(f"❌ Erro ao criar ticket: {response.json()}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None

# ========================================
# EXEMPLOS DE USO
# ========================================

def exemplo_formulario_web():
    """Exemplo: Ticket criado a partir de formulário web"""
    
    # Configurações
    API_URL = "http://192.168.1.100:5000"  # Altere para seu servidor
    USERNAME = "admin"
    PASSWORD = "123456"
    
    creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)
    
    # Simular dados de formulário web
    form_data = {
        'nome': 'João Silva',
        'email': 'joao@empresa.com',
        'categoria': 'computador',
        'urgencia': 'alta',
        'problema': 'Meu computador não liga desde ontem. Já tentei trocar o cabo de força mas não funcionou.'
    }
    
    ticket = creator.create_from_form(form_data)
    return ticket

def exemplo_email():
    """Exemplo: Ticket criado a partir de email"""
    
    API_URL = "http://192.168.1.100:5000"
    USERNAME = "admin"
    PASSWORD = "123456"
    
    creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)
    
    # Simular dados de email
    email_data = {
        'subject': 'Problema com impressora HP',
        'body': 'Boa tarde,\n\nA impressora HP do setor financeiro não está imprimindo em cores. Só sai em preto e branco. Os cartuchos estão cheios.\n\nAguardo retorno.\n\nObrigado,\nMaria',
        'from_name': 'Maria Santos',
        'from_email': 'maria@empresa.com'
    }
    
    ticket = creator.create_from_email(email_data)
    return ticket

def exemplo_chatbot():
    """Exemplo: Ticket criado a partir de chatbot"""
    
    API_URL = "http://192.168.1.100:5000"
    USERNAME = "admin"
    PASSWORD = "123456"
    
    creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)
    
    # Simular dados de chatbot
    chat_data = {
        'user_name': 'Pedro Almeida',
        'user_email': 'pedro@empresa.com',
        'user_message': 'Olá! Estou com problema no Excel. Ele trava sempre que abro planilhas grandes. Pode me ajudar?',
        'category': 'Software',
        'urgency': 'medium'
    }
    
    ticket = creator.create_from_chatbot(chat_data)
    return ticket

if __name__ == "__main__":
    print("🎫 Exemplos de Criação de Tickets via Webhook/Integração\n")
    
    print("1. 📝 Formulário Web:")
    exemplo_formulario_web()
    
    print("\n2. 📧 Email:")
    exemplo_email()
    
    print("\n3. 🤖 Chatbot:")
    exemplo_chatbot()
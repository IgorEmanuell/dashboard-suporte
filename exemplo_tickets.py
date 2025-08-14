#!/usr/bin/env python3
"""
Exemplos práticos de criação de tickets
Execute este script para criar tickets de exemplo
"""

import requests
import json

# Configurações
API_URL = "http://localhost:5000"  # Altere para o IP da sua VPS
USERNAME = "admin"
PASSWORD = "123456"  # Altere para sua senha real

def get_auth_token():
    """Obtém o token de autenticação"""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Erro no login: {response.json()}")
        return None

def create_ticket(token, ticket_data):
    """Cria um ticket"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f"{API_URL}/api/tickets/",
        json=ticket_data,
        headers=headers
    )
    
    if response.status_code == 201:
        ticket = response.json()
        print(f"✅ Ticket criado: #{ticket.get('ticket_number')} - {ticket.get('title')}")
        return ticket
    else:
        print(f"❌ Erro: {response.json()}")
        return None

def main():
    # Obter token
    token = get_auth_token()
    if not token:
        return
    
    print("🎫 Criando tickets de exemplo...\n")
    
    # Exemplo 1: Problema de Hardware
    ticket1 = {
        "type": "Hardware",
        "title": "Computador não liga após queda de energia",
        "description": "O computador da recepção não está ligando desde a queda de energia de ontem. LED da fonte acende mas não dá boot. Já tentei trocar o cabo de força.",
        "requester": "Ana Receptionist",
        "requester_email": "ana@empresa.com",
        "urgency": "high"
    }
    create_ticket(token, ticket1)
    
    # Exemplo 2: Problema de Software
    ticket2 = {
        "type": "Software",
        "title": "Excel travando ao abrir planilhas grandes",
        "description": "O Microsoft Excel 2019 trava sempre que tento abrir planilhas com mais de 50MB. Aparece erro de memória insuficiente, mas o computador tem 16GB RAM.",
        "requester": "Carlos Financeiro",
        "requester_email": "carlos@empresa.com",
        "urgency": "medium"
    }
    create_ticket(token, ticket2)
    
    # Exemplo 3: Problema de Rede
    ticket3 = {
        "type": "Rede",
        "title": "Internet lenta no setor de vendas",
        "description": "A conexão com a internet está muito lenta no setor de vendas. Sites demoram mais de 30 segundos para carregar. Outros setores funcionam normalmente.",
        "requester": "Maria Vendas",
        "requester_email": "maria@empresa.com",
        "urgency": "medium"
    }
    create_ticket(token, ticket3)
    
    # Exemplo 4: Problema de Impressora
    ticket4 = {
        "type": "Impressora",
        "title": "Impressora não imprime em cores",
        "description": "A impressora HP do RH não está imprimindo em cores. Só sai em preto e branco. Já verifiquei os cartuchos e estão cheios.",
        "requester": "João RH",
        "requester_email": "joao@empresa.com",
        "urgency": "low"
    }
    create_ticket(token, ticket4)
    
    # Exemplo 5: Problema de Email
    ticket5 = {
        "type": "Email",
        "title": "Não consigo enviar emails com anexos grandes",
        "description": "Quando tento enviar emails com anexos maiores que 10MB, recebo erro de timeout. Emails pequenos funcionam normalmente.",
        "requester": "Pedro Marketing",
        "requester_email": "pedro@empresa.com",
        "urgency": "medium"
    }
    create_ticket(token, ticket5)
    
    print(f"\n🎉 Todos os tickets de exemplo foram criados!")

if __name__ == "__main__":
    main()
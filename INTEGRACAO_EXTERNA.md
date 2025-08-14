# 🌐 Integração Externa - Criação de Tickets

Este guia mostra como criar tickets de forma externa, tanto via API quanto diretamente no banco de dados.

## 📋 **Métodos Disponíveis**

### 1. **Via API (Recomendado)**
- ✅ Mais seguro (autenticação, validação)
- ✅ Mantém histórico e auditoria
- ✅ Triggers automáticos funcionam
- ✅ Funciona de qualquer lugar

### 2. **Direto no Banco**
- ✅ Mais rápido
- ✅ Não depende da API estar online
- ✅ Útil para migrações em massa
- ⚠️ Requer acesso direto ao PostgreSQL

### 3. **Via Webhook/Integração**
- ✅ Ideal para formulários web
- ✅ Integração com chatbots
- ✅ Processamento de emails
- ✅ Sistemas externos

## 🚀 **Scripts Criados**

### **`external_api_client.py`** - Cliente API Externo
```python
# Configurar servidor
SERVER_URL = "http://192.168.1.100:5000"  # IP da sua VPS
USERNAME = "admin"
PASSWORD = "sua_senha"

# Usar
client = ExternalTicketAPI(SERVER_URL, USERNAME, PASSWORD)
client.login()
client.create_ticket({
    "type": "Hardware",
    "title": "Computador não liga",
    "description": "Descrição detalhada...",
    "requester": "João Silva",
    "requester_email": "joao@empresa.com",
    "urgency": "high"
})
```

### **`direct_database_client.py`** - Acesso Direto ao Banco
```python
# Configurar Supabase
HOST = "db.shfgplhdwwgdgltorren.supabase.co"
PORT = 5432
DATABASE = "postgres"
USER = "postgres"
PASSWORD = "M@e92634664"

# Usar
client = DirectDatabaseClient(HOST, PORT, DATABASE, USER, PASSWORD)
client.connect()
client.create_ticket_direct({
    "type": "Software",
    "title": "Sistema com erro",
    "description": "Descrição...",
    "requester": "Maria Santos",
    "urgency": "medium"
})
```

### **`webhook_ticket_creator.py`** - Integrações
```python
# Para formulários web, emails, chatbots
creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)

# Formulário web
creator.create_from_form(form_data)

# Email
creator.create_from_email(email_data)

# Chatbot
creator.create_from_chatbot(chat_data)
```

## 🔧 **Configurações Necessárias**

### **Para API Externa:**
1. **IP/URL do Servidor**: `http://SEU_IP_VPS:5000`
2. **Usuário e Senha**: Credenciais válidas do sistema
3. **Rede**: Porta 5000 deve estar acessível

### **Para Banco Direto:**
1. **Dados do Supabase**: Host, porta, usuário, senha
2. **Biblioteca**: `pip install psycopg2-binary`
3. **Rede**: Porta 5432 deve estar acessível

## 📊 **Estrutura do Ticket**

```python
ticket_data = {
    "type": "Hardware",           # Obrigatório - Ver tipos disponíveis
    "title": "Título descritivo", # Obrigatório
    "description": "Descrição detalhada do problema", # Obrigatório
    "requester": "Nome do solicitante",              # Obrigatório
    "requester_email": "email@empresa.com",          # Opcional
    "urgency": "high"            # Opcional - low/medium/high
}
```

## 🎯 **Tipos de Tickets Disponíveis**

- `Hardware` - Problemas de equipamentos
- `Software` - Problemas de aplicativos
- `Rede` - Problemas de conectividade
- `Sistema` - Problemas de sistema operacional
- `Impressora` - Problemas de impressão
- `Email` - Problemas de email
- `Telefonia` - Problemas de telefone
- `Acesso` - Problemas de login/permissões
- `Backup` - Problemas de backup
- `Outros` - Outros tipos

## 🔐 **Segurança**

### **API (Recomendado)**
- ✅ Autenticação via JWT
- ✅ Validação de dados
- ✅ Rate limiting (se configurado)
- ✅ Logs de auditoria

### **Banco Direto**
- ⚠️ Acesso direto ao banco
- ⚠️ Validar dados manualmente
- ⚠️ Usar apenas em redes confiáveis
- ⚠️ Considerar VPN para acesso remoto

## 🌐 **Exemplos de Integração**

### **1. Formulário Web (HTML + JavaScript)**
```html
<form id="ticketForm">
    <input name="nome" placeholder="Seu nome" required>
    <input name="email" placeholder="Seu email" type="email">
    <select name="categoria">
        <option value="computador">Computador</option>
        <option value="programa">Programa</option>
        <option value="internet">Internet</option>
    </select>
    <select name="urgencia">
        <option value="baixa">Baixa</option>
        <option value="media">Média</option>
        <option value="alta">Alta</option>
    </select>
    <textarea name="problema" placeholder="Descreva o problema" required></textarea>
    <button type="submit">Enviar Solicitação</button>
</form>

<script>
document.getElementById('ticketForm').onsubmit = function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    // Enviar para seu servidor que usa webhook_ticket_creator.py
    fetch('/webhook/create-ticket', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(response => {
        if(response.ok) {
            alert('Solicitação enviada com sucesso!');
            e.target.reset();
        }
    });
};
</script>
```

### **2. Integração com WhatsApp/Telegram**
```python
# Exemplo para bot do Telegram
def handle_message(message):
    chat_data = {
        'user_name': message.from_user.first_name,
        'user_message': message.text,
        'category': 'Outros',
        'urgency': 'medium'
    }
    
    creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)
    ticket = creator.create_from_chatbot(chat_data)
    
    if ticket:
        bot.reply_to(message, f"✅ Solicitação registrada! Número: {ticket['ticket_number']}")
```

### **3. Processamento de Email**
```python
# Exemplo para processar emails
import imaplib
import email

def process_support_emails():
    # Conectar ao email
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('suporte@empresa.com', 'senha')
    mail.select('inbox')
    
    # Buscar emails não lidos
    status, messages = mail.search(None, 'UNSEEN')
    
    creator = WebhookTicketCreator(API_URL, USERNAME, PASSWORD)
    
    for msg_id in messages[0].split():
        # Processar cada email
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        email_msg = email.message_from_bytes(msg_data[0][1])
        
        email_data = {
            'subject': email_msg['Subject'],
            'body': get_email_body(email_msg),
            'from_email': email_msg['From'],
            'from_name': get_sender_name(email_msg['From'])
        }
        
        # Criar ticket
        ticket = creator.create_from_email(email_data)
        
        if ticket:
            # Marcar como lido e responder
            mail.store(msg_id, '+FLAGS', '\\Seen')
            send_auto_reply(email_data['from_email'], ticket['ticket_number'])
```

## 🧪 **Como Testar**

### **1. Testar API Externa**
```bash
python3 external_api_client.py
```

### **2. Testar Banco Direto**
```bash
python3 direct_database_client.py
```

### **3. Testar Webhooks**
```bash
python3 webhook_ticket_creator.py
```

## 🚨 **Solução de Problemas**

### **Erro de Conexão API**
- ✅ Verificar se servidor está rodando
- ✅ Verificar IP e porta
- ✅ Verificar firewall (porta 5000)
- ✅ Testar: `curl http://SEU_IP:5000/api/health`

### **Erro de Conexão Banco**
- ✅ Verificar credenciais do Supabase
- ✅ Verificar conectividade de rede
- ✅ Testar: `telnet db.xxx.supabase.co 5432`

### **Erro de Autenticação**
- ✅ Verificar usuário e senha
- ✅ Verificar se usuário existe no sistema
- ✅ Testar login via interface web

### **Ticket não aparece**
- ✅ Verificar se foi criado no banco
- ✅ Verificar logs da aplicação
- ✅ Atualizar página do dashboard

## 📈 **Monitoramento**

### **Logs da API**
```bash
# Na VPS
docker-compose -f docker-compose-vps.yml logs -f app
```

### **Logs do Banco**
```sql
-- Ver últimos tickets criados
SELECT * FROM tickets ORDER BY created_at DESC LIMIT 10;

-- Ver histórico de criação
SELECT * FROM ticket_history WHERE action = 'created' ORDER BY changed_at DESC LIMIT 10;
```

---

**🎉 Agora você pode criar tickets de qualquer lugar e integrar com qualquer sistema!** 🚀
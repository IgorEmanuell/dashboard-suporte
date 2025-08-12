# Dashboard de Suporte Técnico - Versão Dockerizada

Sistema completo de gerenciamento de chamados de suporte técnico com arquitetura híbrida: SQLite para autenticação e PostgreSQL para dados operacionais.

## 🏗️ Arquitetura do Sistema

### Bancos de Dados
- **SQLite**: Gerenciamento de usuários e autenticação (local, embarcado na aplicação)
- **PostgreSQL**: Dados operacionais (tickets, tipos, histórico, comentários)

### Tecnologias
- **Backend**: Flask (Python 3.11)
- **Frontend**: React + TypeScript + Tailwind CSS
- **Autenticação**: JWT com SQLite
- **Containerização**: Docker + Docker Compose
- **Banco de Dados**: PostgreSQL 15

## 🚀 Instalação e Configuração

### Pré-requisitos
- Docker e Docker Compose instalados
- Git (para clonar o repositório)

### 1. Configuração Inicial

```bash
# Clone ou extraia o projeto
cd dashboard-suporte

# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Edite as variáveis conforme necessário
nano .env
```

### 2. Configuração do Banco PostgreSQL

O arquivo `docker-compose.yml` já está configurado com um banco PostgreSQL local. Para usar um banco externo:

1. Edite o arquivo `.env` ou as variáveis de ambiente no `docker-compose.yml`:

```env
POSTGRES_HOST=seu-host-postgres.com
POSTGRES_PORT=5432
POSTGRES_DB=dashboard_suporte
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha_segura
```

2. Se usar banco externo, comente ou remova o serviço `postgres` do `docker-compose.yml`

### 3. Executar o Sistema

```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Verificar se os serviços estão rodando
docker-compose ps

# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do PostgreSQL
docker-compose logs -f postgres
```

### 4. Configuração Inicial do Sistema

Após iniciar o sistema, acesse `http://localhost:5000` e:

1. **Criar usuário admin inicial**:
   ```bash
   curl -X POST http://localhost:5000/api/auth/create-admin
   ```

2. **Fazer login**:
   - Usuário: `admin`
   - Senha: `123456`

3. **Alterar senha padrão** (recomendado para produção)

## 📊 Estrutura do Banco PostgreSQL

### Tabelas Principais

#### `tickets` - Chamados de Suporte
```sql
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,  -- TK240001, TK240002, etc.
    type_id INTEGER REFERENCES ticket_types(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requester VARCHAR(255) NOT NULL,
    requester_email VARCHAR(255),
    urgency VARCHAR(20) DEFAULT 'medium',       -- low, medium, high
    status VARCHAR(20) DEFAULT 'pending',       -- pending, in_progress, completed, cancelled
    priority INTEGER DEFAULT 3,                -- 1-5 (1 = mais alta)
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    resolution TEXT,
    tags TEXT[]
);
```

#### `ticket_types` - Tipos de Chamados
```sql
CREATE TABLE ticket_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `ticket_history` - Histórico de Alterações
```sql
CREATE TABLE ticket_history (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

### Funcionalidades Automáticas

1. **Numeração Automática**: Tickets recebem números únicos no formato `TKYY####`
2. **Histórico Automático**: Todas as alterações são registradas automaticamente
3. **Timestamps**: `created_at` e `updated_at` são gerenciados automaticamente
4. **Triggers**: Sistema de triggers para auditoria e controle

## 🔧 Configuração para Produção

### 1. Variáveis de Ambiente Importantes

```env
# Segurança
SECRET_KEY=sua-chave-secreta-muito-forte-aqui

# PostgreSQL (seu banco de produção)
POSTGRES_HOST=seu-servidor-postgres.com
POSTGRES_PORT=5432
POSTGRES_DB=dashboard_suporte_prod
POSTGRES_USER=dashboard_user
POSTGRES_PASSWORD=senha-super-segura

# Flask
FLASK_ENV=production
```

### 2. Configurações de Segurança

1. **Altere a SECRET_KEY** para uma chave forte e única
2. **Configure HTTPS** com proxy reverso (nginx/traefik)
3. **Restrinja CORS** para domínios específicos
4. **Configure backup** do banco PostgreSQL
5. **Monitore logs** e performance

### 3. Backup e Restauração

```bash
# Backup do PostgreSQL
docker-compose exec postgres pg_dump -U postgres dashboard_suporte > backup.sql

# Backup do SQLite (usuários)
docker-compose exec app cp /app/src/database/app.db /backup/users.db

# Restauração
docker-compose exec postgres psql -U postgres dashboard_suporte < backup.sql
```

## 📱 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login do usuário
- `GET /api/auth/verify` - Verificar token
- `POST /api/auth/create-admin` - Criar admin inicial

### Tickets
- `GET /api/tickets/` - Listar todos os tickets
- `POST /api/tickets/` - Criar novo ticket
- `PUT /api/tickets/{id}` - Atualizar ticket
- `DELETE /api/tickets/{id}` - Deletar ticket (admin)
- `GET /api/tickets/types` - Listar tipos de tickets

### Estatísticas
- `GET /api/stats/` - Estatísticas completas
- `GET /api/stats/dashboard` - Estatísticas do dashboard

## 🛠️ Desenvolvimento

### Executar em Modo Desenvolvimento

```bash
# Apenas o banco PostgreSQL
docker-compose up -d postgres

# Configurar ambiente Python local
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Configurar variáveis de ambiente
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=dashboard_suporte
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres123

# Executar aplicação
python src/main.py
```

### Estrutura do Projeto

```
dashboard-suporte/
├── src/
│   ├── main.py                 # Aplicação Flask principal
│   ├── models/
│   │   ├── user.py            # Modelo SQLite para usuários
│   │   └── postgres_connection.py  # Conexão PostgreSQL
│   ├── routes/
│   │   ├── auth.py            # Rotas de autenticação
│   │   ├── tickets.py         # Rotas de tickets
│   │   └── stats.py           # Rotas de estatísticas
│   ├── static/                # Frontend React compilado
│   └── database/
│       └── app.db             # Banco SQLite (criado automaticamente)
├── frontend-src/              # Código fonte React
├── docker-compose.yml         # Configuração Docker
├── Dockerfile                 # Imagem da aplicação
├── init-db.sql               # Script de inicialização PostgreSQL
├── requirements.txt          # Dependências Python
└── README.md                 # Esta documentação
```

## 🔍 Monitoramento e Logs

### Verificar Status dos Serviços

```bash
# Status geral
docker-compose ps

# Logs da aplicação
docker-compose logs -f app

# Logs do PostgreSQL
docker-compose logs -f postgres

# Entrar no container da aplicação
docker-compose exec app bash

# Entrar no PostgreSQL
docker-compose exec postgres psql -U postgres dashboard_suporte
```

### Adminer (Interface Web para Banco)

Acesse `http://localhost:8080` para gerenciar o banco PostgreSQL:
- **Sistema**: PostgreSQL
- **Servidor**: postgres
- **Usuário**: postgres
- **Senha**: postgres123
- **Base de dados**: dashboard_suporte

## 🚨 Solução de Problemas

### Problemas Comuns

1. **Erro de conexão PostgreSQL**:
   ```bash
   # Verificar se o PostgreSQL está rodando
   docker-compose logs postgres
   
   # Reiniciar serviços
   docker-compose restart
   ```

2. **Aplicação não inicia**:
   ```bash
   # Verificar logs
   docker-compose logs app
   
   # Reconstruir imagem
   docker-compose build --no-cache app
   ```

3. **Banco não inicializa**:
   ```bash
   # Remover volumes e recriar
   docker-compose down -v
   docker-compose up -d
   ```

### Comandos Úteis

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reconstruir imagens
docker-compose build

# Ver uso de recursos
docker stats

# Limpar containers e imagens não utilizados
docker system prune
```

## 📈 Próximos Passos

### Melhorias Sugeridas

1. **Notificações**: Sistema de notificações por email/Slack
2. **Relatórios**: Dashboard com gráficos e métricas avançadas
3. **Mobile**: App mobile para equipe de suporte
4. **Integração**: APIs para integrar com outros sistemas
5. **Automação**: Regras automáticas para classificação de tickets

### Escalabilidade

1. **Load Balancer**: Para múltiplas instâncias da aplicação
2. **Redis**: Cache para sessões e dados temporários
3. **Elasticsearch**: Busca avançada em tickets
4. **Kubernetes**: Orquestração para ambientes grandes

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs: `docker-compose logs`
2. Consulte a documentação da API
3. Verifique as configurações de rede e firewall
4. Teste a conectividade com o banco PostgreSQL

---

**Desenvolvido para otimizar o atendimento de suporte técnico em ambientes corporativos**


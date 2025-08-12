# 🚀 Instruções de Instalação - Dashboard de Suporte

## Instalação Rápida (Recomendada)

### 1. Preparação do Ambiente

```bash
# Certifique-se que Docker e Docker Compose estão instalados
docker --version
docker-compose --version

# Clone ou extraia o projeto
cd dashboard-suporte
```

### 2. Configuração com Banco PostgreSQL Externo

Se você já tem um banco PostgreSQL na sua empresa:

1. **Edite o arquivo `docker-compose.yml`**:
   ```yaml
   # Comente ou remova toda a seção 'postgres:' 
   # Mantenha apenas os serviços 'app:' e 'adminer:'
   ```

2. **Configure as variáveis de ambiente**:
   ```bash
   # Edite o docker-compose.yml na seção environment do serviço app:
   environment:
     - SECRET_KEY=sua-chave-secreta-empresa
     - POSTGRES_HOST=seu-servidor-postgres.empresa.com
     - POSTGRES_PORT=5432
     - POSTGRES_DB=dashboard_suporte
     - POSTGRES_USER=seu_usuario_postgres
     - POSTGRES_PASSWORD=sua_senha_postgres
   ```

### 3. Criar o Banco de Dados

**Execute este SQL no seu PostgreSQL**:

```sql
-- 1. Criar o banco (se não existir)
CREATE DATABASE dashboard_suporte;

-- 2. Conectar ao banco e executar o script completo
\c dashboard_suporte;

-- 3. Copie e execute todo o conteúdo do arquivo init-db.sql
-- (O arquivo contém todas as tabelas, triggers e dados iniciais)
```

### 4. Iniciar o Sistema

```bash
# Construir e iniciar
docker-compose up -d

# Verificar se está rodando
docker-compose ps

# Ver logs (se necessário)
docker-compose logs -f app
```

### 5. Configuração Inicial

1. **Acesse**: http://localhost:5000

2. **Criar usuário admin**:
   ```bash
   curl -X POST http://localhost:5000/api/auth/create-admin
   ```

3. **Login**:
   - Usuário: `admin`
   - Senha: `123456`

4. **IMPORTANTE**: Altere a senha padrão após o primeiro login!

## Instalação com PostgreSQL Local (Desenvolvimento)

Se você não tem PostgreSQL, use a configuração padrão:

```bash
# Usar o docker-compose.yml sem modificações
docker-compose up -d

# O PostgreSQL será criado automaticamente
# Dados de acesso:
# - Host: localhost:5432
# - Usuário: postgres  
# - Senha: postgres123
# - Banco: dashboard_suporte
```

## Configuração para Produção

### 1. Segurança

```yaml
# No docker-compose.yml, altere:
environment:
  - SECRET_KEY=SUA-CHAVE-SUPER-SECRETA-AQUI-MIN-32-CHARS
  - POSTGRES_PASSWORD=senha-muito-forte-da-empresa
```

### 2. Rede e Firewall

```bash
# Certifique-se que as portas estão liberadas:
# - 5000: Aplicação web
# - 5432: PostgreSQL (se usando local)
# - 8080: Adminer (opcional, para gerenciar banco)
```

### 3. Backup Automático

```bash
# Adicione ao crontab para backup diário:
0 2 * * * docker-compose exec postgres pg_dump -U postgres dashboard_suporte > /backup/dashboard_$(date +\%Y\%m\%d).sql
```

## Verificação da Instalação

### 1. Testar Aplicação

```bash
# Verificar se a aplicação responde
curl http://localhost:5000

# Testar API
curl -X POST http://localhost:5000/api/auth/create-admin
```

### 2. Verificar Banco de Dados

```bash
# Via Adminer (interface web)
# Acesse: http://localhost:8080
# Sistema: PostgreSQL
# Servidor: postgres (ou seu servidor)
# Usuário: postgres
# Senha: postgres123
# Base: dashboard_suporte

# Via linha de comando
docker-compose exec postgres psql -U postgres dashboard_suporte -c "SELECT COUNT(*) FROM tickets;"
```

### 3. Verificar Logs

```bash
# Logs da aplicação
docker-compose logs app

# Logs do PostgreSQL
docker-compose logs postgres

# Logs em tempo real
docker-compose logs -f
```

## Comandos Úteis para Administração

### Gerenciamento de Containers

```bash
# Parar sistema
docker-compose down

# Reiniciar sistema
docker-compose restart

# Atualizar aplicação (após mudanças)
docker-compose build app
docker-compose up -d app

# Ver status
docker-compose ps

# Ver uso de recursos
docker stats
```

### Backup e Restauração

```bash
# Backup completo
mkdir backup
docker-compose exec postgres pg_dump -U postgres dashboard_suporte > backup/database.sql
docker-compose exec app cp /app/src/database/app.db backup/users.db

# Restauração
docker-compose exec postgres psql -U postgres dashboard_suporte < backup/database.sql
```

### Manutenção do Banco

```bash
# Entrar no PostgreSQL
docker-compose exec postgres psql -U postgres dashboard_suporte

# Comandos úteis no PostgreSQL:
\dt                          # Listar tabelas
SELECT COUNT(*) FROM tickets; # Contar tickets
\q                           # Sair
```

## Solução de Problemas Comuns

### Erro: "Connection refused" ao PostgreSQL

```bash
# 1. Verificar se o PostgreSQL está rodando
docker-compose ps

# 2. Verificar logs do PostgreSQL
docker-compose logs postgres

# 3. Reiniciar serviços
docker-compose restart

# 4. Se persistir, recriar volumes
docker-compose down -v
docker-compose up -d
```

### Erro: "Port already in use"

```bash
# Verificar o que está usando a porta
sudo netstat -tulpn | grep :5000

# Parar o serviço conflitante ou alterar a porta no docker-compose.yml
ports:
  - "5001:5000"  # Usar porta 5001 em vez de 5000
```

### Aplicação não carrega

```bash
# 1. Verificar logs
docker-compose logs app

# 2. Verificar se todas as dependências estão instaladas
docker-compose exec app pip list

# 3. Reconstruir imagem
docker-compose build --no-cache app
docker-compose up -d app
```

### Banco não inicializa

```bash
# 1. Verificar se o script SQL está correto
docker-compose exec postgres psql -U postgres dashboard_suporte -c "\dt"

# 2. Executar script manualmente
docker-compose exec postgres psql -U postgres dashboard_suporte < init-db.sql

# 3. Verificar permissões
docker-compose exec postgres psql -U postgres -c "SELECT current_user;"
```

## Configurações Avançadas

### Usar HTTPS (Produção)

1. **Configure um proxy reverso** (nginx/traefik)
2. **Obtenha certificados SSL** (Let's Encrypt)
3. **Redirecione HTTP para HTTPS**

### Monitoramento

```bash
# Adicionar ao docker-compose.yml:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### Escalabilidade

```bash
# Múltiplas instâncias da aplicação
docker-compose up -d --scale app=3

# Load balancer (nginx)
upstream dashboard {
    server app_1:5000;
    server app_2:5000;
    server app_3:5000;
}
```

---

## ✅ Checklist de Instalação

- [ ] Docker e Docker Compose instalados
- [ ] Projeto extraído/clonado
- [ ] Variáveis de ambiente configuradas
- [ ] Banco PostgreSQL configurado
- [ ] Script SQL executado
- [ ] Sistema iniciado com `docker-compose up -d`
- [ ] Admin criado com `/api/auth/create-admin`
- [ ] Login testado (admin/123456)
- [ ] Senha padrão alterada
- [ ] Backup configurado
- [ ] Firewall/rede configurados

**Sistema pronto para uso em produção!** 🎉


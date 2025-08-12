# 🚀 Guia de Instalação na VPS - Dashboard de Suporte

## 📋 Pré-requisitos

- VPS com Ubuntu 20.04+ ou Debian 11+
- Acesso root/sudo
- PostgreSQL configurado (local ou remoto)
- Pelo menos 1GB RAM e 10GB de espaço

## 🔧 Instalação Automática (Recomendada)

### 1. Fazer Upload dos Arquivos

```bash
# Na sua máquina local, comprimir o projeto
tar -czf dashboard-suporte.tar.gz .

# Enviar para VPS (substitua USER e IP)
scp dashboard-suporte.tar.gz user@SEU_IP_VPS:~/

# Na VPS, extrair
cd ~
tar -xzf dashboard-suporte.tar.gz
cd dashboard-suporte
```

### 2. Executar Script de Configuração

```bash
# Dar permissão e executar
chmod +x setup-vps.sh
./setup-vps.sh
```

O script irá:
- ✅ Instalar Docker, Nginx, dependências
- ✅ Configurar firewall
- ✅ Gerar chave secreta
- ✅ Configurar proxy reverso
- ✅ Configurar backup automático
- ✅ Configurar monitoramento

## 🗄️ Configuração do Banco PostgreSQL

### Opção 1: PostgreSQL Local na VPS

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Configurar usuário e banco
sudo -u postgres psql << EOF
CREATE USER dashboard_user WITH PASSWORD 'senha_forte_aqui';
CREATE DATABASE dashboard_suporte OWNER dashboard_user;
GRANT ALL PRIVILEGES ON DATABASE dashboard_suporte TO dashboard_user;
\q
EOF

# Executar script de inicialização
sudo -u postgres psql -d dashboard_suporte -f init-db-production.sql
```

### Opção 2: PostgreSQL Remoto (Supabase, AWS RDS, etc.)

```bash
# Editar configurações
nano ~/dashboard-suporte/.env

# Alterar para seus dados:
POSTGRES_HOST=seu-servidor.com
POSTGRES_PORT=5432
POSTGRES_DB=dashboard_suporte
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
```

## 🚀 Iniciar a Aplicação

```bash
cd ~/dashboard-suporte

# Iniciar apenas a aplicação
docker-compose -f docker-compose-vps.yml up -d app

# OU iniciar com Adminer (para debug)
docker-compose -f docker-compose-vps.yml --profile admin up -d

# Verificar status
docker-compose -f docker-compose-vps.yml ps
```

## 👤 Configuração Inicial

### 1. Criar Usuário Admin

```bash
# Método 1: Via API
curl -X POST http://localhost:5000/api/auth/create-admin

# Método 2: Se der erro, criar manualmente
docker-compose -f docker-compose-vps.yml exec app python3 -c "
from src.main import app
from src.models.user import db, User
with app.app_context():
    admin = User(username='admin', email='admin@dashboard.com', role='admin')
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()
    print('Admin criado!')
"
```

### 2. Testar Acesso

```bash
# Verificar saúde da aplicação
curl http://localhost:5000/api/health

# Testar login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

### 3. Acessar via Browser

- **URL**: `http://SEU_IP_VPS`
- **Login**: `admin`
- **Senha**: `123456`

**⚠️ IMPORTANTE**: Altere a senha padrão após o primeiro login!

## 🔒 Configurações de Segurança

### 1. Configurar HTTPS (Opcional mas Recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado SSL (substitua seu-dominio.com)
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Alterar Porta SSH (Recomendado)

```bash
sudo nano /etc/ssh/sshd_config
# Alterar: Port 22 para Port 2222
sudo systemctl restart ssh

# Atualizar firewall
sudo ufw allow 2222
sudo ufw delete allow ssh
```

### 3. Configurar Fail2Ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📊 Monitoramento e Logs

### Verificar Status

```bash
# Status dos containers
docker-compose -f docker-compose-vps.yml ps

# Logs da aplicação
docker-compose -f docker-compose-vps.yml logs -f app

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
tail -f ~/dashboard-suporte/logs/monitor.log
tail -f ~/dashboard-suporte/logs/backup.log
```

### Comandos Úteis

```bash
# Reiniciar aplicação
docker-compose -f docker-compose-vps.yml restart app

# Atualizar aplicação
git pull  # Se usando git
docker-compose -f docker-compose-vps.yml build --no-cache app
docker-compose -f docker-compose-vps.yml up -d app

# Backup manual
~/dashboard-suporte/backup.sh

# Ver uso de recursos
docker stats
htop
```

## 🔧 Solução de Problemas

### Aplicação não inicia

```bash
# Verificar logs
docker-compose -f docker-compose-vps.yml logs app

# Verificar conectividade PostgreSQL
docker-compose -f docker-compose-vps.yml exec app python3 -c "
from src.models.postgres_connection import test_postgres_connection
print('PostgreSQL:', 'OK' if test_postgres_connection() else 'ERRO')
"
```

### Erro de conexão PostgreSQL

```bash
# Verificar configurações
cat ~/dashboard-suporte/.env

# Testar conexão manual
psql -h SEU_HOST -p 5432 -U SEU_USER -d dashboard_suporte -c "SELECT 1;"
```

### Nginx não funciona

```bash
# Verificar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

### Porta 5000 ocupada

```bash
# Ver o que está usando a porta
sudo netstat -tulpn | grep :5000

# Matar processo se necessário
sudo kill -9 PID_DO_PROCESSO
```

## 📈 Otimizações de Performance

### 1. Configurar Swap (se VPS tem pouca RAM)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Otimizar PostgreSQL

```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf

# Configurações recomendadas para VPS pequena:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# maintenance_work_mem = 64MB
# checkpoint_completion_target = 0.9
# wal_buffers = 16MB
```

### 3. Configurar Log Rotation

```bash
sudo nano /etc/logrotate.d/dashboard-suporte

# Conteúdo:
/home/*/dashboard-suporte/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
```

## 🎯 Checklist Final

- [ ] ✅ VPS configurada com Docker e Nginx
- [ ] ✅ PostgreSQL configurado e acessível
- [ ] ✅ Script SQL executado (init-db-production.sql)
- [ ] ✅ Arquivo .env configurado com dados reais
- [ ] ✅ Aplicação iniciada e respondendo
- [ ] ✅ Usuário admin criado
- [ ] ✅ Login testado via browser
- [ ] ✅ Senha padrão alterada
- [ ] ✅ HTTPS configurado (opcional)
- [ ] ✅ Backup automático funcionando
- [ ] ✅ Monitoramento ativo

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs app`
2. Teste a conectividade: `curl http://localhost:5000/api/health`
3. Verifique o PostgreSQL: Teste conexão manual
4. Reinicie os serviços: `docker-compose restart`

---

**🎉 Dashboard de Suporte pronto para produção na sua VPS!**
# 🚀 GUIA DE DEPLOY FINAL - Dashboard de Suporte

## ✅ **CONFIGURAÇÃO COMPLETA PARA SUA VPS**

Tudo já está configurado com seus dados reais do Supabase! Agora é só seguir os passos abaixo.

---

## 📋 **PASSO 1: Configurar o Supabase**

### 1.1 Acessar o Supabase
- Acesse: https://supabase.com/dashboard
- Entre no seu projeto: `shfgplhdwwgdgltorren`

### 1.2 Executar o Script SQL
1. No painel do Supabase, vá em **SQL Editor**
2. Copie todo o conteúdo do arquivo `init-supabase.sql`
3. Cole no editor e clique em **RUN**
4. ✅ Isso criará todas as tabelas e dados necessários

---

## 📋 **PASSO 2: Preparar os Arquivos na VPS**

### 2.1 Comprimir o Projeto (na sua máquina local)
```bash
# Comprimir todos os arquivos
tar -czf dashboard-suporte.tar.gz .
```

### 2.2 Enviar para VPS
```bash
# Substitua USER e IP_DA_VPS pelos seus dados
scp dashboard-suporte.tar.gz user@IP_DA_VPS:~/
```

### 2.3 Extrair na VPS
```bash
# Conectar na VPS via SSH
ssh user@IP_DA_VPS

# Extrair arquivos
cd ~
tar -xzf dashboard-suporte.tar.gz
cd dashboard-suporte
```

---

## 📋 **PASSO 3: Executar Configuração Automática**

### 3.1 Rodar o Script de Setup
```bash
# Dar permissão e executar
chmod +x setup-vps.sh
./setup-vps.sh
```

**O script irá automaticamente:**
- ✅ Instalar Docker, Nginx, dependências
- ✅ Configurar firewall (portas 80, 443, 22, 5000)
- ✅ Gerar chave secreta forte
- ✅ Configurar proxy reverso Nginx
- ✅ Configurar backup automático (diário às 2h)
- ✅ Configurar monitoramento (a cada 5 min)
- ✅ Criar arquivo `.env` com seus dados do Supabase

---

## 📋 **PASSO 4: Iniciar a Aplicação**

### 4.1 Subir os Containers
```bash
cd ~/dashboard-suporte

# Iniciar apenas a aplicação
docker-compose -f docker-compose-vps.yml up -d app

# OU iniciar com Adminer (para debug do banco)
docker-compose -f docker-compose-vps.yml --profile admin up -d
```

### 4.2 Verificar Status
```bash
# Ver se está rodando
docker-compose -f docker-compose-vps.yml ps

# Ver logs
docker-compose -f docker-compose-vps.yml logs -f app
```

---

## 📋 **PASSO 5: Configuração Inicial**

### 5.1 Criar Usuário Admin
```bash
# Criar admin via API
curl -X POST http://localhost:5000/api/auth/create-admin

# Deve retornar algo como:
# {"message":"Admin criado com sucesso","username":"admin","password":"123456"}
```

### 5.2 Testar a Aplicação
```bash
# Testar saúde da aplicação
curl http://localhost:5000/api/health

# Testar login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

---

## 🌐 **PASSO 6: Acessar via Browser**

### 6.1 Acessar o Sistema
- **URL**: `http://IP_DA_SUA_VPS`
- **Login**: `admin`
- **Senha**: `123456`

### 6.2 ⚠️ IMPORTANTE - Alterar Senha
1. Faça login com `admin/123456`
2. **ALTERE A SENHA IMEDIATAMENTE** para uma senha forte
3. O sistema está pronto para uso!

---

## 🔧 **COMANDOS ÚTEIS PARA ADMINISTRAÇÃO**

### Gerenciar a Aplicação
```bash
# Ver status
docker-compose -f docker-compose-vps.yml ps

# Ver logs em tempo real
docker-compose -f docker-compose-vps.yml logs -f app

# Reiniciar aplicação
docker-compose -f docker-compose-vps.yml restart app

# Parar tudo
docker-compose -f docker-compose-vps.yml down

# Atualizar aplicação (após mudanças)
docker-compose -f docker-compose-vps.yml build --no-cache app
docker-compose -f docker-compose-vps.yml up -d app
```

### Monitoramento
```bash
# Ver logs do sistema
tail -f ~/dashboard-suporte/logs/monitor.log
tail -f ~/dashboard-suporte/logs/backup.log

# Ver logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Ver uso de recursos
docker stats
htop
```

### Backup Manual
```bash
# Executar backup manualmente
~/dashboard-suporte/backup.sh

# Ver backups
ls -la ~/dashboard-suporte/backup/
```

---

## 🔒 **CONFIGURAÇÕES DE SEGURANÇA (OPCIONAL)**

### Configurar HTTPS com Let's Encrypt
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado (substitua seu-dominio.com)
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Alterar Porta SSH (Recomendado)
```bash
sudo nano /etc/ssh/sshd_config
# Alterar: Port 22 para Port 2222
sudo systemctl restart ssh

# Atualizar firewall
sudo ufw allow 2222
sudo ufw delete allow ssh
```

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### Aplicação não inicia
```bash
# Ver logs detalhados
docker-compose -f docker-compose-vps.yml logs app

# Testar conexão com Supabase
docker-compose -f docker-compose-vps.yml exec app python3 -c "
from src.models.postgres_connection import test_postgres_connection
print('Supabase:', 'OK' if test_postgres_connection() else 'ERRO')
"
```

### Erro de conexão
```bash
# Verificar configurações
cat ~/dashboard-suporte/.env

# Testar conectividade
ping db.shfgplhdwwgdgltorren.supabase.co
```

### Nginx não funciona
```bash
# Verificar configuração
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

---

## ✅ **CHECKLIST FINAL**

- [ ] ✅ Script SQL executado no Supabase
- [ ] ✅ Arquivos enviados para VPS
- [ ] ✅ Script `setup-vps.sh` executado
- [ ] ✅ Docker containers rodando
- [ ] ✅ Usuário admin criado
- [ ] ✅ Acesso via browser funcionando
- [ ] ✅ Senha padrão alterada
- [ ] ✅ Sistema testado e funcionando

---

## 🎯 **RESUMO DOS DADOS CONFIGURADOS**

- **Supabase Host**: `db.shfgplhdwwgdgltorren.supabase.co`
- **Banco**: `postgres`
- **Usuário**: `postgres`
- **Senha**: `M@e92634664`
- **Login Admin**: `admin / 123456` (ALTERE APÓS PRIMEIRO LOGIN!)

---

**🎉 SEU DASHBOARD DE SUPORTE ESTÁ PRONTO PARA PRODUÇÃO!**

Qualquer dúvida ou problema, me avise que te ajudo a resolver! 🚀
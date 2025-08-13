# 🚀 GUIA COMPLETO DE INSTALAÇÃO - Dashboard de Suporte

## 📋 **RESUMO DO PROCESSO**

Este guia te levará do zero até ter o Dashboard funcionando 100% na sua VPS, passo a passo.

---

## 🖥️ **PARTE 1: PREPARAÇÃO LOCAL (na sua máquina)**

### 1.1 Verificar Pré-requisitos
Certifique-se de ter instalado:
- **Node.js** (versão 16+): https://nodejs.org/
- **npm** (vem com Node.js)
- **Git** (opcional)

### 1.2 Executar Script de Preparação
```bash
# No diretório do projeto
chmod +x install-local.sh
./install-local.sh
```

**O que este script faz:**
- ✅ Instala dependências do frontend
- ✅ Constrói o React para produção
- ✅ Cria arquivo comprimido para envio
- ✅ Verifica se tudo está correto

### 1.3 Resultado Esperado
Após executar, você terá:
- Arquivo `dashboard-suporte-deploy.tar.gz` criado
- Frontend construído em `src/static/`
- Tudo pronto para envio à VPS

---

## 🌐 **PARTE 2: CONFIGURAÇÃO DO SUPABASE**

### 2.1 Acessar Painel Supabase
1. Acesse: https://supabase.com/dashboard
2. Entre no seu projeto
3. Vá em **SQL Editor**

### 2.2 Executar Script SQL
1. Abra o arquivo `init-supabase.sql`
2. Copie TODO o conteúdo
3. Cole no SQL Editor do Supabase
4. Clique em **RUN**

**✅ Isso criará:**
- Todas as tabelas necessárias
- Triggers automáticos
- Tipos de tickets padrão
- Índices para performance

---

## 🖥️ **PARTE 3: CONFIGURAÇÃO DA VPS**

### 3.1 Enviar Arquivos para VPS
```bash
# Substitua USER e IP_VPS pelos seus dados
scp dashboard-suporte-deploy.tar.gz user@IP_VPS:~/
```

### 3.2 Conectar na VPS
```bash
ssh user@IP_VPS
```

### 3.3 Extrair e Configurar
```bash
# Extrair arquivos
tar -xzf dashboard-suporte-deploy.tar.gz
cd dashboard-suporte

# Executar configuração completa
chmod +x setup-vps-completo.sh
./setup-vps-completo.sh
```

**O que este script faz:**
- ✅ Instala Docker, Docker Compose, Nginx
- ✅ Configura firewall (portas 80, 443, 5000, SSH)
- ✅ Gera chave secreta forte
- ✅ Configura proxy reverso Nginx
- ✅ Cria scripts de backup e monitoramento
- ✅ Configura tarefas automáticas (cron)
- ✅ Testa conexão com Supabase

---

## 🚀 **PARTE 4: INICIAR A APLICAÇÃO**

### 4.1 Subir os Containers
```bash
# Iniciar aplicação
docker-compose -f docker-compose-vps.yml up -d

# Verificar se está rodando
docker-compose -f docker-compose-vps.yml ps
```

### 4.2 Criar Usuário Admin
```bash
# Aguardar 30 segundos para aplicação inicializar
sleep 30

# Criar admin
curl -X POST http://localhost:5000/api/auth/create-admin
```

**Resposta esperada:**
```json
{
  "message": "Admin criado com sucesso",
  "username": "admin", 
  "password": "123456"
}
```

### 4.3 Testar Aplicação
```bash
# Testar saúde
curl http://localhost:5000/api/health

# Testar login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

---

## 🌐 **PARTE 5: ACESSAR VIA BROWSER**

### 5.1 Descobrir IP da VPS
```bash
# Ver IP público
curl ifconfig.me
```

### 5.2 Acessar Sistema
- **URL**: `http://SEU_IP_VPS`
- **Login**: `admin`
- **Senha**: `123456`

### 5.3 ⚠️ ALTERAR SENHA
**IMPORTANTE**: Altere a senha padrão imediatamente após o primeiro login!

---

## 🔧 **COMANDOS ÚTEIS PARA ADMINISTRAÇÃO**

### Gerenciar Aplicação
```bash
# Ver status
docker-compose -f docker-compose-vps.yml ps

# Ver logs
docker-compose -f docker-compose-vps.yml logs -f app

# Reiniciar
docker-compose -f docker-compose-vps.yml restart app

# Parar
docker-compose -f docker-compose-vps.yml down

# Atualizar (após mudanças)
docker-compose -f docker-compose-vps.yml build --no-cache app
docker-compose -f docker-compose-vps.yml up -d app
```

### Monitoramento
```bash
# Logs do sistema
tail -f logs/monitor.log
tail -f logs/backup.log

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Uso de recursos
docker stats
htop
```

### Backup
```bash
# Backup manual
./backup.sh

# Ver backups
ls -la backup/
```

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### Aplicação não inicia
```bash
# Ver logs detalhados
docker-compose -f docker-compose-vps.yml logs app

# Verificar se portas estão livres
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80
```

### Erro de conexão Supabase
```bash
# Testar conectividade
ping db.shfgplhdwwgdgltorren.supabase.co
telnet db.shfgplhdwwgdgltorren.supabase.co 5432

# Verificar configurações
cat .env
```

### Nginx não funciona
```bash
# Testar configuração
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx

# Ver status
sudo systemctl status nginx
```

### Problemas de permissão Docker
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
exit
ssh user@IP_VPS
```

---

## ✅ **CHECKLIST FINAL**

- [ ] ✅ Script `install-local.sh` executado com sucesso
- [ ] ✅ Arquivo `dashboard-suporte-deploy.tar.gz` criado
- [ ] ✅ SQL executado no Supabase (todas as tabelas criadas)
- [ ] ✅ Arquivos enviados para VPS
- [ ] ✅ Script `setup-vps-completo.sh` executado
- [ ] ✅ Docker containers rodando
- [ ] ✅ Usuário admin criado
- [ ] ✅ Acesso via browser funcionando
- [ ] ✅ Senha padrão alterada
- [ ] ✅ Sistema testado com criação de tickets

---

## 🎯 **DADOS CONFIGURADOS**

- **Supabase Host**: `db.shfgplhdwwgdgltorren.supabase.co`
- **Banco**: `postgres`
- **Usuário**: `postgres`
- **Senha**: `M@e92634664`
- **Login Admin**: `admin / 123456` (ALTERE!)

---

## 📞 **SUPORTE**

Se encontrar problemas:

1. **Verifique os logs**: `docker-compose logs app`
2. **Teste conectividade**: `curl http://localhost:5000/api/health`
3. **Verifique Supabase**: Teste conexão manual
4. **Reinicie serviços**: `docker-compose restart`

---

**🎉 SEU DASHBOARD DE SUPORTE ESTARÁ 100% FUNCIONAL!**

Seguindo este guia passo a passo, você terá um sistema completo de gerenciamento de chamados rodando na sua VPS com backup automático, monitoramento e todas as funcionalidades! 🚀
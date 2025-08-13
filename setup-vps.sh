#!/bin/bash

# Script de configuração para VPS - Dashboard de Suporte
# Execute este script na sua VPS para configurar tudo automaticamente

set -e

echo "🚀 Configurando Dashboard de Suporte na VPS..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script não deve ser executado como root"
   exit 1
fi

# Atualizar sistema
print_status "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
print_status "Instalando dependências..."
sudo apt install -y curl git docker.io docker-compose nginx ufw

# Configurar Docker
print_status "Configurando Docker..."
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Configurar firewall
print_status "Configurando firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000  # Porta da aplicação
sudo ufw --force enable

# Criar diretórios necessários
print_status "Criando estrutura de diretórios..."
mkdir -p ~/dashboard-suporte/logs
mkdir -p ~/dashboard-suporte/src/database
mkdir -p ~/dashboard-suporte/backup

echo "🔧 Instalando dependências do frontend..."
cd frontend-src
npm install
npm run build
cd ..

# Criar diretório static se não existir

# Gerar chave secreta forte
print_status "Gerando chave secreta..."
SECRET_KEY=$(openssl rand -base64 32)
print_success "Chave secreta gerada: $SECRET_KEY"

# Criar arquivo de configuração
print_status "Criando arquivo de configuração..."
cat > ~/dashboard-suporte/.env << EOF
# Configurações de Produção - Dashboard de Suporte
SECRET_KEY=$SECRET_KEY

# PostgreSQL - Supabase (já configurado)
POSTGRES_HOST=db.shfgplhdwwgdgltorren.supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=M@e92634664

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
EOF

# Configurar Nginx (proxy reverso)
print_status "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/dashboard-suporte << EOF
server {
    listen 80;
    server_name _; # Altere para seu domínio

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /api/health {
        proxy_pass http://localhost:5000/api/health;
        access_log off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/dashboard-suporte /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Criar script de backup
print_status "Criando script de backup..."
cat > ~/dashboard-suporte/backup.sh << 'EOF'
#!/bin/bash
# Script de backup automático

BACKUP_DIR="$HOME/dashboard-suporte/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do SQLite (usuários)
cp $HOME/dashboard-suporte/src/database/app.db $BACKUP_DIR/users_$DATE.db

# Backup do PostgreSQL (se local)
# pg_dump -h localhost -U postgres dashboard_suporte > $BACKUP_DIR/postgres_$DATE.sql

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "users_*.db" -mtime +7 -delete
find $BACKUP_DIR -name "postgres_*.sql" -mtime +7 -delete

echo "Backup realizado: $DATE"
EOF

chmod +x ~/dashboard-suporte/backup.sh

# Configurar crontab para backup diário
print_status "Configurando backup automático..."
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/dashboard-suporte/backup.sh >> $HOME/dashboard-suporte/logs/backup.log 2>&1") | crontab -

# Criar script de monitoramento
cat > ~/dashboard-suporte/monitor.sh << 'EOF'
#!/bin/bash
# Script de monitoramento

LOG_FILE="$HOME/dashboard-suporte/logs/monitor.log"

# Verificar se a aplicação está respondendo
if curl -f -s http://localhost:5000/api/health > /dev/null; then
    echo "$(date): Dashboard OK" >> $LOG_FILE
else
    echo "$(date): Dashboard DOWN - Reiniciando..." >> $LOG_FILE
    cd $HOME/dashboard-suporte
    docker-compose -f docker-compose-vps.yml restart app
fi
EOF

chmod +x ~/dashboard-suporte/monitor.sh

# Configurar monitoramento a cada 5 minutos
(crontab -l 2>/dev/null; echo "*/5 * * * * $HOME/dashboard-suporte/monitor.sh") | crontab -

print_success "Configuração básica concluída!"
print_warning "PRÓXIMOS PASSOS OBRIGATÓRIOS:"
echo ""
echo "1. 📝 CONFIGURE O POSTGRESQL:"
echo "   - Edite o arquivo: ~/dashboard-suporte/.env"
echo "   - Altere POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD"
echo ""
echo "2. 🗄️ EXECUTE O SCRIPT SQL:"
echo "   - Use o arquivo init-db-production.sql no seu PostgreSQL"
echo "   - Ou init-db.sql se quiser dados de exemplo"
echo ""
echo "3. 🚀 INICIE A APLICAÇÃO:"
echo "   cd ~/dashboard-suporte"
echo "   docker-compose -f docker-compose-vps.yml up -d"
echo ""
echo "4. 👤 CRIE O USUÁRIO ADMIN:"
echo "   curl -X POST http://localhost:5000/api/auth/create-admin"
echo ""
echo "5. 🌐 ACESSE:"
echo "   http://SEU_IP_VPS"
echo "   Login: admin / Senha: 123456"
echo ""
print_warning "⚠️  ALTERE A SENHA PADRÃO APÓS O PRIMEIRO LOGIN!"
echo ""
print_success "Script de configuração finalizado! 🎉"
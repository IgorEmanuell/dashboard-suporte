#!/bin/bash

# Script COMPLETO de configuração para VPS - Dashboard de Suporte
# Execute este script NA SUA VPS após extrair os arquivos

set -e

echo "🚀 Configurando Dashboard de Suporte na VPS..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Atualizar sistema
print_status "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
print_status "Instalando dependências básicas..."
sudo apt install -y curl git wget unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Instalar Docker
if ! command_exists docker; then
    print_status "Instalando Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    print_success "Docker instalado!"
else
    print_success "Docker já está instalado"
fi

# Instalar Docker Compose
if ! command_exists docker-compose; then
    print_status "Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado!"
else
    print_success "Docker Compose já está instalado"
fi

# Instalar Nginx
if ! command_exists nginx; then
    print_status "Instalando Nginx..."
    sudo apt install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    print_success "Nginx instalado!"
else
    print_success "Nginx já está instalado"
fi

# Configurar firewall
print_status "Configurando firewall..."
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable
print_success "Firewall configurado!"

# Criar diretórios necessários
print_status "Criando estrutura de diretórios..."
mkdir -p logs
mkdir -p src/database
mkdir -p backup

# Gerar chave secreta forte
print_status "Gerando chave secreta..."
SECRET_KEY=$(openssl rand -base64 32)

# Criar arquivo de configuração .env
print_status "Criando arquivo de configuração..."
cat > .env << EOF
# Configurações de Produção - Dashboard de Suporte
SECRET_KEY=$SECRET_KEY

# PostgreSQL - Supabase
POSTGRES_HOST=db.shfgplhdwwgdgltorren.supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=M@e92634664

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
EOF

print_success "Arquivo .env criado com chave secreta: $SECRET_KEY"

# Configurar Nginx (proxy reverso)
print_status "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/dashboard-suporte << 'EOF'
server {
    listen 80;
    server_name _;

    # Aumentar tamanho máximo de upload
    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket support (se necessário no futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /api/health {
        proxy_pass http://localhost:5000/api/health;
        access_log off;
    }

    # Servir arquivos estáticos diretamente (otimização)
    location /static/ {
        proxy_pass http://localhost:5000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/dashboard-suporte /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
print_success "Nginx configurado!"

# Criar script de backup
print_status "Criando script de backup..."
cat > backup.sh << 'EOF'
#!/bin/bash
# Script de backup automático

BACKUP_DIR="$HOME/dashboard-suporte/backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "$(date): Iniciando backup..." >> logs/backup.log

# Backup do SQLite (usuários)
if [ -f "src/database/app.db" ]; then
    cp src/database/app.db $BACKUP_DIR/users_$DATE.db
    echo "$(date): Backup SQLite realizado" >> logs/backup.log
fi

# Backup de configurações
cp .env $BACKUP_DIR/env_$DATE.backup
cp docker-compose-vps.yml $BACKUP_DIR/docker-compose_$DATE.yml

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "users_*.db" -mtime +7 -delete
find $BACKUP_DIR -name "env_*.backup" -mtime +7 -delete
find $BACKUP_DIR -name "docker-compose_*.yml" -mtime +7 -delete

echo "$(date): Backup concluído - $DATE" >> logs/backup.log
EOF

chmod +x backup.sh
print_success "Script de backup criado!"

# Criar script de monitoramento
print_status "Criando script de monitoramento..."
cat > monitor.sh << 'EOF'
#!/bin/bash
# Script de monitoramento

LOG_FILE="logs/monitor.log"

# Verificar se a aplicação está respondendo
if curl -f -s http://localhost:5000/api/health > /dev/null; then
    echo "$(date): Dashboard OK" >> $LOG_FILE
else
    echo "$(date): Dashboard DOWN - Reiniciando..." >> $LOG_FILE
    docker-compose -f docker-compose-vps.yml restart app
    sleep 10
    if curl -f -s http://localhost:5000/api/health > /dev/null; then
        echo "$(date): Dashboard reiniciado com sucesso" >> $LOG_FILE
    else
        echo "$(date): ERRO: Dashboard não respondeu após reinicialização" >> $LOG_FILE
    fi
fi

# Verificar uso de disco
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "$(date): ALERTA: Uso de disco alto: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Verificar uso de memória
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 85 ]; then
    echo "$(date): ALERTA: Uso de memória alto: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x monitor.sh
print_success "Script de monitoramento criado!"

# Configurar crontab
print_status "Configurando tarefas automáticas..."
# Backup diário às 2h
(crontab -l 2>/dev/null; echo "0 2 * * * cd $PWD && ./backup.sh") | crontab -
# Monitoramento a cada 5 minutos
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $PWD && ./monitor.sh") | crontab -
print_success "Crontab configurado!"

# Testar conexão com Supabase
print_status "Testando conexão com Supabase..."
if command_exists python3; then
    python3 -c "
import socket
try:
    socket.create_connection(('db.shfgplhdwwgdgltorren.supabase.co', 5432), timeout=10)
    print('✅ Conexão com Supabase OK!')
except:
    print('❌ Erro na conexão com Supabase')
"
fi

print_success "Configuração da VPS concluída!"
echo ""
print_warning "PRÓXIMOS PASSOS:"
echo ""
echo "1. 🗄️ CONFIGURE O SUPABASE:"
echo "   - Acesse: https://supabase.com/dashboard"
echo "   - Execute o SQL do arquivo: init-supabase.sql"
echo ""
echo "2. 🚀 INICIE A APLICAÇÃO:"
echo "   docker-compose -f docker-compose-vps.yml up -d"
echo ""
echo "3. 👤 CRIE O USUÁRIO ADMIN:"
echo "   curl -X POST http://localhost:5000/api/auth/create-admin"
echo ""
echo "4. 🌐 ACESSE O SISTEMA:"
echo "   http://$(curl -s ifconfig.me)"
echo "   Login: admin / Senha: 123456"
echo ""
print_warning "⚠️  ALTERE A SENHA PADRÃO APÓS O PRIMEIRO LOGIN!"
echo ""
print_success "VPS configurada e pronta para uso! 🎉"
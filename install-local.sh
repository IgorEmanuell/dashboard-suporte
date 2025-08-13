#!/bin/bash

# Script de instalação local - Execute ANTES de enviar para VPS
# Este script prepara tudo na sua máquina local

set -e

echo "🚀 Preparando Dashboard de Suporte para deploy..."

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

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    print_error "Node.js não encontrado. Instale Node.js primeiro:"
    echo "https://nodejs.org/"
    exit 1
fi

# Verificar se npm está instalado
if ! command -v npm &> /dev/null; then
    print_error "npm não encontrado. Instale npm primeiro"
    exit 1
fi

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Construir frontend
print_status "Construindo frontend React..."
cd frontend-src

print_status "Instalando dependências do frontend..."
npm install

print_status "Fazendo build do frontend..."
npm run build

cd ..
print_success "Frontend construído com sucesso!"

# Verificar se o build foi criado
if [ ! -d "src/static" ]; then
    print_error "Erro: Diretório src/static não foi criado!"
    exit 1
fi

if [ ! -f "src/static/index.html" ]; then
    print_error "Erro: index.html não foi gerado!"
    exit 1
fi

print_success "Arquivos estáticos gerados em src/static/"

# Criar arquivo comprimido para envio
print_status "Criando arquivo comprimido para envio..."
tar -czf dashboard-suporte-deploy.tar.gz \
    --exclude=node_modules \
    --exclude=frontend-src/node_modules \
    --exclude=frontend-src/dist \
    --exclude=.git \
    --exclude=*.log \
    --exclude=__pycache__ \
    .

print_success "Arquivo dashboard-suporte-deploy.tar.gz criado!"

echo ""
print_success "✅ PREPARAÇÃO CONCLUÍDA!"
echo ""
print_warning "PRÓXIMOS PASSOS:"
echo "1. Envie o arquivo para sua VPS:"
echo "   scp dashboard-suporte-deploy.tar.gz user@SEU_IP_VPS:~/"
echo ""
echo "2. Conecte na VPS e execute:"
echo "   ssh user@SEU_IP_VPS"
echo "   tar -xzf dashboard-suporte-deploy.tar.gz"
echo "   cd dashboard-suporte"
echo "   chmod +x setup-vps.sh"
echo "   ./setup-vps.sh"
echo ""
echo "3. Configure o Supabase executando o SQL:"
echo "   Arquivo: init-supabase.sql"
echo ""
print_success "Tudo pronto para deploy! 🚀"
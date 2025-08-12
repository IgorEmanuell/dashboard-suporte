FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Criar diretórios necessários
RUN mkdir -p src/database logs

# Criar script de entrada simplificado para VPS
RUN cat > /usr/local/bin/docker-entrypoint.sh << 'EOF' && chmod +x /usr/local/bin/docker-entrypoint.sh
#!/bin/bash
set -e

echo "🚀 Iniciando Dashboard de Suporte..."

# Criar usuário admin automaticamente se não existir
echo "📝 Verificando usuário admin..."
python3 -c "
import os, sys
sys.path.insert(0, '/app')
from src.main import app
from src.models.user import db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@dashboard.com', role='admin')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuário admin criado: admin/123456')
    else:
        print('✅ Usuário admin já existe')
" 2>/dev/null || echo "⚠️  Erro ao criar admin - será criado via API"

echo "🎯 Iniciando aplicação..."
exec "\$@"
EOF

ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "src/main.py"]



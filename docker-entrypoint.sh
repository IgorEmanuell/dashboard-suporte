#!/bin/bash

set -e

# Função para esperar o PostgreSQL estar pronto
wait_for_postgres() {
  echo "Aguardando o PostgreSQL em $POSTGRES_HOST:$POSTGRES_PORT..."
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\q"; do
    >&2 echo "Postgres não está disponível - dormindo"
    sleep 1
  done
  >&2 echo "Postgres está disponível - executando comandos"
}

# Executar o script de espera
wait_for_postgres

# Executar o script SQL de inicialização do banco de dados
# O script init-db-production.sql já está copiado para /docker-entrypoint-initdb.d/
# Usamos o psql para executar o script no banco externo
echo "Executando init-db-production.sql no PostgreSQL..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init-db-production.sql
echo "init-db-production.sql executado com sucesso."

# Criar o usuário admin no SQLite
# O script create_admin_user_auto.py será criado e executado aqui

# Criar o script Python para criação automática do admin
cat <<EOF > /app/create_admin_user_auto.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db, User

with app.app_context():
    username = "admin"
    email = "emanuelligor@hotmail.com"
    password = "M@e92634664"

    existing_admin = User.query.filter_by(username=username).first()
    if not existing_admin:
        admin = User(
            username=username,
            email=email,
            role=\'admin\'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Usuário admin '{username}' criado com sucesso!")
    else:
        print(f"Usuário admin '{username}' já existe. Verificando senha...")
        # Opcional: Atualizar senha se for diferente, mas para simplicidade, apenas verifica
        if not existing_admin.check_password(password):
            existing_admin.set_password(password)
            db.session.add(existing_admin)
            db.session.commit()
            print(f"Senha do usuário admin '{username}' atualizada com sucesso!")
        else:
            print(f"Senha do usuário admin '{username}' já está correta.")

EOF

echo "Criando/verificando usuário admin no SQLite..."
python /app/create_admin_user_auto.py
echo "Usuário admin configurado."

# Remover o script de criação automática do admin após a execução
rm /app/create_admin_user_auto.py

# Executar o comando original da aplicação (CMD do Dockerfile)
exec "$@"



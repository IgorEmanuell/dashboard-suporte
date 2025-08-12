# 🚀 Dashboard de Suporte - Guia de Produção

## 📋 Visão Geral

Este guia fornece instruções completas para colocar o Dashboard de Suporte em produção, garantindo que o sistema funcione com dados reais do seu banco PostgreSQL (Supabase) e autenticação segura via SQLite.

## ⚠️ IMPORTANTE - Diferenças da Versão de Produção

Esta versão foi especificamente configurada para **PRODUÇÃO REAL**, removendo todos os elementos de teste:

- ❌ **Removido**: Credenciais de teste na tela de login
- ❌ **Removido**: Dados de exemplo/tickets fictícios
- ❌ **Removido**: Autenticação simulada
- ✅ **Adicionado**: Autenticação real via API
- ✅ **Adicionado**: Integração completa com PostgreSQL
- ✅ **Adicionado**: Sistema de gerenciamento de usuários
- ✅ **Adicionado**: Script SQL limpo para produção

## 🗄️ Configuração do Banco de Dados

### 1. PostgreSQL (Supabase) - Dados Operacionais

Execute o script `init-db-production.sql` no seu banco Supabase:

```sql
-- Este script cria APENAS a estrutura, SEM dados de exemplo
-- Conecte-se ao seu Supabase e execute:
```

**Importante**: Use o arquivo `init-db-production.sql` que **NÃO** contém dados de exemplo, apenas a estrutura das tabelas.

### 2. SQLite - Autenticação de Usuários

O banco SQLite é criado automaticamente na primeira execução do container da aplicação. O usuário admin será criado automaticamente com as credenciais pré-definidas no `docker-entrypoint.sh`.

## 🐳 Implantação com Docker

### 1. Preparação

Certifique-se de que você tem:
- Docker e Docker Compose instalados
- Acesso ao seu banco Supabase
- As credenciais corretas do banco

### 2. Configuração de Produção

Use o arquivo `docker-compose-production.yml`:

```bash
# Subir a aplicação (isso irá construir a imagem, criar o admin e as tabelas no PostgreSQL)
docker-compose -f docker-compose-production.yml up -d --build
```

### 3. Variáveis de Ambiente Importantes

**⚠️ ALTERE OBRIGATORIAMENTE:**

```yaml
environment:
  # MUDE ESTA CHAVE PARA UMA CHAVE FORTE E ÚNICA!
  - SECRET_KEY=sua-chave-secreta-muito-forte-e-unica-aqui-mude-isso
```

**Credenciais do Banco (já configuradas):**
```yaml
  - POSTGRES_HOST=aws-0-sa-east-1.pooler.supabase.com
  - POSTGRES_PORT=6543
  - POSTGRES_DB=postgres
  - POSTGRES_USER=postgres.daxajqrcpearkcsheeol
  - POSTGRES_PASSWORD=M@e92634664
```

## 👤 Gerenciamento de Usuários

### 1. Usuário Admin Inicial

O usuário admin com email `emanuelligor@hotmail.com` e senha `M@e92634664` será criado automaticamente na primeira inicialização do container da aplicação. Você pode usar essas credenciais para o primeiro login.

### 2. Alterando a Senha do Admin ou Criando Novos Usuários

Para alterar a senha do admin ou criar novos usuários, você precisará acessar o shell do container da aplicação e usar um script Python. **Não há uma interface web para isso por padrão para manter a simplicidade e segurança.**

```bash
# Acessar o shell do container da aplicação
docker exec -it <nome_do_container_da_app> bash

# Exemplo: Para alterar a senha do admin (substitua <nome_do_container_da_app> pelo nome real do seu container, ex: dashboard-suporte-app-1)
# Dentro do container, execute comandos Python para interagir com o banco SQLite
python3 -c "from src.main import app; from src.models.user import db, User; with app.app_context(): user = User.query.filter_by(username=\'admin\').first(); user.set_password(\'SUA_NOVA_SENHA_FORTE\'); db.session.add(user); db.session.commit(); print(\'Senha alterada!\')"

# Exemplo: Para criar um novo usuário (dentro do container)
python3 -c "from src.main import app; from src.models.user import db, User; with app.app_context(): user = User(username=\'novo_usuario\', email=\'novo@email.com\', role=\'support\'); user.set_password(\'senha_do_novo_usuario\'); db.session.add(user); db.session.commit(); print(\'Usuário criado!\')"
```

**Importante**: O script `create_admin_user.py` foi removido, pois a criação inicial do admin é agora automática. Para gerenciamento posterior, use os comandos Python diretamente no shell do container, conforme os exemplos acima.

## 🔐 Segurança em Produção

### 1. Chave Secreta

**OBRIGATÓRIO**: Altere a `SECRET_KEY` no `docker-compose-production.yml`:

```bash
# Gerar uma chave forte
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Firewall e Acesso

- Configure firewall para permitir apenas as portas necessárias
- Use HTTPS em produção (configure um proxy reverso como Nginx)
- Considere usar VPN para acesso administrativo

### 3. Backup

Configure backup regular do:
- Banco PostgreSQL (Supabase já faz isso)
- Arquivo SQLite de usuários (`src/database/app.db`)

## 📊 Verificação de Funcionamento

### 1. Saúde da Aplicação

```bash
# Verificar se a aplicação está respondendo
curl http://localhost:5000/api/health
```

### 2. Logs da Aplicação

```bash
# Ver logs em tempo real
docker-compose -f docker-compose-production.yml logs -f app
```

### 3. Teste de Login

1. Acesse http://localhost:5000
2. Use as credenciais pré-definidas (`emanuelligor@hotmail.com` / `M@e92634664`)
3. Verifique se os dados vêm do banco PostgreSQL

## 🔧 Solução de Problemas

### Problema: "Credenciais inválidas"

**Causa**: Senha incorreta ou usuário não foi criado (verifique os logs do container)
**Solução**: Verifique as credenciais. Se o problema persistir, acesse o container e crie o usuário manualmente conforme as instruções de gerenciamento de usuários.

### Problema: "Erro de conexão com banco"

**Causa**: Credenciais do PostgreSQL incorretas ou banco inacessível
**Solução**: Verifique as variáveis de ambiente no `docker-compose-production.yml` e a conectividade com seu Supabase.

### Problema: Dados não aparecem

**Causa**: Tabelas não foram criadas no PostgreSQL
**Solução**: Verifique os logs do container durante a inicialização para ver se o `init-db-production.sql` foi executado sem erros.

### Problema: Token inválido/expirado

**Causa**: Chave secreta mudou ou token expirou
**Solução**: Faça logout e login novamente

## 📈 Monitoramento

### 1. Logs Importantes

Monitore os logs para:
- Erros de autenticação
- Falhas de conexão com banco
- Erros de aplicação

### 2. Métricas de Uso

A aplicação registra automaticamente:
- Histórico de mudanças em tickets
- Logs de login/logout
- Estatísticas de resolução

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
# Parar os serviços
docker-compose -f docker-compose-production.yml down

# Atualizar código (se necessário)
git pull

# Reconstruir e subir
docker-compose -f docker-compose-production.yml up -d --build
```

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs da aplicação
2. Confirme se o banco PostgreSQL está acessível
3. Verifique se o usuário admin foi criado corretamente
4. Teste a conectividade de rede

---

**✅ Sistema Pronto para Produção!**

Após seguir este guia, seu Dashboard de Suporte estará funcionando com:
- Dados reais do PostgreSQL
- Autenticação segura
- Interface limpa sem referências de teste
- Gerenciamento completo de usuários


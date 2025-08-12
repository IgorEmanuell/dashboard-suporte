-- Script de inicialização do banco PostgreSQL para Dashboard de Suporte - PRODUÇÃO
-- Este script cria todas as tabelas e estrutura necessária SEM dados de exemplo

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de tipos de tickets
CREATE TABLE IF NOT EXISTS ticket_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela principal de tickets
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    type_id INTEGER REFERENCES ticket_types(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requester VARCHAR(255) NOT NULL,
    requester_email VARCHAR(255),
    urgency VARCHAR(20) DEFAULT 'medium' CHECK (urgency IN ('low', 'medium', 'high')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    resolution TEXT,
    tags TEXT[]
);

-- Tabela de histórico de tickets
CREATE TABLE IF NOT EXISTS ticket_history (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Tabela de comentários
CREATE TABLE IF NOT EXISTS ticket_comments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_internal BOOLEAN DEFAULT FALSE
);

-- Tabela de anexos
CREATE TABLE IF NOT EXISTS ticket_attachments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Função para gerar número do ticket automaticamente
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
DECLARE
    year_suffix VARCHAR(4);
    sequence_num INTEGER;
    new_number VARCHAR(20);
BEGIN
    -- Pegar os últimos 2 dígitos do ano
    year_suffix := RIGHT(EXTRACT(YEAR FROM CURRENT_DATE)::TEXT, 2);
    
    -- Buscar o próximo número sequencial para o ano
    SELECT COALESCE(MAX(CAST(SUBSTRING(ticket_number FROM 4) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM tickets
    WHERE ticket_number LIKE 'TK' || year_suffix || '%';
    
    -- Gerar o número com padding de zeros
    new_number := 'TK' || year_suffix || LPAD(sequence_num::TEXT, 4, '0');
    
    NEW.ticket_number := new_number;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para gerar número do ticket
DROP TRIGGER IF EXISTS trigger_generate_ticket_number ON tickets;
CREATE TRIGGER trigger_generate_ticket_number
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION generate_ticket_number();

-- Função para atualizar timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS trigger_update_tickets_updated_at ON tickets;
CREATE TRIGGER trigger_update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Função para registrar histórico automaticamente
CREATE OR REPLACE FUNCTION log_ticket_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log para INSERT
    IF TG_OP = 'INSERT' THEN
        INSERT INTO ticket_history (ticket_id, action, changed_by, notes)
        VALUES (NEW.id, 'created', NEW.created_by, 'Ticket criado');
        RETURN NEW;
    END IF;
    
    -- Log para UPDATE
    IF TG_OP = 'UPDATE' THEN
        -- Status mudou
        IF OLD.status != NEW.status THEN
            INSERT INTO ticket_history (ticket_id, action, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'status_changed', 'status', OLD.status, NEW.status, NEW.updated_by);
        END IF;
        
        -- Urgência mudou
        IF OLD.urgency != NEW.urgency THEN
            INSERT INTO ticket_history (ticket_id, action, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'urgency_changed', 'urgency', OLD.urgency, NEW.urgency, NEW.updated_by);
        END IF;
        
        -- Atribuição mudou
        IF COALESCE(OLD.assigned_to, '') != COALESCE(NEW.assigned_to, '') THEN
            INSERT INTO ticket_history (ticket_id, action, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'assigned', 'assigned_to', OLD.assigned_to, NEW.assigned_to, NEW.updated_by);
        END IF;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para log de mudanças
DROP TRIGGER IF EXISTS trigger_log_ticket_changes ON tickets;
CREATE TRIGGER trigger_log_ticket_changes
    AFTER INSERT OR UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION log_ticket_changes();

-- Inserir tipos de tickets padrão (APENAS OS TIPOS, SEM TICKETS DE EXEMPLO)
INSERT INTO ticket_types (name, description, color) VALUES
('Hardware', 'Problemas relacionados a equipamentos físicos', '#EF4444'),
('Software', 'Problemas com aplicativos e sistemas', '#3B82F6'),
('Rede', 'Problemas de conectividade e rede', '#10B981'),
('Sistema', 'Problemas com sistema operacional', '#F59E0B'),
('Impressora', 'Problemas com impressoras e periféricos', '#8B5CF6'),
('Email', 'Problemas com email e comunicação', '#06B6D4'),
('Telefonia', 'Problemas com telefones e VOIP', '#84CC16'),
('Acesso', 'Problemas de login e permissões', '#F97316'),
('Backup', 'Problemas com backup e recuperação', '#6366F1'),
('Outros', 'Outros tipos de solicitações', '#6B7280')
ON CONFLICT (name) DO NOTHING;

-- REMOVIDO: Inserção de tickets de exemplo para produção limpa

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_urgency ON tickets(urgency);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_type_id ON tickets(type_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_ticket_history_ticket_id ON ticket_history(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_id ON ticket_comments(ticket_id);

-- Views úteis para relatórios
CREATE OR REPLACE VIEW v_tickets_summary AS
SELECT 
    t.id,
    t.ticket_number,
    t.title,
    t.description,
    t.requester,
    t.urgency,
    t.status,
    t.created_at,
    t.completed_at,
    tt.name as type_name,
    tt.color as type_color,
    CASE 
        WHEN t.completed_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (t.completed_at - t.created_at))/3600
        ELSE 
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.created_at))/3600
    END as hours_elapsed
FROM tickets t
LEFT JOIN ticket_types tt ON t.type_id = tt.id;

-- View para estatísticas
CREATE OR REPLACE VIEW v_ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_tickets,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tickets,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_tickets,
    COUNT(*) FILTER (WHERE urgency = 'high') as high_urgency,
    COUNT(*) FILTER (WHERE urgency = 'medium') as medium_urgency,
    COUNT(*) FILTER (WHERE urgency = 'low') as low_urgency,
    COUNT(*) FILTER (WHERE DATE(completed_at) = CURRENT_DATE) as completed_today,
    AVG(CASE 
        WHEN completed_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (completed_at - created_at))/3600
    END) as avg_resolution_hours
FROM tickets;

-- Comentários nas tabelas para documentação
COMMENT ON TABLE tickets IS 'Tabela principal de tickets de suporte';
COMMENT ON TABLE ticket_types IS 'Tipos/categorias de tickets disponíveis';
COMMENT ON TABLE ticket_history IS 'Histórico de mudanças nos tickets';
COMMENT ON TABLE ticket_comments IS 'Comentários adicionados aos tickets';
COMMENT ON TABLE ticket_attachments IS 'Arquivos anexados aos tickets';

COMMENT ON COLUMN tickets.ticket_number IS 'Número único do ticket no formato TKYY#### (ex: TK240001)';
COMMENT ON COLUMN tickets.urgency IS 'Nível de urgência: low, medium, high';
COMMENT ON COLUMN tickets.status IS 'Status atual: pending, in_progress, completed, cancelled';
COMMENT ON COLUMN tickets.priority IS 'Prioridade numérica de 1 (mais alta) a 5 (mais baixa)';

-- Conceder permissões (ajuste conforme necessário)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dashboard_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dashboard_user;


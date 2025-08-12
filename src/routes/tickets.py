from flask import Blueprint, request, jsonify
from src.models.postgres_connection import get_postgres_connection
from src.routes.auth import token_required
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/', methods=['GET'])
@token_required
def get_tickets(current_user):
    """Busca todos os tickets"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, tt.name as type_name 
                FROM tickets t 
                LEFT JOIN ticket_types tt ON t.type_id = tt.id 
                ORDER BY 
                    CASE t.urgency 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    t.created_at DESC
            """)
            tickets = cursor.fetchall()
            
            # Converter para lista de dicionários
            result = []
            for ticket in tickets:
                ticket_dict = dict(ticket)
                # Converter datetime para string ISO
                if ticket_dict.get('created_at'):
                    ticket_dict['created_at'] = ticket_dict['created_at'].isoformat()
                if ticket_dict.get('completed_at'):
                    ticket_dict['completed_at'] = ticket_dict['completed_at'].isoformat()
                result.append(ticket_dict)
            
            return jsonify(result), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar tickets: {str(e)}'}), 500

@tickets_bp.route('/', methods=['POST'])
@token_required
def create_ticket(current_user):
    """Cria um novo ticket"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['type', 'description', 'requester']):
            return jsonify({'message': 'Campos obrigatórios: type, description, requester'}), 400
        
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            # Buscar type_id
            cursor.execute("SELECT id FROM ticket_types WHERE name = %s", (data['type'],))
            type_result = cursor.fetchone()
            if not type_result:
                return jsonify({'message': 'Tipo de ticket inválido'}), 400
            
            # Inserir novo ticket
            cursor.execute("""
                INSERT INTO tickets (type_id, description, requester, urgency, status, created_by)
                VALUES (%s, %s, %s, %s, 'pending', %s)
                RETURNING *
            """, (
                type_result['id'], 
                data['description'], 
                data['requester'], 
                data.get('urgency', 'medium'),
                current_user.username
            ))
            
            new_ticket = cursor.fetchone()
            conn.commit()
            
            # Converter datetime para string
            ticket_dict = dict(new_ticket)
            if ticket_dict.get('created_at'):
                ticket_dict['created_at'] = ticket_dict['created_at'].isoformat()
            
            return jsonify(ticket_dict), 201
            
    except Exception as e:
        return jsonify({'message': f'Erro ao criar ticket: {str(e)}'}), 500

@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@token_required
def update_ticket(current_user, ticket_id):
    """Atualiza um ticket"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query dinamicamente
            update_fields = []
            values = []
            
            if 'urgency' in data:
                update_fields.append("urgency = %s")
                values.append(data['urgency'])
            
            if 'status' in data:
                update_fields.append("status = %s")
                values.append(data['status'])
                if data['status'] == 'completed':
                    update_fields.append("completed_at = %s")
                    values.append(datetime.utcnow())
            
            if 'description' in data:
                update_fields.append("description = %s")
                values.append(data['description'])
            
            if not update_fields:
                return jsonify({'message': 'Nenhum campo para atualizar'}), 400
            
            # Adicionar campos de auditoria
            update_fields.append("updated_at = %s")
            update_fields.append("updated_by = %s")
            values.extend([datetime.utcnow(), current_user.username])
            
            values.append(ticket_id)
            query = f"UPDATE tickets SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            
            cursor.execute(query, values)
            updated_ticket = cursor.fetchone()
            
            if not updated_ticket:
                return jsonify({'message': 'Ticket não encontrado'}), 404
            
            conn.commit()
            
            # Converter datetime para string
            ticket_dict = dict(updated_ticket)
            for field in ['created_at', 'completed_at', 'updated_at']:
                if ticket_dict.get(field):
                    ticket_dict[field] = ticket_dict[field].isoformat()
            
            return jsonify(ticket_dict), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao atualizar ticket: {str(e)}'}), 500

@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@token_required
def delete_ticket(current_user, ticket_id):
    """Deleta um ticket (apenas admins)"""
    try:
        if current_user.role != 'admin':
            return jsonify({'message': 'Acesso negado'}), 403
        
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tickets WHERE id = %s RETURNING id", (ticket_id,))
            deleted = cursor.fetchone()
            
            if not deleted:
                return jsonify({'message': 'Ticket não encontrado'}), 404
            
            conn.commit()
            return jsonify({'message': 'Ticket deletado com sucesso'}), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao deletar ticket: {str(e)}'}), 500

@tickets_bp.route('/types', methods=['GET'])
@token_required
def get_ticket_types(current_user):
    """Busca tipos de tickets disponíveis"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ticket_types ORDER BY name")
            types = cursor.fetchall()
            
            return jsonify([dict(t) for t in types]), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar tipos: {str(e)}'}), 500


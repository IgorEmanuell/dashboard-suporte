from flask import Blueprint, jsonify
from src.models.postgres_connection import get_postgres_connection
from src.routes.auth import token_required

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/', methods=['GET'])
@token_required
def get_stats(current_user):
    """Busca estatísticas do dashboard"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            # Tickets pendentes
            cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'pending'")
            pending_count = cursor.fetchone()['count']
            
            # Tickets finalizados hoje
            cursor.execute("""
                SELECT COUNT(*) as count FROM tickets 
                WHERE status = 'completed' AND DATE(completed_at) = CURRENT_DATE
            """)
            completed_today = cursor.fetchone()['count']
            
            # Tickets por urgência (apenas pendentes)
            cursor.execute("""
                SELECT urgency, COUNT(*) as count 
                FROM tickets 
                WHERE status = 'pending' 
                GROUP BY urgency
            """)
            urgency_results = cursor.fetchall()
            urgency_stats = {row['urgency']: row['count'] for row in urgency_results}
            
            # Total de tickets
            cursor.execute("SELECT COUNT(*) as count FROM tickets")
            total_tickets = cursor.fetchone()['count']
            
            # Tickets por status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                GROUP BY status
            """)
            status_results = cursor.fetchall()
            status_stats = {row['status']: row['count'] for row in status_results}
            
            # Tickets por tipo
            cursor.execute("""
                SELECT tt.name, COUNT(t.id) as count 
                FROM ticket_types tt 
                LEFT JOIN tickets t ON tt.id = t.type_id 
                GROUP BY tt.id, tt.name
                ORDER BY count DESC
            """)
            type_results = cursor.fetchall()
            type_stats = [{'type': row['name'], 'count': row['count']} for row in type_results]
            
            # Estatísticas por período (últimos 7 dias)
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM tickets 
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            daily_results = cursor.fetchall()
            daily_stats = [{'date': row['date'].isoformat(), 'count': row['count']} for row in daily_results]
            
            return jsonify({
                'pending': pending_count,
                'completed_today': completed_today,
                'total': total_tickets,
                'urgency': {
                    'low': urgency_stats.get('low', 0),
                    'medium': urgency_stats.get('medium', 0),
                    'high': urgency_stats.get('high', 0)
                },
                'status': status_stats,
                'by_type': type_stats,
                'daily_last_week': daily_stats
            }), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar estatísticas: {str(e)}'}), 500

@stats_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Estatísticas simplificadas para o dashboard principal"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            # Tickets pendentes
            cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'pending'")
            pending = cursor.fetchone()['count']
            
            # Finalizados hoje
            cursor.execute("""
                SELECT COUNT(*) as count FROM tickets 
                WHERE status = 'completed' AND DATE(completed_at) = CURRENT_DATE
            """)
            completed_today = cursor.fetchone()['count']
            
            # Por urgência (apenas pendentes)
            cursor.execute("""
                SELECT urgency, COUNT(*) as count 
                FROM tickets 
                WHERE status = 'pending' 
                GROUP BY urgency
            """)
            urgency_results = cursor.fetchall()
            urgency = {row['urgency']: row['count'] for row in urgency_results}
            
            return jsonify({
                'pending': pending,
                'completed_today': completed_today,
                'urgency': {
                    'low': urgency.get('low', 0),
                    'medium': urgency.get('medium', 0),
                    'high': urgency.get('high', 0)
                }
            }), 200
            
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar estatísticas: {str(e)}'}), 500


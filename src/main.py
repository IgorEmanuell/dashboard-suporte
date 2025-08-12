import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.tickets import tickets_bp
from src.routes.stats import stats_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configurar CORS
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
app.register_blueprint(stats_bp, url_prefix='/api/stats')

# Configuração do SQLite para autenticação
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do PostgreSQL para dados
app.config['POSTGRES_HOST'] = os.environ.get('POSTGRES_HOST', 'localhost')
app.config['POSTGRES_PORT'] = os.environ.get('POSTGRES_PORT', '5432')
app.config['POSTGRES_DB'] = os.environ.get('POSTGRES_DB', 'dashboard_suporte')
app.config['POSTGRES_USER'] = os.environ.get('POSTGRES_USER', 'postgres')
app.config['POSTGRES_PASSWORD'] = os.environ.get('POSTGRES_PASSWORD', 'password')

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


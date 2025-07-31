from flask import Blueprint, jsonify
from datetime import datetime

# Criar blueprint para rotas de health check
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde"""
    return jsonify({
        'status': 'ok',
        'message': 'Video Processing API is running',
        'timestamp': datetime.now().isoformat()
    })
# Inicialização do pacote routes
from app.routes.video_routes import video_bp
from app.routes.health_routes import health_bp

# Exportar blueprints
__all__ = ['video_bp', 'health_bp']
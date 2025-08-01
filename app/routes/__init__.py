# Inicialização do pacote routes
from app.routes.health_routes import router as health_router
from app.routes.video_routes import router as video_router

# Exportar routers
__all__ = ['health_router', 'video_router']
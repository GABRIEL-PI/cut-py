from flask import Flask
from app.routes.video_routes import video_bp
from app.routes.health_routes import health_bp

def create_app():
    """
    Cria e configura a aplicação Flask
    
    Returns:
        Flask: Aplicação Flask configurada
    """
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # Registrar blueprints
    app.register_blueprint(video_bp)
    app.register_blueprint(health_bp)
    
    return app

# Criar instância da aplicação
app = create_app()
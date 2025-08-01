from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.video_routes import router as video_router
from app.routes.health_routes import router as health_router
from app.jobs.cookie_update_job import CookieUpdateJob

def create_app():
    """
    Cria e configura a aplicação FastAPI
    
    Returns:
        FastAPI: Aplicação FastAPI configurada
    """
    # Criar aplicação FastAPI
    app = FastAPI(title="Video Processing API")
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(video_router)
    app.include_router(health_router)
    
    # Iniciar job de atualização de cookies
    @app.on_event("startup")
    def start_cookie_update_job():
        cookie_job = CookieUpdateJob()
        cookie_job.start()
    
    return app

# Criar instância da aplicação
app = create_app()
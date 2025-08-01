from fastapi import APIRouter
from datetime import datetime
import pytz
from app.models.video_models import HealthResponse

# Criar router para rotas de health check
router = APIRouter(tags=["Health"])

@router.get('/health', response_model=HealthResponse)
def health():
    """Endpoint de verificação de saúde"""
    return {
        'status': 'ok',
        'message': 'Video Processing API is running',
        'timestamp': datetime.now().isoformat()
    }
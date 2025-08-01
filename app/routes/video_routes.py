from fastapi import APIRouter, Path, Query
from typing import Optional, List
from app.controllers.video_controller import VideoController
from app.models.video_models import VideoDownloadRequest, VideoCutRequest, DownloadAndCutRequest

# Criar router para rotas de vídeo
router = APIRouter(prefix="/videos", tags=["Videos"])

# Instanciar controlador
video_controller = VideoController()

# Definir rotas - Rotas específicas primeiro
@router.post('')
async def download_video(request: VideoDownloadRequest):
    return video_controller.download_video(request)

@router.get('')
async def get_all_videos(limit: Optional[int] = Query(None)):
    return video_controller.get_all_videos(limit)

@router.post('/download-and-cut')
async def download_and_cut(request: DownloadAndCutRequest):
    return video_controller.download_and_cut(request)

@router.get('/files')
async def list_files():
    return video_controller.list_files()

@router.get('/files/{file_type}/{filename}')
async def download_file(file_type: str = Path(...), filename: str = Path(...)):
    return video_controller.download_file(file_type, filename)

@router.get('/tasks')
async def get_all_tasks():
    return video_controller.get_all_tasks()

@router.get('/tasks/{task_id}')
async def get_task_status(task_id: str = Path(...)):
    return video_controller.get_task_status(task_id)

# Rotas com parâmetros de caminho por último
@router.post('/{video_id}/cut')
async def cut_video(video_id: int = Path(...), request: VideoCutRequest = None):
    return video_controller.cut_video(request)

@router.get('/{video_id}')
async def get_video(video_id: str = Path(...)):
    return video_controller.get_video(video_id)

@router.get('/{video_id}/error')
async def get_video_error(video_id: str = Path(...)):
    return video_controller.get_video_error(video_id)
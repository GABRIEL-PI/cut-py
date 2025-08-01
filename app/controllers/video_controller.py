from fastapi import HTTPException, Response, Request, Query
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import Optional, Dict, Any, List, Union
from app.services.video_service import VideoService
from app.config import DOWNLOADS_DIR, CUTS_DIR
from app.models.video_models import VideoDownloadRequest, VideoCutRequest, DownloadAndCutRequest

class VideoController:
    """
    Controlador para endpoints relacionados a vídeos
    """
    
    def __init__(self):
        """
        Inicializa o controlador de vídeos
        """
        self.video_service = VideoService()
    
    def download_video(self, request: VideoDownloadRequest):
        """
        Endpoint para baixar vídeos
        """
        try:
            # O método download_video retorna (resultado, status_code)
            result, status_code = self.video_service.download_video(
                url=request.url,
                filename=request.filename,
                validate=request.validate,
                cookies=request.cookies,
                cookies_from_browser=request.cookies_from_browser
            )
            
            # Se o status_code não for 200, lançar uma exceção HTTP
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=result)
                
            return result
            
        except HTTPException as e:
            # Repassar exceções HTTP
            raise e
        except Exception as e:
            # Converter outras exceções em HTTPException
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def cut_video(self, request: VideoCutRequest):
        """
        Endpoint para cortar vídeos
        """
        try:
            result, status_code = self.video_service.cut_video(
                video_id=request.video_id,
                start_time=request.start_time,
                end_time=request.end_time,
                output_filename=request.output_filename
            )
            
            # Se o status_code não for 200, lançar uma exceção HTTP
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=result)
                
            return result
            
        except HTTPException as e:
            # Repassar exceções HTTP
            raise e
        except Exception as e:
            # Converter outras exceções em HTTPException
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def download_and_cut(self, request: DownloadAndCutRequest):
        """
        Endpoint para baixar e cortar vídeo em uma operação
        """
        try:
            result = self.video_service.download_and_cut(
                url=request.url,
                start_time=request.start_time,
                end_time=request.end_time,
                filename=request.filename,
                output_filename=request.output_filename,
                cookies=request.cookies,
                cookies_from_browser=request.cookies_from_browser
            )
            
            return result
            
        except Exception as e:
            # Converter exceções em HTTPException
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def get_task_status(self, task_id: str):
        """
        Endpoint para obter status de uma tarefa
        
        Args:
            task_id: ID da tarefa
        """
        try:
            result, status_code = self.video_service.get_task_status(task_id)
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=result)
            return result
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def get_all_tasks(self):
        """
        Endpoint para listar todas as tarefas
        """
        try:
            tasks = self.video_service.get_all_tasks()
            return tasks
            
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def get_video(self, video_id: str):
        """
        Endpoint para obter informações de um vídeo
        
        Args:
            video_id: ID do vídeo
        """
        try:
            result, status_code = self.video_service.get_video(video_id)
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=result)
            return result
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def get_video_error(self, video_id: str):
        """
        Endpoint para obter detalhes de erro de um vídeo
        
        Args:
            video_id: ID do vídeo
        """
        try:
            # Obter detalhes de erro do vídeo
            error_details, status_code = self.video_service.get_video_error_details(video_id)
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=error_details)
            return error_details
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def get_all_videos(self, limit: Optional[int] = Query(None)):
        """
        Endpoint para listar todos os vídeos
        """
        try:
            videos = self.video_service.get_all_videos(limit)
            return videos
            
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
    
    def list_files(self):
        """
        Endpoint para listar arquivos disponíveis para download
        """
        try:
            # Listar arquivos na pasta de downloads
            download_files = []
            if os.path.exists(DOWNLOADS_DIR):
                download_files = [f for f in os.listdir(DOWNLOADS_DIR) if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))]
            
            # Listar arquivos na pasta de cortes
            cut_files = []
            if os.path.exists(CUTS_DIR):
                cut_files = [f for f in os.listdir(CUTS_DIR) if os.path.isfile(os.path.join(CUTS_DIR, f))]
            
            return {
                'downloads': download_files,
                'cuts': cut_files
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
            
    def download_file(self, file_type: str, filename: str):
        """
        Endpoint para baixar um arquivo
        """
        try:
            if file_type == 'download':
                file_path = os.path.join(DOWNLOADS_DIR, filename)
            elif file_type == 'cut':
                file_path = os.path.join(CUTS_DIR, filename)
            else:
                raise HTTPException(status_code=400, detail={'error': 'Tipo de arquivo inválido'})
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail={'error': 'Arquivo não encontrado'})
            
            return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail={'error': str(e)})
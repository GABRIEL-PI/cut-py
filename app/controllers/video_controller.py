from flask import request, jsonify, send_file
import os
from app.services.video_service import VideoService
from app.config import DOWNLOADS_DIR, CUTS_DIR

class VideoController:
    """
    Controlador para endpoints relacionados a vídeos
    """
    
    def __init__(self):
        """
        Inicializa o controlador de vídeos
        """
        self.video_service = VideoService()
    
    def download_video(self):
        """
        Endpoint para baixar vídeos
        """
        try:
            data = request.get_json()
            
            if not data or 'url' not in data:
                return jsonify({'error': 'URL é obrigatória'}), 400
            
            url = data['url']
            filename = data.get('filename')
            
            result = self.video_service.download_video(url, filename)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def cut_video(self):
        """
        Endpoint para cortar vídeos
        """
        try:
            data = request.get_json()
            
            required_fields = ['video_id', 'start_time', 'end_time']
            for field in required_fields:
                if not data or field not in data:
                    return jsonify({'error': f'{field} é obrigatório'}), 400
            
            video_id = data['video_id']
            start_time = data['start_time']
            end_time = data['end_time']
            output_filename = data.get('output_filename')
            
            result, status_code = self.video_service.cut_video(
                video_id, start_time, end_time, output_filename
            )
            
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def download_and_cut(self):
        """
        Endpoint para baixar e cortar vídeo em uma operação
        """
        try:
            data = request.get_json()
            
            required_fields = ['url', 'start_time', 'end_time']
            for field in required_fields:
                if not data or field not in data:
                    return jsonify({'error': f'{field} é obrigatório'}), 400
            
            url = data['url']
            start_time = data['start_time']
            end_time = data['end_time']
            filename = data.get('filename')
            output_filename = data.get('output_filename')
            
            result = self.video_service.download_and_cut(
                url, start_time, end_time, filename, output_filename
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_task_status(self, task_id):
        """
        Endpoint para obter status de uma tarefa
        
        Args:
            task_id: ID da tarefa
        """
        try:
            result, status_code = self.video_service.get_task_status(task_id)
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_all_tasks(self):
        """
        Endpoint para listar todas as tarefas
        """
        try:
            tasks = self.video_service.get_all_tasks()
            return jsonify(tasks)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_video(self, video_id):
        """
        Endpoint para obter informações de um vídeo
        
        Args:
            video_id: ID do vídeo
        """
        try:
            result, status_code = self.video_service.get_video(video_id)
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_all_videos(self):
        """
        Endpoint para listar todos os vídeos
        """
        try:
            limit = request.args.get('limit', type=int)
            videos = self.video_service.get_all_videos(limit)
            return jsonify(videos)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def list_files(self):
        """
        Endpoint para listar arquivos disponíveis
        """
        try:
            files = {
                'downloads': [],
                'cuts': []
            }
            
            # Listar downloads
            if os.path.exists(DOWNLOADS_DIR):
                files['downloads'] = [f for f in os.listdir(DOWNLOADS_DIR) if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))]
            
            # Listar cortes
            if os.path.exists(CUTS_DIR):
                files['cuts'] = [f for f in os.listdir(CUTS_DIR) if os.path.isfile(os.path.join(CUTS_DIR, f))]
            
            return jsonify(files)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def download_file(self, file_type, filename):
        """
        Endpoint para baixar um arquivo
        
        Args:
            file_type: Tipo do arquivo (download ou cut)
            filename: Nome do arquivo
        """
        try:
            if file_type == 'download':
                file_path = os.path.join(DOWNLOADS_DIR, filename)
            elif file_type == 'cut':
                file_path = os.path.join(CUTS_DIR, filename)
            else:
                return jsonify({'error': 'Tipo de arquivo inválido'}), 400
            
            if not os.path.exists(file_path):
                return jsonify({'error': f'Arquivo {filename} não encontrado'}), 404
            
            return send_file(file_path, as_attachment=True)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
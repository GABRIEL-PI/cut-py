import os
import uuid
import threading
import subprocess
from datetime import datetime
from app.repositories.video_repository import VideoRepository
from app.config import DOWNLOADS_DIR, CUTS_DIR, TEMP_DIR

class VideoService:
    """
    Serviço para gerenciamento de vídeos
    """
    
    def __init__(self):
        """
        Inicializa o serviço de vídeos
        """
        self.video_repository = VideoRepository()
        self.tasks = {}
    
    def download_video(self, url, filename=None):
        """
        Inicia o download de um vídeo
        
        Args:
            url: URL do vídeo
            filename: Nome do arquivo (opcional)
            
        Returns:
            dict: Informações da tarefa iniciada
        """
        # Gerar nome de arquivo se não fornecido
        if not filename:
            filename = f'video_{uuid.uuid4().hex[:8]}'
            
        # Garantir que o filename tenha extensão
        if not filename.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            filename += '.%(ext)s'
        
        # Caminho completo para o arquivo
        output_path = os.path.join(DOWNLOADS_DIR, filename)
        
        # Determinar a plataforma com base na URL
        platform = self._detect_platform(url)
        
        # Criar registro no banco de dados
        video_id = self.video_repository.create_video(
            platform=platform,
            url=url,
            filename=filename,
            status="downloading"
        )
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        self.tasks[task_id] = {
            'id': task_id,
            'video_id': video_id,
            'type': 'download',
            'status': 'running',
            'url': url,
            'output_path': output_path,
            'created_at': datetime.now().isoformat(),
            'output': '',
            'error': ''
        }
        
        # Comando para download
        command = f'python download.py --url "{url}" --output "{output_path}"'
        
        # Executar em thread separada
        thread = threading.Thread(target=self._run_command, args=(task_id, command, video_id))
        thread.daemon = True
        thread.start()
        
        return {
            'task_id': task_id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Download iniciado',
            'output_path': output_path
        }
    
    def cut_video(self, video_id, start_time, end_time, output_filename=None):
        """
        Inicia o corte de um vídeo
        
        Args:
            video_id: ID do vídeo a ser cortado
            start_time: Tempo inicial do corte (formato HH:MM:SS)
            end_time: Tempo final do corte (formato HH:MM:SS)
            output_filename: Nome do arquivo de saída (opcional)
            
        Returns:
            dict: Informações da tarefa iniciada ou erro
        """
        # Buscar informações do vídeo
        video = self.video_repository.find(video_id)
        if not video:
            return {'error': f'Vídeo com ID {video_id} não encontrado'}, 404
        
        # Verificar se o vídeo está completo
        if video['status'] != 'completed':
            return {'error': f'Vídeo com ID {video_id} não está pronto para corte (status: {video["status"]})'}, 400
        
        # Gerar nome de arquivo de saída se não fornecido
        if not output_filename:
            output_filename = f'cut_{uuid.uuid4().hex[:8]}.mp4'
        
        # Caminhos completos
        input_file = os.path.join(DOWNLOADS_DIR, video['filename'])
        output_path = os.path.join(CUTS_DIR, output_filename)
        
        # Verificar se arquivo de entrada existe
        if not os.path.exists(input_file):
            return {'error': f'Arquivo de entrada não encontrado: {input_file}'}, 404
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        self.tasks[task_id] = {
            'id': task_id,
            'video_id': video_id,
            'type': 'cut',
            'status': 'running',
            'input_file': input_file,
            'output_path': output_path,
            'start_time': start_time,
            'end_time': end_time,
            'created_at': datetime.now().isoformat(),
            'output': '',
            'error': ''
        }
        
        # Comando para corte
        command = f'python cut.py --input "{input_file}" --output "{output_path}" --start "{start_time}" --end "{end_time}"'
        
        # Executar em thread separada
        thread = threading.Thread(target=self._run_command, args=(task_id, command))
        thread.daemon = True
        thread.start()
        
        return {
            'task_id': task_id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Corte iniciado',
            'output_path': output_path
        }
    
    def download_and_cut(self, url, start_time, end_time, filename=None, output_filename=None):
        """
        Inicia o download e corte de um vídeo em uma operação
        
        Args:
            url: URL do vídeo
            start_time: Tempo inicial do corte (formato HH:MM:SS)
            end_time: Tempo final do corte (formato HH:MM:SS)
            filename: Nome do arquivo de download (opcional)
            output_filename: Nome do arquivo de saída (opcional)
            
        Returns:
            dict: Informações da tarefa iniciada
        """
        # Gerar nomes de arquivo se não fornecidos
        if not filename:
            filename = f'video_{uuid.uuid4().hex[:8]}'
        if not output_filename:
            output_filename = f'cut_{uuid.uuid4().hex[:8]}.mp4'
        
        # Garantir extensão no filename de download
        if not filename.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            filename += '.%(ext)s'
        
        # Caminhos completos
        download_path = os.path.join(DOWNLOADS_DIR, filename)
        cut_path = os.path.join(CUTS_DIR, output_filename)
        
        # Determinar a plataforma com base na URL
        platform = self._detect_platform(url)
        
        # Criar registro no banco de dados
        video_id = self.video_repository.create_video(
            platform=platform,
            url=url,
            filename=filename,
            status="downloading"
        )
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        self.tasks[task_id] = {
            'id': task_id,
            'video_id': video_id,
            'type': 'download_and_cut',
            'status': 'running',
            'url': url,
            'download_path': download_path,
            'cut_path': cut_path,
            'start_time': start_time,
            'end_time': end_time,
            'created_at': datetime.now().isoformat(),
            'output': '',
            'error': ''
        }
        
        # Iniciar thread para download e corte
        thread = threading.Thread(
            target=self._download_and_cut_thread,
            args=(task_id, url, download_path, cut_path, start_time, end_time, video_id)
        )
        thread.daemon = True
        thread.start()
        
        return {
            'task_id': task_id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Download e corte iniciados',
            'download_path': download_path,
            'cut_path': cut_path
        }
    
    def get_task_status(self, task_id):
        """
        Obtém o status de uma tarefa
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            dict: Informações da tarefa ou erro
        """
        if task_id not in self.tasks:
            return {'error': f'Tarefa com ID {task_id} não encontrada'}, 404
        
        return self.tasks[task_id], 200
    
    def get_all_tasks(self):
        """
        Obtém todas as tarefas
        
        Returns:
            list: Lista de tarefas
        """
        return list(self.tasks.values())
    
    def get_video(self, video_id):
        """
        Obtém informações de um vídeo
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            dict: Informações do vídeo ou erro
        """
        video = self.video_repository.find(video_id)
        if not video:
            return {'error': f'Vídeo com ID {video_id} não encontrado'}, 404
        
        return video, 200
    
    def get_all_videos(self, limit=None):
        """
        Obtém todos os vídeos
        
        Args:
            limit: Limite de vídeos a retornar (opcional)
            
        Returns:
            list: Lista de vídeos
        """
        if limit:
            return self.video_repository.query().order_by("created_at", "desc").limit(limit).all()
        else:
            return self.video_repository.query().order_by("created_at", "desc").all()
    
    def _detect_platform(self, url):
        """
        Detecta a plataforma com base na URL
        
        Args:
            url: URL do vídeo
            
        Returns:
            str: Nome da plataforma
        """
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'kwai.com' in url:
            return 'kwai'
        elif 'pinterest.com' in url:
            return 'pinterest'
        else:
            return 'unknown'
    
    def _run_command(self, task_id, command, video_id=None):
        """
        Executa um comando em uma thread separada
        
        Args:
            task_id: ID da tarefa
            command: Comando a ser executado
            video_id: ID do vídeo (opcional)
        """
        try:
            # Atualizar status da tarefa
            self.tasks[task_id]['status'] = 'running'
            
            # Executar comando
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Capturar saída e erro
            stdout, stderr = process.communicate()
            
            # Atualizar tarefa com resultado
            if process.returncode == 0:
                self.tasks[task_id]['status'] = 'completed'
                self.tasks[task_id]['output'] = stdout
                
                # Atualizar status do vídeo se fornecido
                if video_id and self.tasks[task_id]['type'] == 'download':
                    print(f"Chamando update_status para vídeo {video_id} com status 'completed'")
                    # Garantir que video_id seja um número inteiro
                    if isinstance(video_id, dict) and 'id' in video_id:
                        video_id = video_id['id']
                    result = self.video_repository.update_status(video_id, 'completed')
                    print(f"Resultado da chamada update_status: {result}")
            else:
                self.tasks[task_id]['status'] = 'error'
                self.tasks[task_id]['error'] = stderr
                
                # Atualizar status do vídeo se fornecido
                if video_id:
                    print(f"Chamando update_status para vídeo {video_id} com status 'error'")
                    # Garantir que video_id seja um número inteiro
                    if isinstance(video_id, dict) and 'id' in video_id:
                        video_id = video_id['id']
                    result = self.video_repository.update_status(video_id, 'error')
                    print(f"Resultado da chamada update_status: {result}")
        
        except Exception as e:
            # Atualizar tarefa com erro
            self.tasks[task_id]['status'] = 'error'
            self.tasks[task_id]['error'] = str(e)
            
            # Atualizar status do vídeo se fornecido
            if video_id:
                self.video_repository.update_status(video_id, 'error')
    
    def _download_and_cut_thread(self, task_id, url, download_path, cut_path, start_time, end_time, video_id):
        """
        Thread para download e corte sequencial
        
        Args:
            task_id: ID da tarefa
            url: URL do vídeo
            download_path: Caminho para download
            cut_path: Caminho para o corte
            start_time: Tempo inicial do corte
            end_time: Tempo final do corte
            video_id: ID do vídeo
        """
        try:
            # Atualizar status da tarefa
            self.tasks[task_id]['status'] = 'downloading'
            self.tasks[task_id]['output'] = 'Iniciando download...\n'
            
            # Comando para download
            download_command = f'python download.py --url "{url}" --output "{download_path}"'
            
            # Executar comando de download
            download_process = subprocess.Popen(
                download_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Capturar saída e erro
            download_stdout, download_stderr = download_process.communicate()
            
            # Verificar resultado do download
            if download_process.returncode != 0:
                self.tasks[task_id]['status'] = 'error'
                self.tasks[task_id]['error'] = download_stderr
                self.video_repository.update_status(video_id, 'error')
                return
            
            # Atualizar status da tarefa e do vídeo
            self.tasks[task_id]['status'] = 'cutting'
            self.tasks[task_id]['output'] += 'Download concluído. Iniciando corte...\n'
            self.video_repository.update_status(video_id, 'processing')
            
            # Comando para corte
            cut_command = f'python cut.py --input "{download_path}" --output "{cut_path}" --start "{start_time}" --end "{end_time}"'
            
            # Executar comando de corte
            cut_process = subprocess.Popen(
                cut_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Capturar saída e erro
            cut_stdout, cut_stderr = cut_process.communicate()
            
            # Verificar resultado do corte
            if cut_process.returncode == 0:
                self.tasks[task_id]['status'] = 'completed'
                self.tasks[task_id]['output'] += 'Corte concluído com sucesso.\n'
                self.video_repository.update_status(video_id, 'completed')
            else:
                self.tasks[task_id]['status'] = 'error'
                self.tasks[task_id]['error'] = cut_stderr
                self.video_repository.update_status(video_id, 'error')
        
        except Exception as e:
            # Atualizar tarefa com erro
            self.tasks[task_id]['status'] = 'error'
            self.tasks[task_id]['error'] = str(e)
            self.video_repository.update_status(video_id, 'error')
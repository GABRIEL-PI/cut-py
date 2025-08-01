import os
import uuid
import json
import threading
import subprocess
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List, Union
from urllib.parse import urlparse
from app.repositories.video_repository import VideoRepository
from app.config import DOWNLOADS_DIR, CUTS_DIR, TEMP_DIR
from app.utils.cookie_manager import CookieManager
from app.config.cookies import get_cookies_file_path, is_valid_browser
from app.services.auth_service import AuthService, SUPPORTED_PLATFORMS

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
        self.auth_service = AuthService()
    
    def download_video(self, url, filename=None, validate=True, cookies=None, cookies_from_browser=None):
        """
        Inicia o download de um vídeo
        
        Args:
            url: URL do vídeo
            filename: Nome do arquivo (opcional)
            validate: Validar a URL antes de iniciar o download (padrão: True)
            cookies: Caminho para o arquivo de cookies (opcional)
            cookies_from_browser: Navegador para extrair cookies (chrome, firefox, opera, edge, safari) (opcional)
            
        Returns:
            tuple: (resultado, status_code) - Informações da tarefa iniciada e código de status HTTP
        """
        # Validar URL se solicitado
        if validate:
            # Verificar se a URL é válida
            if not url or not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                return {'error': 'URL inválida'}, 400
                
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
        
        # Processar parâmetros de cookies
        cookies_file = None
        
        # Se um arquivo de cookies foi fornecido
        if cookies:
            cookies_file = get_cookies_file_path(cookies)
            if not CookieManager.verify_cookies_file(cookies_file):
                print(f"Arquivo de cookies não encontrado ou inválido: {cookies_file}")
                cookies_file = None
        
        # Se foi solicitado extrair cookies do navegador
        if cookies_from_browser and is_valid_browser(cookies_from_browser):
            # Extrair cookies do navegador
            extracted_cookies = CookieManager.save_cookies_from_browser(
                browser_name=cookies_from_browser
            )
            if extracted_cookies:
                cookies_file = extracted_cookies
        
        # Se não tiver cookies ainda, tentar obter do serviço de autenticação centralizada
        if not cookies_file:
            # Determinar a plataforma para buscar cookies centralizados
            platform_name = self._get_platform_name(platform)
            if platform_name in SUPPORTED_PLATFORMS:
                central_cookies = self.auth_service.get_cookies_file(platform_name)
                if central_cookies:
                    cookies_file = central_cookies
                    print(f"Usando cookies centralizados para: {platform_name}")

        
        # Adicionar parâmetro de cookies ao comando se disponível
        if cookies_file and os.path.exists(cookies_file):
            command += f' --cookies "{cookies_file}"'
        elif cookies_from_browser:
            command += f' --cookies-from-browser "{cookies_from_browser}"'
        
        # Executar em thread separada
        thread = threading.Thread(target=self._run_command, args=(task_id, command, video_id))
        thread.daemon = True
        thread.start()
        
        result = {
            'task_id': task_id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Download iniciado',
            'output_path': output_path
        }
        
        return result, 200
    
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
    
    def download_and_cut(self, url, start_time, end_time, filename=None, output_filename=None, cookies=None, cookies_from_browser=None):
        """
        Inicia o download e corte de um vídeo em uma operação
        
        Args:
            url: URL do vídeo
            start_time: Tempo inicial do corte (formato HH:MM:SS)
            end_time: Tempo final do corte (formato HH:MM:SS)
            filename: Nome do arquivo de download (opcional)
            output_filename: Nome do arquivo de saída (opcional)
            cookies: Caminho para o arquivo de cookies (opcional)
            cookies_from_browser: Navegador para extrair cookies (chrome, firefox, opera, edge, safari) (opcional)
            
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
            args=(task_id, url, download_path, cut_path, start_time, end_time, video_id, cookies, cookies_from_browser)
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
        
    def get_video_error_details(self, video_id):
        """
        Obtém detalhes de erro de um vídeo
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            tuple: (detalhes do erro, código de status HTTP)
        """
        # Buscar o vídeo no repositório
        video = self.video_repository.find_by_id(video_id)
        
        if not video:
            return {'error': f'Vídeo com ID {video_id} não encontrado'}, 404
            
        if video['status'] != 'error':
            return {'error': 'Este vídeo não está em estado de erro'}, 400
            
        # Buscar tarefas relacionadas a este vídeo
        error_details = {'video': video}
        
        # Procurar nas tarefas por informações de erro relacionadas a este vídeo
        related_tasks = []
        for task_id, task in self.tasks.items():
            # Verificar se o video_id está diretamente na tarefa
            task_video_id = task.get('video_id')
            
            # Se video_id for um dicionário, extrair o ID
            if isinstance(task_video_id, dict) and 'id' in task_video_id:
                task_video_id = task_video_id['id']
                
            # Comparar com o ID do vídeo
            if task_video_id == video_id:
                task_info = {
                    'task_id': task_id,
                    'type': task.get('type'),
                    'status': task.get('status'),
                    'error': task.get('error'),
                    'error_details': task.get('error_details')
                }
                related_tasks.append(task_info)
        
        error_details['related_tasks'] = related_tasks
        
        return error_details, 200
    
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
        video = self.video_repository.find_by_id(video_id)
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
    
    def _get_platform_name(self, platform):
        """
        Converte o nome da plataforma para o formato usado pelo serviço de autenticação
        
        Args:
            platform: Nome da plataforma detectada
            
        Returns:
            str: Nome da plataforma no formato do serviço de autenticação
        """
        # Mapeamento de plataformas detectadas para plataformas suportadas pelo serviço de autenticação
        platform_mapping = {
            'youtube': 'youtube',
            'instagram': 'instagram',
            'facebook': 'facebook',
            'kwai': 'kwai',
            'pinterest': 'pinterest',
            # Adicionar outros mapeamentos conforme necessário
        }
        
        return platform_mapping.get(platform.lower(), 'unknown')
    
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
            self.tasks[task_id]['progress'] = 0
            
            # Executar comando
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Capturar saída em tempo real
            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                print(f"DEBUG - Linha capturada: {line.strip()}")
                
                # Extrair JSON da linha
                try:
                    # Tentar encontrar o início do JSON na linha
                    json_start = line.find('{')
                    if json_start >= 0:
                        json_str = line[json_start:]
                        progress_data = json.loads(json_str)
                        if isinstance(progress_data, dict):
                            if progress_data.get('status') == 'downloading' and 'percent' in progress_data:
                                # Atualizar progresso na tarefa
                                self.tasks[task_id]['progress'] = progress_data['percent']
                                self.tasks[task_id]['progress_details'] = progress_data
                                print(f"Download progresso: {progress_data['percent']}%")
                except Exception as e:
                    # Ignorar linhas que não são JSON válido
                    print(f"DEBUG - Erro ao processar JSON: {str(e)}")
                    pass
            
            # Aguardar término do processo
            process.wait()
            stderr = process.stderr.read()
            
            # Atualizar tarefa com resultado
            if process.returncode == 0:
                self.tasks[task_id]['status'] = 'completed'
                self.tasks[task_id]['output'] = ''.join(output_lines)
                self.tasks[task_id]['progress'] = 100  # Garantir que o progresso seja 100% ao completar
                
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
                
                # Procurar por informações de erro em formato JSON nas linhas de saída
                error_details = stderr
                error_json = None
                
                for line in output_lines:
                    try:
                        # Tentar encontrar o início do JSON na linha
                        json_start = line.find('{')
                        if json_start >= 0:
                            json_str = line[json_start:]
                            data = json.loads(json_str)
                            if isinstance(data, dict) and data.get('status') == 'error':
                                error_json = data
                                break
                    except Exception:
                        pass
                
                # Registrar detalhes do erro
                if error_json:
                    self.tasks[task_id]['error'] = error_json.get('error', stderr)
                    self.tasks[task_id]['error_details'] = error_json
                    print(f"ERRO DETALHADO (JSON): {error_json}")
                else:
                    self.tasks[task_id]['error'] = stderr
                    print(f"ERRO DETALHADO (stderr): {stderr}")
                
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
    
    def _download_and_cut_thread(self, task_id, url, download_path, cut_path, start_time, end_time, video_id, cookies=None, cookies_from_browser=None):
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
            cookies: Caminho para o arquivo de cookies (opcional)
            cookies_from_browser: Navegador para extrair cookies (opcional)
        """
        try:
            # Atualizar status da tarefa
            self.tasks[task_id]['status'] = 'downloading'
            self.tasks[task_id]['output'] = 'Iniciando download...\n'
            
            # Comando para download
            download_command = f'python download.py --url "{url}" --output "{download_path}"'
            
            # Processar parâmetros de cookies
            cookies_file = None
            
            # Se um arquivo de cookies foi fornecido
            if cookies:
                cookies_file = get_cookies_file_path(cookies)
                if not CookieManager.verify_cookies_file(cookies_file):
                    print(f"Arquivo de cookies não encontrado ou inválido: {cookies_file}")
                    cookies_file = None
            
            # Se foi solicitado extrair cookies do navegador
            if cookies_from_browser and is_valid_browser(cookies_from_browser):
                # Extrair cookies do navegador
                extracted_cookies = CookieManager.save_cookies_from_browser(
                    browser_name=cookies_from_browser
                )
                if extracted_cookies:
                    cookies_file = extracted_cookies
            
            # Adicionar parâmetro de cookies ao comando se disponível
            if cookies_file and os.path.exists(cookies_file):
                download_command += f' --cookies "{cookies_file}"'
            elif cookies_from_browser:
                download_command += f' --cookies-from-browser "{cookies_from_browser}"'
            
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
                
                # Registrar detalhes do erro
                error_log = {
                    'error_type': 'download_error',
                    'command': download_command,
                    'stderr': download_stderr,
                    'return_code': download_process.returncode,
                    'url': url
                }
                print(f"ERRO DE DOWNLOAD DETALHADO: {error_log}")
                
                # Atualizar status do vídeo para erro
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
            import traceback
            error_traceback = traceback.format_exc()
            
            # Atualizar tarefa com erro
            self.tasks[task_id]['status'] = 'error'
            self.tasks[task_id]['error'] = str(e)
            self.tasks[task_id]['error_details'] = {
                'error_type': 'exception',
                'error_message': str(e),
                'traceback': error_traceback,
                'url': url
            }
            
            # Registrar detalhes do erro
            print(f"ERRO DE EXCEÇÃO: {str(e)}")
            print(f"TRACEBACK: {error_traceback}")
            
            # Atualizar status do vídeo
            self.video_repository.update_status(video_id, 'error')
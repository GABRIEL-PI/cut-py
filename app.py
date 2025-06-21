from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Diretórios para armazenar os arquivos
DOWNLOADS_DIR = "/app/downloads"
CUTS_DIR = "/app/cuts"
TEMP_DIR = "/app/temp"

# Criar diretórios se não existirem
for directory in [DOWNLOADS_DIR, CUTS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Armazenar status das tarefas
tasks = {}

def run_command(task_id, command):
    """Executa um comando e armazena o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=3600)
        tasks[task_id]['status'] = 'completed' if result.returncode == 0 else 'failed'
        tasks[task_id]['output'] = result.stdout
        tasks[task_id]['error'] = result.stderr
        tasks[task_id]['return_code'] = result.returncode
        tasks[task_id]['completed_at'] = datetime.now().isoformat()
    except subprocess.TimeoutExpired:
        tasks[task_id]['status'] = 'timeout'
        tasks[task_id]['error'] = 'Comando expirou após 1 hora'
        tasks[task_id]['completed_at'] = datetime.now().isoformat()
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)
        tasks[task_id]['completed_at'] = datetime.now().isoformat()

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde"""
    return jsonify({
        'status': 'ok',
        'message': 'Video Processing API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/download', methods=['POST'])
def download_video():
    """Endpoint para baixar vídeos"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL é obrigatória'}), 400
        
        url = data['url']
        filename = data.get('filename', f'video_{uuid.uuid4().hex[:8]}')
        
        # Garantir que o filename tenha extensão
        if not filename.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            filename += '.%(ext)s'
        
        output_path = os.path.join(DOWNLOADS_DIR, filename)
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        tasks[task_id] = {
            'id': task_id,
            'type': 'download',
            'status': 'running',
            'url': url,
            'output_path': output_path,
            'created_at': datetime.now().isoformat(),
            'output': '',
            'error': ''
        }
        
        # Comando para download
        command = f'python3 /app/download.py --url "{url}" --output "{output_path}"'
        
        # Executar em thread separada
        thread = threading.Thread(target=run_command, args=(task_id, command))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Download iniciado',
            'output_path': output_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cut', methods=['POST'])
def cut_video():
    """Endpoint para cortar vídeos"""
    try:
        data = request.get_json()
        
        required_fields = ['input_file', 'start_time', 'end_time']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        input_file = data['input_file']
        start_time = data['start_time']
        end_time = data['end_time']
        output_filename = data.get('output_filename', f'cut_{uuid.uuid4().hex[:8]}.mp4')
        
        # Se o arquivo de entrada não for caminho absoluto, assumir que está na pasta downloads
        if not os.path.isabs(input_file):
            input_file = os.path.join(DOWNLOADS_DIR, input_file)
        
        output_path = os.path.join(CUTS_DIR, output_filename)
        
        # Verificar se arquivo de entrada existe
        if not os.path.exists(input_file):
            return jsonify({'error': f'Arquivo de entrada não encontrado: {input_file}'}), 404
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        tasks[task_id] = {
            'id': task_id,
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
        command = f'python3 /app/cut.py --input "{input_file}" --start "{start_time}" --end "{end_time}" --output "{output_path}"'
        
        # Executar em thread separada
        thread = threading.Thread(target=run_command, args=(task_id, command))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Corte iniciado',
            'output_path': output_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-and-cut', methods=['POST'])
def download_and_cut():
    """Endpoint para baixar e cortar vídeo em uma operação"""
    try:
        data = request.get_json()
        
        required_fields = ['url', 'start_time', 'end_time']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        url = data['url']
        start_time = data['start_time']
        end_time = data['end_time']
        filename = data.get('filename', f'video_{uuid.uuid4().hex[:8]}')
        output_filename = data.get('output_filename', f'cut_{uuid.uuid4().hex[:8]}.mp4')
        
        # Garantir extensão no filename de download
        if not filename.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            filename += '.%(ext)s'
        
        download_path = os.path.join(DOWNLOADS_DIR, filename)
        cut_path = os.path.join(CUTS_DIR, output_filename)
        
        # Gerar ID da tarefa
        task_id = str(uuid.uuid4())
        
        # Inicializar tarefa
        tasks[task_id] = {
            'id': task_id,
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
        
        # Comandos sequenciais
        download_cmd = f'python3 /app/download.py --url "{url}" --output "{download_path}"'
        cut_cmd = f'python3 /app/cut.py --input "{download_path}" --start "{start_time}" --end "{end_time}" --output "{cut_path}"'
        combined_cmd = f'{download_cmd} && {cut_cmd}'
        
        # Executar em thread separada
        thread = threading.Thread(target=run_command, args=(task_id, combined_cmd))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Download e corte iniciados',
            'download_path': download_path,
            'cut_path': cut_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Consultar status de uma tarefa"""
    if task_id not in tasks:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    return jsonify(tasks[task_id])

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """Listar todas as tarefas"""
    return jsonify(list(tasks.values()))

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Fazer download de um arquivo processado"""
    # Procurar primeiro na pasta de cortes, depois na de downloads
    for directory in [CUTS_DIR, DOWNLOADS_DIR]:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    
    return jsonify({'error': 'Arquivo não encontrado'}), 404

@app.route('/files', methods=['GET'])
def list_files():
    """Listar arquivos disponíveis"""
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

@app.route('/clean', methods=['POST'])
def clean_files():
    """Limpar arquivos antigos"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)  # Padrão: arquivos mais antigos que 7 dias
        
        cleaned = {'downloads': 0, 'cuts': 0}
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        # Limpar downloads
        for filename in os.listdir(DOWNLOADS_DIR):
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                cleaned['downloads'] += 1
        
        # Limpar cortes
        for filename in os.listdir(CUTS_DIR):
            filepath = os.path.join(CUTS_DIR, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                cleaned['cuts'] += 1
        
        return jsonify({
            'message': f'Arquivos mais antigos que {days} dias foram removidos',
            'cleaned': cleaned
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
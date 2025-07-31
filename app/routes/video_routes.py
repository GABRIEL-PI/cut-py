from flask import Blueprint
from app.controllers.video_controller import VideoController

# Criar blueprint para rotas de vídeo
video_bp = Blueprint('video', __name__)

# Instanciar controlador
video_controller = VideoController()

# Definir rotas
@video_bp.route('/videos', methods=['POST'])
def download_video():
    return video_controller.download_video()

@video_bp.route('/videos/<int:video_id>/cut', methods=['POST'])
def cut_video(video_id):
    return video_controller.cut_video()

@video_bp.route('/videos/download-and-cut', methods=['POST'])
def download_and_cut():
    return video_controller.download_and_cut()

@video_bp.route('/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    return video_controller.get_video(video_id)

@video_bp.route('/videos', methods=['GET'])
def get_all_videos():
    return video_controller.get_all_videos()

@video_bp.route('/tasks/<string:task_id>', methods=['GET'])
def get_task_status(task_id):
    return video_controller.get_task_status(task_id)

@video_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    return video_controller.get_all_tasks()

@video_bp.route('/files', methods=['GET'])
def list_files():
    return video_controller.list_files()

@video_bp.route('/files/<string:file_type>/<path:filename>', methods=['GET'])
def download_file(file_type, filename):
    return video_controller.download_file(file_type, filename)
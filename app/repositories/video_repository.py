from datetime import datetime
from app.repositories.mysql_repository import BaseRepository
from app.models.video import Video

class VideoRepository(BaseRepository):
    """
    Repositório para operações com vídeos no banco de dados
    """
    
    def __init__(self):
        """
        Inicializa o repositório de vídeos
        """
        super().__init__(table_name="videos", primary_key="id")
    
    def create_video(self, platform, url, filename, status="pending", duration=None):
        """
        Cria um novo registro de vídeo
        
        Args:
            platform: Plataforma de origem do vídeo
            url: URL do vídeo
            filename: Nome do arquivo
            status: Status inicial do vídeo (default: pending)
            duration: Duração do vídeo em segundos (opcional)
            
        Returns:
            int: ID do vídeo criado
        """
        data = {
            "platform": platform,
            "url": url,
            "filename": filename,
            "status": status,
            "duration": duration,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return self.create(data)
    
    def update_status(self, video_id, status):
        """
        Atualiza o status de um vídeo
        
        Args:
            video_id: ID do vídeo
            status: Novo status (pending, downloading, completed, error)
            
        Returns:
            bool: True se atualizado com sucesso
        """
        print(f"Atualizando status do vídeo {video_id} para {status}")
        # Simplificar para apenas atualizar o status
        result = self.update(video_id, {"status": status})
        print(f"Resultado da atualização: {result}")
        return result
    
    def update_duration(self, video_id, duration):
        """
        Atualiza a duração de um vídeo
        
        Args:
            video_id: ID do vídeo
            duration: Duração em segundos
            
        Returns:
            bool: True se atualizado com sucesso
        """
        return self.update(video_id, {"duration": duration, "updated_at": datetime.now()})
    
    def find_by_url(self, url):
        """
        Busca um vídeo pela URL
        
        Args:
            url: URL do vídeo
            
        Returns:
            dict: Dados do vídeo ou None se não encontrado
        """
        return self.query().where("url", url).first()
    
    def find_by_filename(self, filename):
        """
        Busca um vídeo pelo nome do arquivo
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            dict: Dados do vídeo ou None se não encontrado
        """
        return self.query().where("filename", filename).first()
    
    def find_by_status(self, status):
        """
        Busca vídeos por status
        
        Args:
            status: Status a ser buscado
            
        Returns:
            list: Lista de vídeos com o status especificado
        """
        return self.query().where("status", status).all()
    
    def get_recent_videos(self, limit=10):
        """
        Obtém os vídeos mais recentes
        
        Args:
            limit: Número máximo de vídeos a retornar
            
        Returns:
            list: Lista de vídeos ordenados por data de criação
        """
        return self.query().order_by("created_at", "desc").limit(limit).all()
    
    def delete_video(self, video_id):
        """
        Exclui um vídeo pelo ID
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            bool: True se excluído com sucesso
        """
        return self.delete(video_id)
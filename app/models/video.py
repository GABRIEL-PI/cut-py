from datetime import datetime

class Video:
    """
    Modelo para representar um vídeo
    """
    
    def __init__(self, id=None, platform=None, url=None, filename=None, 
                 status="pending", duration=None, created_at=None, updated_at=None):
        """
        Inicializa um objeto Video
        
        Args:
            id: ID do vídeo
            platform: Plataforma de origem do vídeo
            url: URL do vídeo
            filename: Nome do arquivo
            status: Status do vídeo (pending, downloading, completed, error)
            duration: Duração do vídeo em segundos
            created_at: Data de criação
            updated_at: Data de atualização
        """
        self.id = id
        self.platform = platform
        self.url = url
        self.filename = filename
        self.status = status
        self.duration = duration
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria um objeto Video a partir de um dicionário
        
        Args:
            data: Dicionário com dados do vídeo
            
        Returns:
            Video: Objeto Video
        """
        return cls(
            id=data.get('id'),
            platform=data.get('platform'),
            url=data.get('url'),
            filename=data.get('filename'),
            status=data.get('status', 'pending'),
            duration=data.get('duration'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """
        Converte o objeto Video para um dicionário
        
        Returns:
            dict: Dicionário com dados do vídeo
        """
        return {
            "id": self.id,
            "platform": self.platform,
            "url": self.url,
            "filename": self.filename,
            "status": self.status,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at
        }
    
    def __repr__(self):
        return f"<Video(id={self.id}, platform={self.platform}, status={self.status})>"
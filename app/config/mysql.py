import os
import pymysql
import logging
from app.config import DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

class MySQL:
    """Classe para gerenciar conexões com o banco de dados MySQL"""
    
    @staticmethod
    def get_connection():
        """Obtém uma conexão com o banco de dados MySQL
        
        Returns:
            pymysql.connections.Connection: Conexão com o banco de dados
        """
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as e:
            logger.error(f"Erro ao conectar ao MySQL: {e}")
            raise
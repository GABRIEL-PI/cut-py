import os
import json
import tempfile
import subprocess
from pathlib import Path
from app.config.cookies import COOKIES_DIR, DEFAULT_COOKIES_FILE, SUPPORTED_BROWSERS

class CookieManager:
    """
    Gerenciador de cookies para download de vídeos
    """
    
    @staticmethod
    def save_cookies_from_browser(browser_name, output_file=None):
        """
        Extrai cookies do navegador e salva em um arquivo
        
        Args:
            browser_name: Nome do navegador (chrome, firefox, opera, edge, safari)
            output_file: Caminho para salvar o arquivo de cookies (opcional)
            
        Returns:
            str: Caminho para o arquivo de cookies ou None se falhar
        """
        if browser_name.lower() not in SUPPORTED_BROWSERS:
            print(f"Navegador não suportado: {browser_name}")
            return None
        
        if not output_file:
            output_file = DEFAULT_COOKIES_FILE
        
        try:
            # Usar yt-dlp para extrair cookies
            cmd = [
                "yt-dlp",
                "--cookies-from-browser",
                browser_name,
                "--cookies",
                output_file,
                "--skip-download",
                "--quiet",
                "https://www.youtube.com/"
            ]
            
            subprocess.run(cmd, check=True)
            
            if os.path.exists(output_file):
                return output_file
            
        except subprocess.CalledProcessError as e:
            print(f"Erro ao extrair cookies: {str(e)}")
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
        
        return None
    
    @staticmethod
    def verify_cookies_file(cookies_file):
        """
        Verifica se o arquivo de cookies existe e é válido
        
        Args:
            cookies_file: Caminho para o arquivo de cookies
            
        Returns:
            bool: True se o arquivo for válido, False caso contrário
        """
        if not cookies_file or not os.path.exists(cookies_file):
            return False
        
        # Verificar se o arquivo tem conteúdo
        return os.path.getsize(cookies_file) > 0
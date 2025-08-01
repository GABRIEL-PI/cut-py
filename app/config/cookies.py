import os
from pathlib import Path
from app.config import TEMP_DIR

# Diretório para armazenar os cookies
COOKIES_DIR = os.path.join(TEMP_DIR, "cookies")

# Criar diretório se não existir
os.makedirs(COOKIES_DIR, exist_ok=True)

# Caminho padrão para o arquivo de cookies
DEFAULT_COOKIES_FILE = os.path.join(COOKIES_DIR, "youtube_cookies.txt")

# Navegadores suportados para extração de cookies
SUPPORTED_BROWSERS = ["chrome", "firefox", "opera", "edge", "safari"]

def get_cookies_file_path(filename=None):
    """
    Obtém o caminho completo para um arquivo de cookies
    
    Args:
        filename: Nome do arquivo de cookies (opcional)
        
    Returns:
        str: Caminho completo para o arquivo de cookies
    """
    if not filename:
        return DEFAULT_COOKIES_FILE
    
    # Se o caminho for absoluto, retornar como está
    if os.path.isabs(filename):
        return filename
    
    # Caso contrário, combinar com o diretório de cookies
    return os.path.join(COOKIES_DIR, filename)

def is_valid_browser(browser_name):
    """
    Verifica se o navegador é suportado para extração de cookies
    
    Args:
        browser_name: Nome do navegador
        
    Returns:
        bool: True se o navegador for suportado, False caso contrário
    """
    return browser_name.lower() in SUPPORTED_BROWSERS
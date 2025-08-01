import os
import time
import logging
import threading
import schedule
from datetime import datetime
from app.services.auth_service import AuthService

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cookie_update_job')

class CookieUpdateJob:
    """Job para atualização periódica de cookies"""
    
    _instance = None
    _lock = threading.Lock()
    _running = False
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CookieUpdateJob, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Inicializa o job de atualização de cookies"""
        if self._initialized:
            return
            
        self.auth_service = AuthService()
        self._initialized = True
    
    def start(self):
        """Inicia o job de atualização de cookies"""
        if CookieUpdateJob._running:
            logger.info("Job de atualização de cookies já está em execução")
            return
        
        # Configurar credenciais iniciais (exemplo com YouTube/Gmail)
        self.auth_service.set_credentials(
            "youtube", 
            "cut.py01@gmail.com", 
            "G@bryel123"
        )
        
        # Realizar login inicial para todas as plataformas configuradas
        self._update_all_cookies()
        
        # Agendar atualização diária às 3 da manhã
        schedule.every().day.at("03:00").do(self._update_all_cookies)
        
        # Iniciar thread para executar o agendador
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        CookieUpdateJob._running = True
        
        logger.info("Job de atualização de cookies iniciado")
    
    def _update_all_cookies(self):
        """Atualiza os cookies de todas as plataformas configuradas"""
        try:
            logger.info("Iniciando atualização de cookies para todas as plataformas")
            results = self.auth_service.update_all_cookies()
            
            # Registrar resultados
            for platform, success in results.items():
                if success:
                    logger.info(f"Cookies atualizados com sucesso para: {platform}")
                else:
                    logger.error(f"Falha ao atualizar cookies para: {platform}")
            
            return results
        except Exception as e:
            logger.error(f"Erro ao atualizar cookies: {str(e)}")
            return {}
    
    def add_platform_credentials(self, platform, username, password):
        """Adiciona credenciais para uma nova plataforma
        
        Args:
            platform: Nome da plataforma (youtube, instagram, facebook, etc.)
            username: Nome de usuário ou email
            password: Senha
            
        Returns:
            bool: True se as credenciais foram definidas com sucesso
        """
        success = self.auth_service.set_credentials(platform, username, password)
        
        # Se as credenciais foram definidas com sucesso, tentar fazer login imediatamente
        if success:
            cookies_file = self.auth_service.login_and_save_cookies(platform)
            if cookies_file:
                logger.info(f"Login inicial realizado com sucesso para: {platform}")
            else:
                logger.error(f"Falha no login inicial para: {platform}")
        
        return success
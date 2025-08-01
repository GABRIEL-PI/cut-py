import os
import json
import time
import logging
import threading
import schedule
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from app.config import TEMP_DIR
from app.config.cookies import COOKIES_DIR, SUPPORTED_BROWSERS

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('auth_service')

# Diretório para armazenar cookies centralizados
CENTRAL_COOKIES_DIR = os.path.join(COOKIES_DIR, "central")
os.makedirs(CENTRAL_COOKIES_DIR, exist_ok=True)

# Plataformas suportadas
SUPPORTED_PLATFORMS = {
    "youtube": {
        "login_url": "https://accounts.google.com/signin",
        "cookies_file": "youtube_cookies.txt",
        "domain": "youtube.com"
    },
    "instagram": {
        "login_url": "https://www.instagram.com/accounts/login/",
        "cookies_file": "instagram_cookies.txt",
        "domain": "instagram.com"
    },
    "facebook": {
        "login_url": "https://www.facebook.com/login/",
        "cookies_file": "facebook_cookies.txt",
        "domain": "facebook.com"
    },
    "kwai": {
        "login_url": "https://www.kwai.com/login",
        "cookies_file": "kwai_cookies.txt",
        "domain": "kwai.com"
    },
    "pinterest": {
        "login_url": "https://www.pinterest.com/login/",
        "cookies_file": "pinterest_cookies.txt",
        "domain": "pinterest.com"
    }
}

class AuthService:
    """Serviço para gerenciamento de autenticação centralizada"""
    
    _instance = None
    _lock = threading.Lock()
    _scheduler_started = False
    
    @staticmethod
    def _find_chromedriver_recursively(start_dir):
        """Procura recursivamente pelo chromedriver em um diretório
        
        Args:
            start_dir: Diretório inicial para a busca
            
        Returns:
            str: Caminho para o chromedriver ou None se não encontrado
        """
        if not os.path.exists(start_dir):
            return None
            
        for root, dirs, files in os.walk(start_dir):
            for file in files:
                if file == 'chromedriver.exe' or file == 'chromedriver':
                    return os.path.join(root, file)
        return None
    
    @staticmethod
    def _check_chrome_installation():
        """Verifica se o Chrome está instalado e retorna o caminho
        
        Returns:
            str: Caminho para o executável do Chrome ou None se não encontrado
        """
        chrome_path = None
        
        # Verificar no Windows
        if sys.platform.startswith('win'):
            # Locais comuns de instalação do Chrome no Windows
            possible_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
        
        # Verificar no Linux
        elif sys.platform.startswith('linux'):
            try:
                chrome_path = subprocess.check_output(['which', 'google-chrome']).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                pass
        
        # Verificar no macOS
        elif sys.platform == 'darwin':
            default_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            if os.path.exists(default_path):
                chrome_path = default_path
        
        return chrome_path
        
    @staticmethod
    def _check_firefox_installation():
        """Verifica se o Firefox está instalado e retorna o caminho
        
        Returns:
            str: Caminho para o executável do Firefox ou None se não encontrado
        """
        firefox_path = None
        
        # Verificar no Windows
        if sys.platform.startswith('win'):
            # Locais comuns de instalação do Firefox no Windows
            possible_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Mozilla Firefox', 'firefox.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Mozilla Firefox', 'firefox.exe')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    firefox_path = path
                    break
        
        # Verificar no Linux
        elif sys.platform.startswith('linux'):
            try:
                firefox_path = subprocess.check_output(['which', 'firefox']).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                pass
        
        # Verificar no macOS
        elif sys.platform == 'darwin':
            default_path = '/Applications/Firefox.app/Contents/MacOS/firefox'
            if os.path.exists(default_path):
                firefox_path = default_path
        
        return firefox_path
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AuthService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Inicializa o serviço de autenticação"""
        if self._initialized:
            return
            
        self.credentials = {}
        self.last_update = {}
        self._initialized = True
        
        # Iniciar o agendador se ainda não estiver rodando
        if not AuthService._scheduler_started:
            self._start_scheduler()
    
    def _start_scheduler(self):
        """Inicia o agendador para atualização periódica de cookies"""
        # Agendar atualização diária de cookies às 3 da manhã
        schedule.every().day.at("03:00").do(self.update_all_cookies)
        
        # Iniciar thread para executar o agendador
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        AuthService._scheduler_started = True
        logger.info("Agendador de atualização de cookies iniciado")
    
    def set_credentials(self, platform: str, username: str, password: str) -> bool:
        """Define as credenciais para uma plataforma
        
        Args:
            platform: Nome da plataforma (youtube, instagram, facebook, etc.)
            username: Nome de usuário ou email
            password: Senha
            
        Returns:
            bool: True se as credenciais foram definidas com sucesso
        """
        if platform not in SUPPORTED_PLATFORMS:
            logger.error(f"Plataforma não suportada: {platform}")
            return False
        
        self.credentials[platform] = {
            "username": username,
            "password": password
        }
        
        logger.info(f"Credenciais definidas para a plataforma: {platform}")
        return True
    
    def login_and_save_cookies(self, platform: str) -> Optional[str]:
        """Realiza login na plataforma e salva os cookies
        
        Args:
            platform: Nome da plataforma (youtube, instagram, facebook, etc.)
            
        Returns:
            str: Caminho para o arquivo de cookies ou None se falhar
        """
        if platform not in SUPPORTED_PLATFORMS:
            logger.error(f"Plataforma não suportada: {platform}")
            return None
        
        if platform not in self.credentials:
            logger.error(f"Credenciais não definidas para a plataforma: {platform}")
            return None
        
        platform_config = SUPPORTED_PLATFORMS[platform]
        credentials = self.credentials[platform]
        
        # Verificar se o Chrome está instalado
        chrome_path = self._check_chrome_installation()
        if not chrome_path:
            logger.error(f"Chrome não encontrado no sistema. Não é possível realizar login na plataforma: {platform}")
            return None
        else:
            logger.info(f"Chrome encontrado em: {chrome_path}")
            
        # Tentar inicializar o Chrome primeiro
        try:
            # Configurar o Chrome em modo headless
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            chrome_options.binary_location = chrome_path
            
            # Tentar inicializar o driver sem especificar a arquitetura
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_error:
                # Se falhar, tentar inicializar diretamente
                logger.warning(f"Erro ao inicializar ChromeDriver: {str(driver_error)}. Tentando método alternativo...")
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception as driver_error2:
                    logger.warning(f"Erro ao inicializar Chrome diretamente: {str(driver_error2)}. Tentando método alternativo com caminho explícito...")
                    try:
                        # Tentar com caminho explícito para o chromedriver
                        chrome_path_parts = os.path.normpath(chrome_path).split(os.sep)
                        chrome_version = chrome_path_parts[-2] if len(chrome_path_parts) > 1 else ''
                        logger.info(f"Versão do Chrome detectada: {chrome_version}")
                        
                        # Procurar o chromedriver em vários locais possíveis
                        possible_driver_paths = [
                            # Caminho específico que aparece nos logs de erro
                            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', '138.0.7204.183', 'chromedriver-win32', 'chromedriver.exe'),
                            # Outros caminhos possíveis
                            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', chrome_version, 'chromedriver.exe'),
                            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', chrome_version, 'chromedriver-win32', 'chromedriver.exe'),
                            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', chrome_version, 'chromedriver-win64', 'chromedriver.exe'),
                            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win32', chrome_version, 'chromedriver.exe')
                        ]
                        
                        driver_path = None
                        for path in possible_driver_paths:
                            if os.path.exists(path):
                                driver_path = path
                                logger.info(f"ChromeDriver encontrado em: {driver_path}")
                                break
                                
                        if driver_path:
                            service = ChromeService(driver_path)
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                        else:
                            # Tentar encontrar o chromedriver recursivamente
                            logger.info("Procurando chromedriver recursivamente...")
                            wdm_dir = os.path.join(os.path.expanduser('~'), '.wdm')
                            recursive_driver_path = self._find_chromedriver_recursively(wdm_dir)
                            
                            if recursive_driver_path:
                                logger.info(f"ChromeDriver encontrado recursivamente em: {recursive_driver_path}")
                                service = ChromeService(recursive_driver_path)
                                driver = webdriver.Chrome(service=service, options=chrome_options)
                            else:
                                # Listar os diretórios para ajudar na depuração
                                if os.path.exists(wdm_dir):
                                    logger.info(f"Conteúdo do diretório .wdm: {os.listdir(wdm_dir)}")
                                    drivers_dir = os.path.join(wdm_dir, 'drivers')
                                    if os.path.exists(drivers_dir):
                                        logger.info(f"Conteúdo do diretório drivers: {os.listdir(drivers_dir)}")
                                        chromedriver_dir = os.path.join(drivers_dir, 'chromedriver')
                                        if os.path.exists(chromedriver_dir):
                                            logger.info(f"Conteúdo do diretório chromedriver: {os.listdir(chromedriver_dir)}")
                                
                                raise Exception(f"ChromeDriver não encontrado em nenhum dos caminhos possíveis")
                    except Exception as driver_error3:
                        logger.error(f"Todos os métodos de inicialização do Chrome falharam: {str(driver_error3)}")
                        raise
        except Exception as chrome_error:
            # Se falhar com Chrome, tentar Firefox como fallback
            logger.warning(f"Falha ao inicializar Chrome: {str(chrome_error)}. Tentando Firefox como fallback...")
            firefox_path = self._check_firefox_installation()
            if not firefox_path:
                logger.error("Firefox não encontrado no sistema. Não é possível realizar login.")
                return None
                
            logger.info(f"Firefox encontrado em: {firefox_path}")
            try:
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0")
                
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=firefox_options)
                logger.info("Firefox WebDriver inicializado com sucesso")
            except Exception as firefox_error:
                logger.error(f"Erro ao inicializar Firefox: {str(firefox_error)}")
                return None
            
            # Processo de login específico para cada plataforma
            if platform == "youtube":
                self._login_youtube(driver, credentials)
            elif platform == "instagram":
                self._login_instagram(driver, credentials)
            elif platform == "facebook":
                self._login_facebook(driver, credentials)
            elif platform == "kwai":
                self._login_kwai(driver, credentials)
            elif platform == "pinterest":
                self._login_pinterest(driver, credentials)
            
            # Extrair e salvar cookies
            cookies_file = os.path.join(CENTRAL_COOKIES_DIR, platform_config["cookies_file"])
            self._save_cookies_to_file(driver, cookies_file, platform_config["domain"])
            
            # Atualizar timestamp da última atualização
            self.last_update[platform] = datetime.now().isoformat()
            
            # Fechar o driver
            driver.quit()
            
            logger.info(f"Login realizado com sucesso na plataforma: {platform}")
            return cookies_file
            
        except Exception as e:
            logger.error(f"Erro ao realizar login na plataforma {platform}: {str(e)}")
            return None
    
    def _login_youtube(self, driver, credentials):
        """Realiza login no YouTube/Google"""
        driver.get("https://accounts.google.com/signin")
        
        # Aguardar e preencher email
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "identifier")))
        email_field = driver.find_element(By.NAME, "identifier")
        email_field.send_keys(credentials["username"])
        driver.find_element(By.ID, "identifierNext").click()
        
        # Aguardar e preencher senha
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "Passwd")))
        password_field = driver.find_element(By.NAME, "Passwd")
        password_field.send_keys(credentials["password"])
        driver.find_element(By.ID, "passwordNext").click()
        
        # Aguardar conclusão do login
        WebDriverWait(driver, 30).until(lambda d: "accounts.google.com" not in d.current_url)
        
        # Navegar para o YouTube para garantir que os cookies sejam criados
        driver.get("https://www.youtube.com/")
        time.sleep(5)  # Aguardar carregamento completo
    
    def _login_instagram(self, driver, credentials):
        """Realiza login no Instagram"""
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        
        # Preencher usuário e senha
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(credentials["username"])
        password_field.send_keys(credentials["password"])
        
        # Clicar no botão de login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Aguardar conclusão do login
        WebDriverWait(driver, 30).until(lambda d: "instagram.com/accounts/login" not in d.current_url)
        time.sleep(5)  # Aguardar carregamento completo
    
    def _login_facebook(self, driver, credentials):
        """Realiza login no Facebook"""
        driver.get("https://www.facebook.com/login/")
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "email")))
        
        # Preencher email e senha
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "pass")
        
        email_field.send_keys(credentials["username"])
        password_field.send_keys(credentials["password"])
        
        # Clicar no botão de login
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        
        # Aguardar conclusão do login
        WebDriverWait(driver, 30).until(lambda d: "facebook.com/login" not in d.current_url)
        time.sleep(5)  # Aguardar carregamento completo
    
    def _login_kwai(self, driver, credentials):
        """Realiza login no Kwai"""
        driver.get("https://www.kwai.com/login")
        
        # Implementar lógica específica para o Kwai
        # Como o Kwai pode ter diferentes métodos de login, esta é uma implementação básica
        # que pode precisar de ajustes conforme a interface atual do site
        
        # Aguardar carregamento da página
        time.sleep(5)
        
        # Tentar encontrar campos de login
        try:
            # Tentar encontrar campos de email/senha
            email_field = driver.find_element(By.XPATH, "//input[@type='email' or @type='text']")
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            
            email_field.send_keys(credentials["username"])
            password_field.send_keys(credentials["password"])
            
            # Tentar encontrar botão de login
            login_button = driver.find_element(By.XPATH, "//button[contains(@class, 'login') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
            login_button.click()
            
            # Aguardar conclusão do login
            time.sleep(10)
        except Exception as e:
            logger.error(f"Erro no processo de login do Kwai: {str(e)}")
            raise
    
    def _login_pinterest(self, driver, credentials):
        """Realiza login no Pinterest"""
        driver.get("https://www.pinterest.com/login/")
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "email")))
        
        # Preencher email e senha
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys(credentials["username"])
        password_field.send_keys(credentials["password"])
        
        # Clicar no botão de login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Aguardar conclusão do login
        WebDriverWait(driver, 30).until(lambda d: "pinterest.com/login" not in d.current_url)
        time.sleep(5)  # Aguardar carregamento completo
    
    def _save_cookies_to_file(self, driver, cookies_file: str, domain: str):
        """Salva os cookies do navegador em um arquivo no formato compatível com yt-dlp
        
        Args:
            driver: Instância do WebDriver
            cookies_file: Caminho para o arquivo de cookies
            domain: Domínio para filtrar os cookies
        """
        # Obter todos os cookies do navegador
        browser_cookies = driver.get_cookies()
        
        # Filtrar cookies pelo domínio
        filtered_cookies = [cookie for cookie in browser_cookies 
                           if domain in cookie.get('domain', '')]
        
        # Converter para o formato Netscape (compatível com yt-dlp)
        with open(cookies_file, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This file was generated by AuthService\n")
            f.write("# https://github.com/netscape/mozilla/releases\n")
            f.write("# This is a generated file! Do not edit.\n\n")
            
            for cookie in filtered_cookies:
                secure = "TRUE" if cookie.get('secure', False) else "FALSE"
                http_only = "TRUE" if cookie.get('httpOnly', False) else "FALSE"
                expires = str(int(cookie.get('expiry', 0))) if 'expiry' in cookie else "0"
                
                cookie_line = f"{cookie.get('domain', '')}\t"
                cookie_line += "TRUE\t"  # includeSubdomains
                cookie_line += f"{cookie.get('path', '/')}\t"
                cookie_line += f"{secure}\t"
                cookie_line += f"{expires}\t"
                cookie_line += f"{cookie.get('name', '')}\t"
                cookie_line += f"{cookie.get('value', '')}\n"
                
                f.write(cookie_line)
        
        logger.info(f"Cookies salvos em: {cookies_file}")
    
    def get_cookies_file(self, platform: str) -> Optional[str]:
        """Obtém o caminho para o arquivo de cookies de uma plataforma
        
        Args:
            platform: Nome da plataforma (youtube, instagram, facebook, etc.)
            
        Returns:
            str: Caminho para o arquivo de cookies ou None se não existir
        """
        if platform not in SUPPORTED_PLATFORMS:
            logger.error(f"Plataforma não suportada: {platform}")
            return None
        
        platform_config = SUPPORTED_PLATFORMS[platform]
        cookies_file = os.path.join(CENTRAL_COOKIES_DIR, platform_config["cookies_file"])
        
        if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 0:
            return cookies_file
        
        # Se o arquivo não existir ou estiver vazio, tentar fazer login
        if platform in self.credentials:
            return self.login_and_save_cookies(platform)
        
        return None
    
    def update_all_cookies(self) -> Dict[str, bool]:
        """Atualiza os cookies de todas as plataformas configuradas
        
        Returns:
            Dict[str, bool]: Dicionário com o resultado da atualização para cada plataforma
        """
        results = {}
        
        for platform in self.credentials.keys():
            if platform in SUPPORTED_PLATFORMS:
                logger.info(f"Atualizando cookies para a plataforma: {platform}")
                cookies_file = self.login_and_save_cookies(platform)
                results[platform] = cookies_file is not None
        
        return results
    
    def get_last_update(self, platform: str) -> Optional[str]:
        """Obtém a data da última atualização dos cookies de uma plataforma
        
        Args:
            platform: Nome da plataforma (youtube, instagram, facebook, etc.)
            
        Returns:
            str: Data da última atualização em formato ISO ou None se não houver
        """
        return self.last_update.get(platform)
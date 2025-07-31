import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios para armazenar os arquivos
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
CUTS_DIR = os.path.join(os.getcwd(), "cuts")
TEMP_DIR = os.path.join(os.getcwd(), "temp")

# Criar diretórios se não existirem
for directory in [DOWNLOADS_DIR, CUTS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configurações do banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_DATABASE = os.getenv("DB_DATABASE", "cut")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")

# String de conexão com o banco de dados
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
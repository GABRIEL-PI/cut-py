#!/usr/bin/env python3
"""
Script para executar a aplicação em modo de desenvolvimento
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def setup_environment():
    """Configura o ambiente de desenvolvimento"""
    # Verificar se os diretórios necessários existem
    for directory in ['downloads', 'cuts', 'temp']:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório '{directory}' verificado/criado")
    
    # Verificar se o banco de dados está inicializado
    try:
        db_init_script = os.path.join('database', 'init_db.py')
        if os.path.exists(db_init_script):
            print("🔧 Inicializando banco de dados...")
            subprocess.run([sys.executable, db_init_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao inicializar o banco de dados: {e}")
        return False
    
    return True

def run_app():
    """Executa a aplicação"""
    try:
        print("🚀 Iniciando aplicação...")
        subprocess.run([sys.executable, 'main.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar a aplicação: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⛔ Aplicação interrompida pelo usuário")
        return True

if __name__ == "__main__":
    print("🔧 Configurando ambiente de desenvolvimento...")
    if setup_environment():
        run_app()
    else:
        print("❌ Falha ao configurar o ambiente")
        sys.exit(1)
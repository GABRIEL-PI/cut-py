#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_DATABASE = os.getenv("DB_DATABASE", "cut")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")

def init_database():
    """Inicializa o banco de dados"""
    try:
        # Conectar ao servidor MySQL (sem especificar o banco de dados)
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        with connection.cursor() as cursor:
            # Criar banco de dados se não existir
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE}")
            print(f"✅ Banco de dados '{DB_DATABASE}' verificado/criado")
            
            # Usar o banco de dados
            cursor.execute(f"USE {DB_DATABASE}")
            
            # Ler e executar o script SQL
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
            with open(schema_path, "r") as f:
                sql_script = f.read()
                
            # Executar cada comando separadamente
            for command in sql_script.split(';'):
                if command.strip():
                    cursor.execute(command)
            
            connection.commit()
            print("✅ Esquema do banco de dados criado com sucesso")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar o banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Inicializando banco de dados...")
    success = init_database()
    sys.exit(0 if success else 1)
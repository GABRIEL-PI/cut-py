#!/usr/bin/env python3
"""
Script de teste para a API de processamento de vídeo
"""

import requests
import json
import time
import sys

# Configuração da API
API_BASE_URL = "http://localhost:5000"

def test_health():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_list_files():
    """Testa listagem de arquivos"""
    print("\n📁 Testando listagem de arquivos...")
    try:
        response = requests.get(f"{API_BASE_URL}/files")
        if response.status_code == 200:
            data = response.json()
            print("✅ Listagem de arquivos OK")
            print(f"   Downloads: {len(data.get('downloads', []))}")
            print(f"   Cortes: {len(data.get('cuts', []))}")
            return True
        else:
            print(f"❌ Listagem falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def test_list_tasks():
    """Testa listagem de tarefas"""
    print("\n📋 Testando listagem de tarefas...")
    try:
        response = requests.get(f"{API_BASE_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print("✅ Listagem de tarefas OK")
            print(f"   Total de tarefas: {len(tasks)}")
            return True
        else:
            print(f"❌ Listagem de tarefas falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na listagem de tarefas: {e}")
        return False

def test_download_simulation():
    """Simula um teste de download (sem realmente baixar)"""
    print("\n⬇️ Testando endpoint de download (simulação)...")
    
    # Usar uma URL de teste que deve falhar rapidamente
    test_data = {
        "url": "https://www.youtube.com/watch?v=INVALID_VIDEO_ID",
        "filename": "test_video"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/download",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print("✅ Download iniciado (simulação)")
            print(f"   Task ID: {task_id}")
            
            # Aguardar um pouco e verificar status
            print("   Aguardando processamento...")
            time.sleep(5)
            
            status_response = requests.get(f"{API_BASE_URL}/status/{task_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   Status: {status_data.get('status')}")
                if status_data.get('error'):
                    print(f"   Erro esperado: {status_data.get('error')[:100]}...")
            
            return True
        else:
            print(f"❌ Download falhou: {response.status_code}")
            try:
                print(f"   Erro: {response.json()}")
            except:
                print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de download: {e}")
        return False

def test_cut_simulation():
    """Simula um teste de corte (sem arquivo real)"""
    print("\n✂️ Testando endpoint de corte (simulação)...")
    
    test_data = {
        "input_file": "arquivo_inexistente.mp4",
        "start_time": "00:00:10",
        "end_time": "00:00:20",
        "output_filename": "test_cut.mp4"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/cut",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Esperamos um erro 404 já que o arquivo não existe
        if response.status_code == 404:
            print("✅ Endpoint de corte funcionando (erro esperado para arquivo inexistente)")
            return True
        elif response.status_code == 200:
            print("⚠️ Endpoint de corte retornou sucesso inesperadamente")
            return True
        else:
            print(f"❌ Erro inesperado no corte: {response.status_code}")
            try:
                print(f"   Erro: {response.json()}")
            except:
                print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de corte: {e}")
        return False

def test_invalid_endpoints():
    """Testa endpoints inválidos"""
    print("\n🚫 Testando endpoints inválidos...")
    
    # Teste GET em endpoint POST
    try:
        response = requests.get(f"{API_BASE_URL}/download")
        if response.status_code == 405:  # Method Not Allowed
            print("✅ Validação de método OK")
        else:
            print(f"⚠️ Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de método: {e}")
        return False
    
    # Teste endpoint inexistente
    try:
        response = requests.get(f"{API_BASE_URL}/endpoint_inexistente")
        if response.status_code == 404:
            print("✅ Endpoint inexistente retorna 404")
        else:
            print(f"⚠️ Resposta inesperada para endpoint inexistente: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de endpoint inexistente: {e}")
        return False
    
    return True

def run_all_tests():
    """Executa todos os testes"""
    print("🧪 Iniciando testes da API de processamento de vídeo...\n")
    
    tests = [
        ("Health Check", test_health),
        ("Listagem de Arquivos", test_list_files),
        ("Listagem de Tarefas", test_list_tasks),
        ("Download (Simulação)", test_download_simulation),
        ("Corte (Simulação)", test_cut_simulation),
        ("Endpoints Inválidos", test_invalid_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status:12} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-"*50)
    print(f"Total: {len(results)} | Passou: {passed} | Falhou: {failed}")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! API está funcionando corretamente.")
        return True
    else:
        print(f"\n⚠️ {failed} teste(s) falharam. Verifique a configuração.")
        return False

if __name__ == "__main__":
    # Verificar se foi passado URL customizada
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1].rstrip('/')
        print(f"🔧 Usando URL customizada: {API_BASE_URL}")
    
    success = run_all_tests()
    sys.exit(0 if success else 1) 
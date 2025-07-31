#!/usr/bin/env python3
"""
Script para testar a implementação do mysql_repository.py
"""

import os
import sys
from datetime import datetime

# Adicionar diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.video_repository import VideoRepository
from app.models.video import Video

def test_repository():
    """Testa as operações básicas do repositório"""
    print("🧪 Iniciando testes do VideoRepository...\n")
    
    # Inicializar repositório
    repo = VideoRepository()
    
    # Testar criação
    print("⬇️ Testando criação de vídeo...")
    video_id = repo.create_video(
        platform="youtube",
        url="https://www.youtube.com/watch?v=test123",
        filename="test_video.mp4",
        status="pending"
    )
    
    if video_id:
        print(f"✅ Vídeo criado com ID: {video_id}")
    else:
        print("❌ Falha ao criar vídeo")
        return False
    
    # Testar busca por ID
    print("\n🔍 Testando busca por ID...")
    video = repo.find(video_id)
    
    if video and video.get('id') == video_id:
        print(f"✅ Vídeo encontrado: {video}")
    else:
        print("❌ Falha ao buscar vídeo por ID")
        return False
    
    # Testar atualização de status
    print("\n🔄 Testando atualização de status...")
    updated = repo.update_status(video_id, "downloading")
    
    if updated:
        print("✅ Status atualizado com sucesso")
        video = repo.find(video_id)
        print(f"   Novo status: {video.get('status')}")
    else:
        print("❌ Falha ao atualizar status")
        return False
    
    # Testar busca por URL
    print("\n🔍 Testando busca por URL...")
    video_by_url = repo.find_by_url("https://www.youtube.com/watch?v=test123")
    
    if video_by_url and video_by_url.get('id') == video_id:
        print(f"✅ Vídeo encontrado por URL: {video_by_url.get('id')}")
    else:
        print("❌ Falha ao buscar vídeo por URL")
        return False
    
    # Testar busca por status
    print("\n🔍 Testando busca por status...")
    videos_by_status = repo.find_by_status("downloading")
    
    if videos_by_status and len(videos_by_status) > 0:
        print(f"✅ Vídeos encontrados por status: {len(videos_by_status)}")
    else:
        print("❌ Falha ao buscar vídeos por status")
        return False
    
    # Testar busca recente
    print("\n🔍 Testando busca de vídeos recentes...")
    recent_videos = repo.get_recent_videos(limit=5)
    
    if recent_videos and len(recent_videos) > 0:
        print(f"✅ Vídeos recentes encontrados: {len(recent_videos)}")
    else:
        print("❌ Falha ao buscar vídeos recentes")
        return False
    
    # Testar exclusão
    print("\n🗑️ Testando exclusão de vídeo...")
    deleted = repo.delete_video(video_id)
    
    if deleted:
        print("✅ Vídeo excluído com sucesso")
        video = repo.find(video_id)
        if not video:
            print("   Confirmado: vídeo não existe mais")
        else:
            print("❌ Vídeo ainda existe após exclusão")
            return False
    else:
        print("❌ Falha ao excluir vídeo")
        return False
    
    print("\n🎉 Todos os testes do repositório passaram!")
    return True

if __name__ == "__main__":
    try:
        success = test_repository()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)
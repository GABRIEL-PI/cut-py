import yt_dlp
import argparse
import sys
import json
import traceback

def progress_hook(d):
    if d['status'] == 'downloading':
        # Calcular e exibir o progresso
        if d.get('total_bytes'):
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            progress_info = {
                'status': 'downloading',
                'percent': round(percent, 2),
                'downloaded_bytes': d['downloaded_bytes'],
                'total_bytes': d['total_bytes'],
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
            # Imprimir como JSON para ser capturado pelo processo pai
            print(json.dumps(progress_info), flush=True)
    elif d['status'] == 'finished':
        progress_info = {
            'status': 'finished',
            'filename': d.get('filename', '')
        }
        print(json.dumps(progress_info), flush=True)
    elif d['status'] == 'error':
        # Reportar erros durante o download
        error_info = {
            'status': 'error',
            'error': d.get('error', 'Erro desconhecido durante o download')
        }
        print(json.dumps(error_info), flush=True)

def main():
    parser = argparse.ArgumentParser(description="Download de vídeos do YouTube")
    parser.add_argument("--url", type=str, required=True, help="URL do vídeo a ser baixado")
    parser.add_argument("--output", type=str, required=True, help="Caminho para salvar o vídeo")

    args = parser.parse_args()

    ydl_opts = {
        'format': 'best',
        'outtmpl': args.output,
        'quiet': False,  # Permitir saída para capturar progresso
        'no_warnings': False,
        'no_call_home': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        yt = yt_dlp.YoutubeDL(ydl_opts)
        yt.download([args.url])
    except yt_dlp.utils.DownloadError as e:
        # Capturar erros específicos de download
        error_info = {
            'status': 'error',
            'error': str(e),
            'error_type': 'download_error',
            'url': args.url
        }
        print(json.dumps(error_info), flush=True)
        # Imprimir o erro para stderr para ser capturado pelo processo pai
        print(f"ERRO DE DOWNLOAD: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Capturar qualquer outro erro
        error_details = traceback.format_exc()
        error_info = {
            'status': 'error',
            'error': str(e),
            'error_type': 'general_error',
            'details': error_details,
            'url': args.url
        }
        print(json.dumps(error_info), flush=True)
        # Imprimir o erro para stderr para ser capturado pelo processo pai
        print(f"ERRO GERAL: {str(e)}\n{error_details}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
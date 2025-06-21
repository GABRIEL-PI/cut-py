import yt_dlp
import argparse

def main():
    parser = argparse.ArgumentParser(description="Download de vídeos do YouTube")
    parser.add_argument("--url", type=str, required=True, help="URL do vídeo a ser baixado")
    parser.add_argument("--output", type=str, required=True, help="Caminho para salvar o vídeo")

    args = parser.parse_args()

    ydl_opts = {
        'format': 'best',
        'outtmpl': args.output,
        'quiet': True,
        'no_warnings': True,
        'no_call_home': True,
    }
    yt = yt_dlp.YoutubeDL(ydl_opts)
    yt.download([args.url])

if __name__ == "__main__":
    main()
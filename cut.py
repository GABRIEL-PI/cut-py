from moviepy import VideoFileClip
import argparse
import os

def time_to_seconds(t):
    h, m, s = map(int, t.split(':'))
    return h * 3600 + m * 60 + s

def main():
    parser = argparse.ArgumentParser(description="Comando para realizar cortes de vídeo em Python")
    parser.add_argument("--start", type=str, required=True, help="Tempo inicial do corte. Ex: 01:00:00 (Formato HH:MM:SS)")
    parser.add_argument("--end", type=str, required=True, help="Tempo final do corte. Ex: 01:05:00 (Formato HH:MM:SS)")
    parser.add_argument("--input", type=str, required=True, help="Arquivo a ser cortado")
    parser.add_argument("--output", type=str, required=True, help="Local a ser salvo")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Erro: Arquivo {args.input} não encontrado.")
        exit(1)

    start_time = time_to_seconds(args.start)
    end_time = time_to_seconds(args.end)

    if start_time >= end_time:
        print("Erro: O tempo inicial deve ser menor que o tempo final.")
        exit(1)

    try:
        print(f"Carregando vídeo: {args.input}")
        
        clip = VideoFileClip(args.input)
        
        if end_time > clip.duration:
            print(f"Aviso: Tempo final ({end_time}s) maior que duração do vídeo ({clip.duration}s)")
            end_time = clip.duration
        
        if start_time >= clip.duration:
            print(f"Erro: Tempo inicial ({start_time}s) é maior que a duração do vídeo ({clip.duration}s)")
            clip.close()
            exit(1)

        print(f"Cortando vídeo de {args.start} até {args.end}")
        
        subclip = clip.subclipped(start_time, end_time)

        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        subclip.write_videofile(
            args.output, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True
        )

        print(f"Vídeo cortado salvo em: {args.output}")
        
        subclip.close()
        clip.close()

    except Exception as e:
        print(f"Erro ao processar o vídeo: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
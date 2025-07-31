# Documentação da API de Processamento de Vídeos

Este documento contém a documentação de todas as rotas disponíveis na API de Processamento de Vídeos, incluindo os payloads necessários para cada endpoint.

## Índice

- [Verificação de Saúde](#verificação-de-saúde)
- [Vídeos](#vídeos)
  - [Baixar Vídeo](#baixar-vídeo)
  - [Cortar Vídeo](#cortar-vídeo)
  - [Baixar e Cortar Vídeo](#baixar-e-cortar-vídeo)
  - [Obter Vídeo](#obter-vídeo)
  - [Listar Todos os Vídeos](#listar-todos-os-vídeos)
- [Tarefas](#tarefas)
  - [Obter Status da Tarefa](#obter-status-da-tarefa)
  - [Listar Todas as Tarefas](#listar-todas-as-tarefas)
- [Arquivos](#arquivos)
  - [Listar Arquivos](#listar-arquivos)
  - [Baixar Arquivo](#baixar-arquivo)

## Verificação de Saúde

### GET /health

Verifica se a API está funcionando corretamente.

**Resposta:**

```json
{
  "status": "ok",
  "message": "Video Processing API is running",
  "timestamp": "2023-06-01T12:00:00.000000"
}
```

## Vídeos

### POST /videos

Inicia o download de um vídeo a partir de uma URL.

**Payload:**

```json
{
  "url": "https://www.youtube.com/watch?v=exemplo",
  "filename": "meu_video.mp4" // Opcional
}
```

**Resposta:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": 1,
  "status": "started",
  "message": "Download iniciado",
  "output_path": "D:\Sistemas\cut-py\downloads\meu_video.mp4"
}
```

### POST /videos/{video_id}/cut

Inicia o corte de um vídeo previamente baixado.

**Payload:**

```json
{
  "video_id": 1,
  "start_time": "00:01:30",
  "end_time": "00:02:45",
  "output_filename": "meu_corte.mp4" // Opcional
}
```

**Resposta:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": 1,
  "status": "started",
  "message": "Corte iniciado",
  "output_path": "D:\Sistemas\cut-py\cuts\meu_corte.mp4"
}
```

**Códigos de Erro:**

- `400 Bad Request`: Campos obrigatórios ausentes ou vídeo não está pronto para corte
- `404 Not Found`: Vídeo não encontrado ou arquivo de entrada não encontrado

### POST /videos/download-and-cut

Baixa e corta um vídeo em uma única operação.

**Payload:**

```json
{
  "url": "https://www.youtube.com/watch?v=exemplo",
  "start_time": "00:01:30",
  "end_time": "00:02:45",
  "filename": "meu_video.mp4", // Opcional
  "output_filename": "meu_corte.mp4" // Opcional
}
```

**Resposta:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": 1,
  "status": "started",
  "message": "Download e corte iniciados",
  "download_path": "D:\Sistemas\cut-py\downloads\meu_video.mp4",
  "cut_path": "D:\Sistemas\cut-py\cuts\meu_corte.mp4"
}
```

### GET /videos/{video_id}

Obtém informações sobre um vídeo específico.

**Resposta:**

```json
{
  "id": 1,
  "platform": "youtube",
  "url": "https://www.youtube.com/watch?v=exemplo",
  "filename": "meu_video.mp4",
  "status": "completed",
  "duration": 180.5,
  "created_at": "2023-06-01T12:00:00.000000",
  "updated_at": "2023-06-01T12:05:00.000000"
}
```

**Códigos de Erro:**

- `404 Not Found`: Vídeo não encontrado

### GET /videos

Lista todos os vídeos disponíveis.

**Parâmetros de Query:**

- `limit` (opcional): Limita o número de vídeos retornados

**Resposta:**

```json
[
  {
    "id": 1,
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=exemplo1",
    "filename": "video1.mp4",
    "status": "completed",
    "duration": 180.5,
    "created_at": "2023-06-01T12:00:00.000000",
    "updated_at": "2023-06-01T12:05:00.000000"
  },
  {
    "id": 2,
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@usuario/video/exemplo2",
    "filename": "video2.mp4",
    "status": "downloading",
    "duration": null,
    "created_at": "2023-06-01T13:00:00.000000",
    "updated_at": "2023-06-01T13:00:00.000000"
  }
]
```

## Tarefas

### GET /tasks/{task_id}

Obtém o status de uma tarefa específica.

**Resposta:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": 1,
  "type": "download",
  "status": "completed",
  "url": "https://www.youtube.com/watch?v=exemplo",
  "output_path": "D:\Sistemas\cut-py\downloads\meu_video.mp4",
  "created_at": "2023-06-01T12:00:00.000000",
  "output": "Download concluído com sucesso.",
  "error": ""
}
```

**Códigos de Erro:**

- `404 Not Found`: Tarefa não encontrada

### GET /tasks

Lista todas as tarefas.

**Resposta:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "video_id": 1,
    "type": "download",
    "status": "completed",
    "url": "https://www.youtube.com/watch?v=exemplo1",
    "output_path": "D:\Sistemas\cut-py\downloads\video1.mp4",
    "created_at": "2023-06-01T12:00:00.000000",
    "output": "Download concluído com sucesso.",
    "error": ""
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "video_id": 2,
    "type": "cut",
    "status": "running",
    "input_file": "D:\Sistemas\cut-py\downloads\video2.mp4",
    "output_path": "D:\Sistemas\cut-py\cuts\corte2.mp4",
    "start_time": "00:01:30",
    "end_time": "00:02:45",
    "created_at": "2023-06-01T13:00:00.000000",
    "output": "Iniciando corte...",
    "error": ""
  }
]
```

## Arquivos

### GET /files

Lista todos os arquivos disponíveis nas pastas de downloads e cortes.

**Resposta:**

```json
{
  "downloads": [
    "video1.mp4",
    "video2.mp4"
  ],
  "cuts": [
    "corte1.mp4",
    "corte2.mp4"
  ]
}
```

### GET /files/{file_type}/{filename}

Baixa um arquivo específico.

**Parâmetros de URL:**

- `file_type`: Tipo do arquivo (`download` ou `cut`)
- `filename`: Nome do arquivo

**Resposta:**

O arquivo solicitado como um download.

**Códigos de Erro:**

- `400 Bad Request`: Tipo de arquivo inválido
- `404 Not Found`: Arquivo não encontrado

## Códigos de Status

- `200 OK`: Requisição bem-sucedida
- `400 Bad Request`: Parâmetros inválidos ou ausentes
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Formatos

- Tempos: Formato HH:MM:SS (horas:minutos:segundos)
- IDs de tarefas: UUIDs (formato string)
- IDs de vídeos: Inteiros
- Timestamps: ISO 8601 (YYYY-MM-DDTHH:MM:SS.ssssss)
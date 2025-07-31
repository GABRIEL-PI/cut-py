# Plataforma de Download e Corte de Vídeos Multiplataforma

Este projeto implementa uma API para download e corte de vídeos de múltiplas plataformas (YouTube, Instagram, TikTok, Pinterest), seguindo princípios de arquitetura limpa e SOLID.

---

## 🧾 **PRD – Plataforma de Download e Corte de Vídeos Multiplataforma**

### 📌 Visão Geral

O objetivo do sistema é permitir que usuários façam o download de vídeos e shorts de plataformas como YouTube, Instagram, TikTok e Pinterest, armazenem localmente, e realizem cortes automatizados. O sistema será modular, escalável, seguindo os princípios **SOLID** e utilizando MySQL como persistência de dados.

---

## Como Usar
1. 1.
   Configure o arquivo .env com suas credenciais de banco de dados.
2. 2.
   Execute python database/init_db.py para inicializar o banco de dados.
3. 3.
   Execute python main.py para iniciar a aplicação.
4. 4.
   A API estará disponível em http://localhost:5000 .
Você também pode usar o script run_dev.py para configurar o ambiente e iniciar a aplicação em um único comando.

Para testar a implementação do repositório MySQL, execute python test_mysql_repository.py .

A aplicação agora está pronta para uso, com todas as funcionalidades mantidas, mas usando o mysql_repository.py em vez do SQLAlchemy para operações de banco de dados.

## 🎯 Objetivos

* Baixar vídeos e shorts de múltiplas plataformas.
* Armazenar metadados em MySQL.
* Cortar vídeos com base em regras (duração, highlights, AI etc.).
* Organizar arquivos por pastas (`downloads/`, `cuts/`, `temp/`).
* Fornecer uma API REST para controlar e monitorar tarefas.
* Estrutura modular com controllers, services, repositories, routers.

---

## 🏗️ Arquitetura de Diretórios

```
/
├── app/
│   ├── config.py
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── routes/
│   └── utils/
├── downloads/
├── cuts/
├── temp/
├── tests/
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧩 Componentes Técnicos

### 🔧 **Dependências Sugeridas**

| Finalidade             | Pacote Python                     |
| ---------------------- | --------------------------------- |
| YouTube downloads      | `pytube` ou `yt_dlp`              |
| TikTok/Instagram/etc.  | `yt_dlp` (suporte genérico amplo) |
| Processamento de vídeo | `moviepy` ou `ffmpeg-python`      |
| API                    | `FastAPI` ou `Flask`              |
| ORM                    | `SQLAlchemy`                      |
| Banco de dados         | MySQL                             |
| Variáveis de ambiente  | `python-dotenv`                   |
| Log                    | `loguru` ou `logging`             |

---

## 🔌 Integrações

### 🟣 YouTube / TikTok / Instagram / Pinterest

Usar `yt_dlp`, que já suporta a maioria dessas plataformas:

```python
from yt_dlp import YoutubeDL

ydl_opts = {
    'outtmpl': 'downloads/%(id)s.%(ext)s',
}
with YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
```

---

## ⚙️ Funcionalidades

### 1. 🎥 **Download de Vídeo**

* Input: URL
* Output: Arquivo em `/downloads/`
* Salva no banco: ID do vídeo, plataforma, status, caminho do arquivo, duração, etc.

### 2. ✂️ **Corte de Vídeo**

* Input: ID do vídeo, tempo de início/fim ou lógica automática (ex: shorts)
* Output: `/cuts/video_id_cut.mp4`

### 3. 📁 **Gerenciamento de Arquivos**

* Limpeza da pasta `/temp/`
* Organização por data ou ID

### 4. 📦 **API REST**

* `POST /videos`: iniciar download
* `GET /videos/{id}`: status e metadados
* `POST /videos/{id}/cut`: cortar vídeo
* `GET /videos/{id}/file`: baixar arquivo

---

## 🧱 Estrutura SOLID (Exemplo de Separação de Camadas)

### ✔️ `Controllers`: Validação + resposta HTTP

### ✔️ `Services`: Regras de negócio (ex: baixar, cortar)

### ✔️ `Repositories`: Abstração de banco

### ✔️ `Models`: ORM (SQLAlchemy)

### ✔️ `Routes`: Define os endpoints (FastAPI)

### ✔️ `Utils`: Execução de comandos, ferramentas auxiliares

---

## 🔐 Banco de Dados (MySQL)

### Tabela: `videos`

```sql
CREATE TABLE videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    url TEXT,
    filename VARCHAR(255),
    status ENUM('pending', 'downloading', 'completed', 'error'),
    duration FLOAT,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## 🧪 Testes

Cobertura com `pytest` para:

* `services/`: lógica de download/corte
* `controllers/`: entrada e saída da API
* `repositories/`: comunicação com o banco

---

## 🐳 Dockerfile (exemplo)

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 🚀 Plano de Expansão

* Suporte a IA para sugerir cortes automáticos (Whisper + Gemini)
* Dashboard web com React ou Svelte
* Autenticação com JWT
* Fila de tarefas com Celery ou Redis

---

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.11+
- MySQL
- FFmpeg

### Configuração

1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/cut-py.git
cd cut-py
```

2. Instale as dependências

```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com suas credenciais de banco de dados

```
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=cut
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

4. Inicialize o banco de dados

```bash
python database/init_db.py
```

### Executando a aplicação

```bash
python main.py
```

A API estará disponível em `http://localhost:5000`

### Testando a aplicação

```bash
python test_api.py
```

### Testando o repositório MySQL

```bash
python test_mysql_repository.py
```

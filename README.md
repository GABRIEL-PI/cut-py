# Sistema de Processamento de Vídeo para n8n

Este projeto permite baixar e cortar vídeos do YouTube através de uma API REST, integrando perfeitamente com n8n para automação de workflows.

## 🚀 Funcionalidades

- **Download de vídeos**: Baixa vídeos do YouTube usando yt-dlp
- **Corte de vídeos**: Corta vídeos em segmentos específicos usando MoviePy
- **API REST**: Interface HTTP para integração com n8n
- **Processamento assíncrono**: Tarefas executadas em background
- **Monitoramento**: Endpoints para verificar status das tarefas
- **Gerenciamento de arquivos**: Listagem e limpeza automática
- **Dockerizado**: Pronto para deploy com Docker/Portainer

## 📋 Pré-requisitos

- Docker e Docker Compose
- n8n rodando (se não tiver, o docker-compose pode criar um)
- Portainer (opcional, para gerenciamento visual)

## 🔧 Instalação e Configuração

### 1. Clone e Configure o Projeto

```bash
# Já está no seu diretório do projeto
# Certifique-se que todos os arquivos estão presentes
ls -la
```

### 2. Configure a Rede do Docker

Se você já tem n8n rodando, primeiro descubra qual rede ele está usando:

```bash
# Listar redes existentes
docker network ls

# Ver detalhes de uma rede específica (substitua pelo nome da sua rede n8n)
docker network inspect NOME_DA_REDE_N8N
```

Edite o `docker-compose.yml` e ajuste a seção `networks`:

```yaml
networks:
  n8n-network:
    driver: bridge
    external: true  # Se já existe
    # name: NOME_DA_SUA_REDE_N8N  # Descomente e ajuste se necessário
```

### 3. Deploy com Docker Compose

```bash
# Construir e iniciar o serviço
docker-compose up -d --build

# Verificar se está rodando
docker-compose ps

# Ver logs se necessário
docker-compose logs -f video-processor
```

### 4. Deploy no Portainer (Alternativo)

1. Acesse seu Portainer
2. Vá em "Stacks"
3. Clique em "Add stack"
4. Cole o conteúdo do `docker-compose.yml`
5. Ajuste as variáveis conforme necessário
6. Deploy

## 📡 API Endpoints

### Base URL
```
http://localhost:5000
```
(ou `http://video-processor:5000` de dentro do n8n)

### Endpoints Disponíveis

#### 1. Health Check
```http
GET /health
```

#### 2. Download de Vídeo
```http
POST /download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "filename": "meu_video" // opcional
}
```

#### 3. Cortar Vídeo
```http
POST /cut
Content-Type: application/json

{
  "input_file": "meu_video.mp4",
  "start_time": "00:01:30",
  "end_time": "00:02:45",
  "output_filename": "corte_meu_video.mp4" // opcional
}
```

#### 4. Download e Corte em Uma Operação
```http
POST /download-and-cut
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "start_time": "00:00:30",
  "end_time": "00:01:00",
  "filename": "video_original", // opcional
  "output_filename": "video_cortado.mp4" // opcional
}
```

#### 5. Consultar Status de Tarefa
```http
GET /status/{task_id}
```

#### 6. Listar Todas as Tarefas
```http
GET /tasks
```

#### 7. Listar Arquivos
```http
GET /files
```

#### 8. Download de Arquivo
```http
GET /download/{filename}
```

#### 9. Limpeza de Arquivos
```http
POST /clean
Content-Type: application/json

{
  "days": 7 // remove arquivos mais antigos que X dias
}
```

## 🔄 Integração com n8n

### Método 1: Usando HTTP Request Nodes

1. **Adicione um nó "HTTP Request"** no seu workflow
2. **Configure a URL**: `http://video-processor:5000/download-and-cut`
3. **Método**: POST
4. **Headers**: `Content-Type: application/json`
5. **Body**: JSON com os parâmetros necessários

Exemplo de configuração:
```json
{
  "url": "{{ $json.video_url }}",
  "start_time": "{{ $json.start_time }}",
  "end_time": "{{ $json.end_time }}"
}
```

### Método 2: Importando Workflows Prontos

Use os exemplos do arquivo `n8n-workflows-examples.json`:

1. Abra o n8n
2. Vá em "Workflows"
3. Clique em "Import"
4. Cole o JSON do workflow desejado
5. Ajuste conforme necessário

### Exemplos de Uso no n8n

#### Workflow Básico de Download e Corte:
1. **Manual Trigger** → Inicia manualmente
2. **HTTP Request** → Chama `/download-and-cut`
3. **Wait** → Aguarda processamento
4. **HTTP Request** → Verifica status
5. **IF** → Verifica se completou
6. **Function** → Processa resultado

#### Webhook para Automação:
1. **Webhook Trigger** → Recebe dados externos
2. **Function** → Processa dados recebidos
3. **HTTP Request** → Chama API de vídeo
4. **Wait** → Aguarda processamento
5. **Email/Slack** → Notifica conclusão

## 🗂️ Estrutura de Arquivos

```
/app/
├── downloads/          # Vídeos baixados
├── cuts/              # Vídeos cortados
├── temp/              # Arquivos temporários
├── app.py             # API Flask
├── download.py        # Script de download
├── cut.py             # Script de corte
└── requirements.txt   # Dependências
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Adicione no `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=production
  - MAX_DOWNLOAD_SIZE=500MB  # Tamanho máximo de download
  - CLEANUP_INTERVAL=24h     # Intervalo de limpeza automática
  - ALLOWED_DOMAINS=youtube.com,youtu.be  # Domínios permitidos
```

### Volumes Personalizados

```yaml
volumes:
  - /caminho/host/downloads:/app/downloads
  - /caminho/host/cuts:/app/cuts
```

### Recursos e Limites

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

## 🚨 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs video-processor

# Verificar se a porta está em uso
netstat -tulpn | grep :5000
```

### Erro de rede no n8n
```bash
# Verificar se estão na mesma rede
docker network ls
docker network inspect NOME_DA_REDE
```

### Erro de permissão
```bash
# Ajustar permissões dos diretórios
sudo chown -R 1000:1000 downloads cuts temp
```

### Erro de dependências
```bash
# Reconstruir imagem
docker-compose build --no-cache video-processor
```

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:5000/health
```

### Status do Container
```bash
docker-compose ps
docker stats video-processor
```

### Logs em Tempo Real
```bash
docker-compose logs -f video-processor
```

## 🔐 Segurança

### Recomendações
- Use HTTPS em produção
- Configure autenticação se necessário
- Limite o tamanho dos uploads
- Monitore o uso de disco
- Configure backup dos vídeos importantes

### Firewall
```bash
# Permitir apenas conexões locais na porta 5000
sudo ufw allow from 172.0.0.0/8 to any port 5000
```

## 📈 Performance

### Otimizações
- Use SSD para melhor I/O
- Ajuste a memória conforme necessário
- Configure limpeza automática
- Use proxy reverso (nginx)

### Exemplo de configuração nginx:
```nginx
location /video-api/ {
    proxy_pass http://localhost:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    client_max_body_size 500M;
}
```

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs primeiro
2. Consulte a seção de troubleshooting
3. Teste os endpoints individualmente
4. Verifique a conectividade de rede

## 📝 Changelog

- v1.0.0: Versão inicial com API REST e integração n8n
- Suporte a download e corte de vídeos
- Processamento assíncrono
- Monitoramento de tarefas
- Limpeza automática de arquivos 
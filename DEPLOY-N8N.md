# 🚀 Deploy Rápido - Integração com n8n Existente

## ⚡ Passos Rápidos

### 1. Preparar Ambiente
```bash
# Dar permissão ao script helper
chmod +x deploy-helper.sh

# Configurar ambiente
./deploy-helper.sh setup
```

### 2. Construir e Iniciar
```bash
# Construir imagem
./deploy-helper.sh build

# Iniciar serviço
./deploy-helper.sh start
```

### 3. Testar
```bash
# Verificar status
./deploy-helper.sh status

# Executar testes
./deploy-helper.sh test

# Ver informações de integração
./deploy-helper.sh info
```

## 🔗 Configuração no n8n

### URLs para HTTP Request Nodes:
- **Download**: `http://video-processor:5000/download`
- **Corte**: `http://video-processor:5000/cut`
- **Download + Corte**: `http://video-processor:5000/download-and-cut`
- **Status**: `http://video-processor:5000/status/{task_id}`

### Exemplo de Payload:
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "start_time": "00:00:30",
  "end_time": "00:01:00",
  "output_filename": "meu_video_cortado.mp4"
}
```

## 📁 Estrutura de Arquivos

```
/root/n8n-videos/          # Compartilhado com n8n
├── video1.mp4             # Downloads
├── video2.mp4
└── cuts/                  # Cortes
    ├── corte1.mp4
    └── corte2.mp4
```

## 🔧 Configuração Avançada

### Expor via Traefik (Opcional)
No `docker-compose.video.yml`, descomente as labels do Traefik e configure:
```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.video-processor.rule=Host(`video.${DOMAIN_NAME}`)
  # ... outras configurações
```

### Variáveis de Ambiente
Crie um arquivo `.env` com:
```bash
DOMAIN_NAME=seudominio.com
SUBDOMAIN=n8n
```

## 🛠️ Comandos Úteis

```bash
# Ver logs em tempo real
./deploy-helper.sh logs

# Verificar rede e containers
./deploy-helper.sh network

# Fazer backup dos vídeos
./deploy-helper.sh backup

# Parar serviços
./deploy-helper.sh stop

# Reiniciar serviços
./deploy-helper.sh restart

# Atualizar sistema
./deploy-helper.sh update
```

## 🔍 Troubleshooting

### Erro de rede
```bash
# Verificar se a rede n8n existe
docker network ls | grep n8n

# Criar rede se necessário
docker network create n8n
```

### Erro de permissão
```bash
# Ajustar permissões
sudo chown -R 1000:1000 /root/n8n-videos
```

### Container não inicia
```bash
# Ver logs detalhados
./deploy-helper.sh logs

# Verificar status
./deploy-helper.sh status
```

## 🎯 Workflow n8n Exemplo

1. **Webhook** → Recebe URL do vídeo
2. **HTTP Request** → POST para `http://video-processor:5000/download-and-cut`
3. **Wait** → Aguarda 2 minutos
4. **HTTP Request** → GET para `http://video-processor:5000/status/{task_id}`
5. **IF** → Verifica se status == "completed"
6. **Email/Slack** → Notifica sucesso

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:5000/health
```

### Listar Arquivos
```bash
curl http://localhost:5000/files
```

### Status de Tarefas
```bash
curl http://localhost:5000/tasks
```

## 🔐 Segurança

- API está na rede interna `n8n`
- Apenas containers na mesma rede podem acessar
- Opcional: Configurar autenticação básica via Traefik
- Arquivos salvos em `/root/n8n-videos` (acesso restrito)

---

**🎉 Pronto! Seu sistema de processamento de vídeo está integrado com n8n!** 
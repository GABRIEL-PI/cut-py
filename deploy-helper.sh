#!/bin/bash

# Deploy Helper - Sistema de Processamento de Vídeo para n8n
# Este script ajuda com tarefas comuns de deploy e manutenção

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variáveis
PROJECT_NAME="video-processor"
NETWORK_NAME="n8n"
COMPOSE_FILE="docker-compose.video.yml"

echo -e "${BLUE}🚀 Deploy Helper - Sistema de Processamento de Vídeo${NC}"
echo "=================================================="

# Função para mostrar ajuda
show_help() {
    echo "Uso: ./deploy-helper.sh [COMANDO]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  setup           - Configurar ambiente inicial"
    echo "  build           - Construir imagem Docker"
    echo "  start           - Iniciar serviços"
    echo "  stop            - Parar serviços"
    echo "  restart         - Reiniciar serviços"
    echo "  logs            - Ver logs em tempo real"
    echo "  status          - Ver status dos containers"
    echo "  test            - Executar testes da API"
    echo "  clean           - Limpeza de containers e volumes"
    echo "  network         - Verificar/criar rede Docker"
    echo "  backup          - Fazer backup dos vídeos"
    echo "  restore         - Restaurar backup"
    echo "  update          - Atualizar sistema"
    echo "  info|integration - Mostrar informações de integração"
    echo "  help            - Mostrar esta ajuda"
}

# Função para verificar dependências
check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependências...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker não encontrado. Instale o Docker primeiro.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose não encontrado. Instale o Docker Compose primeiro.${NC}"
        exit 1
    fi
    
    # Verificar se o arquivo compose existe
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Arquivo $COMPOSE_FILE não encontrado.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependências OK${NC}"
}

# Função para configurar ambiente
setup_environment() {
    echo -e "${BLUE}⚙️ Configurando ambiente para integração com n8n...${NC}"
    
    # Verificar se a rede n8n existe
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        echo -e "${YELLOW}⚠️ Rede Docker '$NETWORK_NAME' não encontrada.${NC}"
        echo -e "${YELLOW}Certifique-se que seu n8n está rodando com a rede '$NETWORK_NAME'${NC}"
        read -p "Criar rede $NETWORK_NAME agora? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            docker network create $NETWORK_NAME
            echo -e "${GREEN}✅ Rede $NETWORK_NAME criada${NC}"
        else
            echo -e "${YELLOW}⚠️ Continuando sem criar rede...${NC}"
        fi
    else
        echo -e "${GREEN}✅ Rede Docker $NETWORK_NAME já existe${NC}"
    fi
    
    # Verificar se o diretório /root/n8n-videos existe
    if [ ! -d "/root/n8n-videos" ]; then
        echo -e "${YELLOW}⚠️ Diretório /root/n8n-videos não encontrado.${NC}"
        echo -e "${BLUE}Criando diretórios necessários...${NC}"
        sudo mkdir -p /root/n8n-videos/cuts
        sudo chown -R 1000:1000 /root/n8n-videos
    fi
    
    # Criar diretórios locais alternativos
    mkdir -p downloads cuts temp
    sudo chown -R 1000:1000 downloads cuts temp
    
    echo -e "${GREEN}✅ Ambiente configurado${NC}"
    echo -e "${BLUE}💡 Dica: Verifique se as variáveis DOMAIN_NAME e SUBDOMAIN estão configuradas no seu .env${NC}"
}

# Função para construir imagem
build_image() {
    echo -e "${BLUE}🔨 Construindo imagem Docker...${NC}"
    docker-compose -f $COMPOSE_FILE build --no-cache $PROJECT_NAME
    echo -e "${GREEN}✅ Imagem construída${NC}"
}

# Função para iniciar serviços
start_services() {
    echo -e "${BLUE}🚀 Iniciando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE up -d
    
    echo -e "${YELLOW}⏳ Aguardando serviços iniciarem...${NC}"
    sleep 10
    
    # Verificar se está rodando
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Serviços iniciados com sucesso${NC}"
        echo -e "${BLUE}📍 API disponível em:${NC}"
        echo -e "  - Interno (n8n): http://video-processor:5000"
        echo -e "  - Externo: http://localhost:5000"
        if [ -n "$DOMAIN_NAME" ]; then
            echo -e "  - Traefik: https://video.$DOMAIN_NAME (se configurado)"
        fi
    else
        echo -e "${RED}❌ Erro ao iniciar serviços${NC}"
        docker-compose -f $COMPOSE_FILE logs
        exit 1
    fi
}

# Função para parar serviços
stop_services() {
    echo -e "${BLUE}🛑 Parando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE down
    echo -e "${GREEN}✅ Serviços parados${NC}"
}

# Função para reiniciar serviços
restart_services() {
    echo -e "${BLUE}🔄 Reiniciando serviços...${NC}"
    docker-compose -f $COMPOSE_FILE restart
    echo -e "${GREEN}✅ Serviços reiniciados${NC}"
}

# Função para ver logs
show_logs() {
    echo -e "${BLUE}📝 Mostrando logs em tempo real...${NC}"
    echo -e "${YELLOW}Pressione Ctrl+C para sair${NC}"
    docker-compose -f $COMPOSE_FILE logs -f $PROJECT_NAME
}

# Função para mostrar status
show_status() {
    echo -e "${BLUE}📊 Status dos containers:${NC}"
    docker-compose -f $COMPOSE_FILE ps
    
    echo -e "\n${BLUE}🌐 Rede Docker:${NC}"
    if docker network ls | grep -q "$NETWORK_NAME"; then
        echo -e "${GREEN}✅ Rede $NETWORK_NAME ativa${NC}"
        # Mostrar containers na rede
        echo -e "\n${BLUE}Containers na rede $NETWORK_NAME:${NC}"
        docker network inspect $NETWORK_NAME --format '{{range .Containers}}{{.Name}} - {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null || echo "Nenhum container"
    else
        echo -e "${RED}❌ Rede $NETWORK_NAME não encontrada${NC}"
    fi
    
    echo -e "\n${BLUE}💾 Uso de espaço:${NC}"
    if [ -d "/root/n8n-videos" ]; then
        echo "N8N Videos: $(sudo du -sh /root/n8n-videos 2>/dev/null | cut -f1 || echo 'N/A')"
    fi
    if [ -d "downloads" ]; then
        echo "Downloads locais: $(du -sh downloads | cut -f1)"
    fi
    if [ -d "cuts" ]; then
        echo "Cortes locais: $(du -sh cuts | cut -f1)"
    fi
    
    echo -e "\n${BLUE}🌐 Conectividade:${NC}"
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API respondendo em localhost:5000${NC}"
    else
        echo -e "${RED}❌ API não está respondendo${NC}"
    fi
    
    # Testar conectividade interna
    if docker exec video-processor curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API respondendo internamente${NC}"
    else
        echo -e "${YELLOW}⚠️ API pode não estar respondendo internamente${NC}"
    fi
}

# Função para executar testes
run_tests() {
    echo -e "${BLUE}🧪 Executando testes da API...${NC}"
    
    if [ -f "test_api.py" ]; then
        if command -v python3 &> /dev/null; then
            # Verificar se requests está instalado
            if python3 -c "import requests" 2>/dev/null; then
                python3 test_api.py
            else
                echo -e "${YELLOW}⚠️ Biblioteca 'requests' não encontrada. Instalando...${NC}"
                pip3 install requests
                python3 test_api.py
            fi
        else
            echo -e "${RED}❌ Python3 não encontrado${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Arquivo test_api.py não encontrado${NC}"
        exit 1
    fi
}

# Função para limpeza
clean_system() {
    echo -e "${BLUE}🧹 Limpando sistema...${NC}"
    
    read -p "Isso vai remover todos os containers e volumes. Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Limpeza concluída${NC}"
    else
        echo -e "${YELLOW}Limpeza cancelada${NC}"
    fi
}

# Função para verificar rede
check_network() {
    echo -e "${BLUE}📡 Verificando configuração de rede...${NC}"
    
    if docker network ls | grep -q "$NETWORK_NAME"; then
        echo -e "${GREEN}✅ Rede $NETWORK_NAME existe${NC}"
        
        # Mostrar containers na rede
        echo -e "\n${BLUE}Containers na rede:${NC}"
        docker network inspect $NETWORK_NAME --format '{{range .Containers}}{{.Name}} - {{.IPv4Address}}{{"\n"}}{{end}}'
        
    else
        echo -e "${YELLOW}⚠️ Rede $NETWORK_NAME não existe${NC}"
        echo -e "${BLUE}Esta rede deve ser criada pelo seu stack n8n.${NC}"
        read -p "Criar rede agora para testes? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            docker network create $NETWORK_NAME
            echo -e "${GREEN}✅ Rede criada${NC}"
        fi
    fi
}

# Função para backup
backup_data() {
    echo -e "${BLUE}💾 Fazendo backup dos dados...${NC}"
    
    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="backup_videos_$BACKUP_DATE.tar.gz"
    
    # Incluir dados do n8n se existirem
    BACKUP_PATHS=""
    if [ -d "/root/n8n-videos" ]; then
        BACKUP_PATHS="$BACKUP_PATHS /root/n8n-videos"
    fi
    if [ -d "downloads" ]; then
        BACKUP_PATHS="$BACKUP_PATHS downloads"
    fi
    if [ -d "cuts" ]; then
        BACKUP_PATHS="$BACKUP_PATHS cuts"
    fi
    
    if [ -n "$BACKUP_PATHS" ]; then
        sudo tar -czf "$BACKUP_FILE" $BACKUP_PATHS 2>/dev/null || true
        echo -e "${GREEN}✅ Backup criado: $BACKUP_FILE${NC}"
        
        # Mostrar tamanho do backup
        BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
        echo -e "${BLUE}📏 Tamanho do backup: $BACKUP_SIZE${NC}"
    else
        echo -e "${YELLOW}⚠️ Nenhum dado para backup${NC}"
    fi
}

# Função para restaurar backup
restore_data() {
    echo -e "${BLUE}📂 Restaurando backup...${NC}"
    
    # Listar backups disponíveis
    BACKUPS=(backup_videos_*.tar.gz)
    if [ ${#BACKUPS[@]} -eq 0 ] || [ ! -f "${BACKUPS[0]}" ]; then
        echo -e "${RED}❌ Nenhum backup encontrado${NC}"
        exit 1
    fi
    
    echo "Backups disponíveis:"
    for i in "${!BACKUPS[@]}"; do
        echo "$((i+1)). ${BACKUPS[$i]}"
    done
    
    read -p "Escolha um backup (1-${#BACKUPS[@]}): " choice
    
    if [[ "$choice" -ge 1 && "$choice" -le ${#BACKUPS[@]} ]]; then
        SELECTED_BACKUP="${BACKUPS[$((choice-1))]}"
        echo -e "${BLUE}Restaurando: $SELECTED_BACKUP${NC}"
        
        sudo tar -xzf "$SELECTED_BACKUP"
        echo -e "${GREEN}✅ Backup restaurado${NC}"
    else
        echo -e "${RED}❌ Seleção inválida${NC}"
        exit 1
    fi
}

# Função para atualizar sistema
update_system() {
    echo -e "${BLUE}🔄 Atualizando sistema...${NC}"
    
    # Parar serviços
    docker-compose -f $COMPOSE_FILE down
    
    # Reconstruir imagem
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # Iniciar serviços
    docker-compose -f $COMPOSE_FILE up -d
    
    echo -e "${GREEN}✅ Sistema atualizado${NC}"
}

# Função para mostrar informações de integração
show_integration_info() {
    echo -e "${BLUE}🔗 Informações de Integração com n8n:${NC}"
    echo ""
    echo -e "${YELLOW}URLs para usar no n8n:${NC}"
    echo "  - http://video-processor:5000/download"
    echo "  - http://video-processor:5000/cut"
    echo "  - http://video-processor:5000/download-and-cut"
    echo "  - http://video-processor:5000/status/{task_id}"
    echo "  - http://video-processor:5000/files"
    echo ""
    echo -e "${YELLOW}Exemplo de payload para download-and-cut:${NC}"
    echo '{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "start_time": "00:01:00",
  "end_time": "00:02:00",
  "output_filename": "meu_corte.mp4"
}'
    echo ""
    echo -e "${YELLOW}Arquivos salvos em:${NC}"
    echo "  - Downloads: /root/n8n-videos/ (compartilhado com n8n)"
    echo "  - Cortes: /root/n8n-videos/cuts/"
}

# Processar argumentos
case "${1:-help}" in
    setup)
        check_dependencies
        setup_environment
        ;;
    build)
        check_dependencies
        build_image
        ;;
    start)
        check_dependencies
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_system
        ;;
    network)
        check_network
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data
        ;;
    update)
        update_system
        ;;
    info|integration)
        show_integration_info
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconhecido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Operação concluída!${NC}" 
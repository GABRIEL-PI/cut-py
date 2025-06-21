FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não root
RUN useradd -m -u 1000 videouser

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .
COPY download.py .
COPY cut.py .

# Criar diretórios necessários
RUN mkdir -p /app/downloads /app/cuts /app/temp && \
    chown -R videouser:videouser /app

# Mudar para usuário não root
USER videouser

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

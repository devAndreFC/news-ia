# Imagem base oficial do Python
FROM python:3.11-slim

# Configurações para evitar problemas de buffering e locale
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Criar diretório da aplicação
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para melhor aproveitamento de cache)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Comando padrão
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2"]

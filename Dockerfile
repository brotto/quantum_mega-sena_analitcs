FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto
COPY . .

# Expor porta 8000 para a API
EXPOSE 8000

# Healthcheck para o Easypanel saber se o app está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para iniciar a API
CMD ["uvicorn", "api_megasena:app", "--host", "0.0.0.0", "--port", "8000"]

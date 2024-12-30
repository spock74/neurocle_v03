# Imagem base
FROM python:3.12-slim

# Configuração do diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Configurar timeout do Uvicorn
ENV UVICORN_TIMEOUT=300

# Usar o Gunicorn como servidor WSGI com workers do Uvicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "300", "--bind", "0.0.0.0:8000"]

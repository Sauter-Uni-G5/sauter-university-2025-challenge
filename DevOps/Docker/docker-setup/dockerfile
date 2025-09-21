# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY src/ ./src/

# Expõe a porta
EXPOSE 8000

# Rodar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

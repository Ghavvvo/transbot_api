# Dockerfile para TransBot API
# Usa embeddings precomputados - sin ChromaDB
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Variables de entorno por defecto
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=5000



# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación (incluye precomputed_embeddings/)
COPY . .

# Exponer puerto (configurable vía ENV)
EXPOSE ${PORT}

# Healthcheck para verificar que la API responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health')"

# Comando para ejecutar la aplicación
CMD gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 app:app

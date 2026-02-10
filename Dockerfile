# Dockerfile para despliegue en Render.com
# Versión SIMPLIFICADA - ya no necesita ChromaDB ni discos persistentes
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para SentenceTransformers
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación (incluye precomputed_embeddings/)
COPY . .

# Los embeddings precomputados ya vienen en el código fuente
# No necesitas inicialización adicional!

# Exponer puerto
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]

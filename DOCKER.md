# 🐳 Despliegue con Docker

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd transbot_api

# 2. Configurar variables de entorno
cp .env.docker .env
# Editar .env y agregar tu MISTRAL_API_KEY

# 3. Construir y ejecutar
docker-compose up -d

# 4. Verificar
curl http://localhost:5000/api/health
```

### Opción 2: Docker sin Compose

```bash
# 1. Construir imagen
docker build -t transbot-api .

# 2. Ejecutar contenedor
docker run -d \
  --name transbot-api \
  -p 5000:5000 \
  -e MISTRAL_API_KEY=tu_api_key_aqui \
  -e FLASK_ENV=production \
  transbot-api

# 3. Verificar logs
docker logs -f transbot-api
```

## 📋 Variables de Entorno

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `MISTRAL_API_KEY` | API Key de Mistral AI | ✅ Sí | - |
| `FLASK_ENV` | Entorno (development/production) | No | production |
| `EMBEDDING_MODEL` | Modelo de embeddings | No | paraphrase-multilingual-MiniLM-L12-v2 |
| `PORT` | Puerto del servidor | No | 5000 |

## 🔧 Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Reconstruir imagen
docker-compose up -d --build

# Ver estadísticas
docker stats transbot-api

# Entrar al contenedor
docker exec -it transbot-api bash
```

## 🏗️ Dockerfile

El Dockerfile incluye:
- ✅ Python 3.12 slim (imagen ligera)
- ✅ Dependencias del sistema para SentenceTransformers
- ✅ Embeddings precomputados (incluidos en la imagen)
- ✅ Healthcheck automático
- ✅ Optimizado para producción

## 🔒 Seguridad

### Buenas Prácticas

1. **Variables de Entorno**
   ```bash
   # NUNCA subas .env a Git
   # Usa docker secrets en producción
   docker secret create mistral_key mistral_api_key.txt
   ```

2. **Usuario no-root (opcional)**
   ```dockerfile
   # Agregar al Dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

3. **Escaneo de vulnerabilidades**
   ```bash
   docker scan transbot-api
   ```

## 📊 Recursos

El contenedor usa por defecto:
- **CPU:** 0.5-1 core
- **RAM:** 1-2 GB
- **Disco:** ~1.5 GB (imagen + cache)

Ajusta según necesidad en `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

## 🌐 Despliegue en Producción

### Docker Swarm

```bash
docker stack deploy -c docker-compose.yml transbot
```

### Kubernetes

Ver [kubernetes.yaml](kubernetes.yaml) para configuración completa.

### AWS ECS / Azure Container Instances

1. Sube la imagen a un registry:
   ```bash
   docker tag transbot-api:latest tu-registry/transbot-api:latest
   docker push tu-registry/transbot-api:latest
   ```

2. Configura variables de entorno en la consola del servicio

## 🆘 Troubleshooting

### Contenedor no inicia
```bash
# Ver logs detallados
docker logs transbot-api

# Verificar healthcheck
docker inspect transbot-api | grep -A 5 Health
```

### Error "No module named..."
```bash
# Reconstruir sin cache
docker-compose build --no-cache
```

### Puerto ya en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8080:5000"  # Host:Container
```

## 📝 Notas

- Los embeddings están incluidos en la imagen (no requiere volúmenes)
- El healthcheck verifica `/api/health` cada 30 segundos
- El contenedor se reinicia automáticamente con `restart: unless-stopped`

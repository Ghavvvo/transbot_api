# 🚀 Guía de Despliegue en Render.com

## 📋 Requisitos Previos
- Cuenta en [Render.com](https://render.com)
- Repositorio Git con el código (GitHub, GitLab o Bitbucket)
- API Key de Mistral AI

## 🔧 Configuración de ChromaDB Persistente

### ⚠️ IMPORTANTE: Persistencia de Datos
Render.com tiene un sistema de archivos **efímero** por defecto. Para mantener tu base de datos ChromaDB con los embeddings, **DEBES usar un disco persistente**.

### Opciones de Despliegue

#### **Opción 1: Usando render.yaml (Recomendado)**

1. **Sube tu código a Git** con todos los archivos incluyendo `render.yaml`

2. **En Render Dashboard:**
   - Ve a "Blueprints"
   - Conecta tu repositorio
   - Render detectará automáticamente el `render.yaml`
   - El disco persistente se creará automáticamente

3. **Configura las variables de entorno:**
   - `MISTRAL_API_KEY`: Tu API key de Mistral
   - `FLASK_ENV`: production

4. **Deploy automático** 🎉

#### **Opción 2: Configuración Manual**

1. **Crear nuevo Web Service:**
   - Conecta tu repositorio Git
   - Runtime: **Python**
   - Build Command: `pip install -r requirements.txt && python init_embeddings.py`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

2. **Crear Disco Persistente:**
   - En tu servicio, ve a "Disks"
   - Click "Add Disk"
   - Name: `chroma-db-disk`
   - Mount Path: `/opt/render/project/src/chroma_db`
   - Size: **1 GB** (suficiente para embeddings)
   - Click "Create"

3. **Variables de Entorno:**
   ```
   MISTRAL_API_KEY=tu_api_key_aquí
   FLASK_ENV=production
   PYTHON_VERSION=3.12.0
   ```

4. **Deploy** 🚀

## 💾 ¿Qué es el Disco Persistente?

El disco persistente:
- ✅ Mantiene los datos entre reinicios
- ✅ Conserva los embeddings de ChromaDB
- ✅ Solo se crea UNA VEZ (no se borra)
- ✅ Se monta en la ruta especificada

**Costo:**
- Plan Free: NO incluye discos persistentes
- Plan Starter ($7/mes): Incluye discos persistentes
- Discos adicionales: ~$0.25/GB/mes

## 🔄 Alternativas si NO quieres pagar

### Opción A: Reinicializar en cada deploy
Modifica `app.py` para que siempre ejecute `init_embeddings.py` al inicio:

```python
# Al inicio de app.py
if not os.path.exists('chroma_db') or not os.listdir('chroma_db'):
    print("Inicializando embeddings...")
    import subprocess
    subprocess.run(['python', 'init_embeddings.py'])
```

**Desventaja:** Tarda ~2-5 minutos en cada reinicio

### Opción B: Usar servicio externo de ChromaDB
- [Chroma Cloud](https://www.trychroma.com/cloud) (beta)
- [Hosted ChromaDB](https://docs.trychroma.com/deployment/docker)

### Opción C: Usar otro hosting con persistencia gratis
- **Railway.app**: Ofrece volúmenes persistentes
- **Fly.io**: Ofrece volúmenes persistentes en plan gratis
- **Vercel + Supabase**: Para vectores (requiere más cambios)

## 🧪 Verificar que funciona

Después del deploy, prueba:

```bash
# Health check
curl https://tu-app.onrender.com/api/health

# Probar búsqueda
curl -X POST https://tu-app.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es el límite de velocidad?"}'
```

## 📊 Monitoreo

En Render Dashboard puedes ver:
- Logs en tiempo real
- Uso del disco persistente
- Métricas de CPU/RAM
- Historial de deploys

## ⚡ Optimizaciones

1. **Workers de Gunicorn:** Ajusta según tu plan
   - Free: 1 worker
   - Starter: 2-4 workers

2. **Timeout:** Para generación de preguntas, usa timeout alto (120s)

3. **Cache de modelos:** Los modelos de SentenceTransformer se cachean automáticamente

## 🆘 Problemas Comunes

### "ChromaDB está vacío después del deploy"
- ✅ Verifica que el disco persistente esté montado
- ✅ Revisa que `init_embeddings.py` se ejecutó en el build

### "Error: No module named 'gunicorn'"
- ✅ Verifica que `gunicorn` esté en `requirements.txt`

### "Timeout en requests"
- ✅ Aumenta el timeout de gunicorn: `--timeout 180`

### "Disco lleno"
- ✅ Aumenta el tamaño del disco en Settings > Disks

## 📝 Notas Finales

- **Backup:** Render hace backups automáticos de discos persistentes
- **Escalabilidad:** Puedes aumentar el tamaño del disco sin perder datos
- **Migraciones:** Los datos persisten entre deploys y actualizaciones

¡Buena suerte con tu despliegue! 🚀


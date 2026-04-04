# 🚗 TransBot API

API REST para consultas sobre la Ley 109 (Código de Seguridad Vial de Cuba) con RAG (Retrieval-Augmented Generation) usando Mistral AI.

## 🚀 Características

- ✅ **Búsqueda semántica** de artículos de la Ley 109
- ✅ **Generación de respuestas** conversacionales con IA
- ✅ **Generación de pruebas** de tránsito personalizadas
- ✅ **Embeddings precomputados** - sin necesidad de base de datos externa
- ✅ **Listo para producción** - funciona en plan gratuito de Render.com

## 📋 Requisitos

- Python 3.12+
- API Key de Mistral AI ([obtener aquí](https://console.mistral.ai/))

## 🔧 Instalación Local

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd transbot_api

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu MISTRAL_API_KEY

# 5. Ejecutar servidor
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 🌐 Endpoints Disponibles

### Health Check
```bash
GET /api/health
```

### Chat RAG - Consultas conversacionales
```bash
POST /api/chat
Content-Type: application/json

{
  "query": "¿Cuál es el límite de velocidad en zona urbana?",
  "max_articles": 5
}
```

### Búsqueda de artículos
```bash
POST /api/search
Content-Type: application/json

{
  "query": "velocidad máxima",
  "n_results": 5
}
```

### Generar prueba de tránsito
```bash
POST /api/generate-test
Content-Type: application/json

{
  "num_questions": 20
}
```

### Obtener artículo específico
```bash
GET /api/articles/<article_id>
```

### Estadísticas
```bash
GET /api/stats
```

## 🚀 Despliegue en Render.com

### Opción 1: Blueprint (Recomendado)

1. Haz fork del repositorio
2. En [Render Dashboard](https://dashboard.render.com/) → "Blueprints"
3. Conecta tu repositorio
4. Render detecta `render.yaml` automáticamente
5. Configura la variable de entorno `MISTRAL_API_KEY`
6. ¡Deploy! 🎉

### Opción 2: Manual

1. New Web Service → Conecta tu repositorio
2. **Runtime:** Python
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
5. **Environment Variables:**
   - `MISTRAL_API_KEY` = tu_api_key
   - `FLASK_ENV` = production
   - `EMBEDDING_MODEL` = paraphrase-multilingual-MiniLM-L12-v2 (opcional)
6. **Plan:** Free ✅
7. Deploy

**Nota:** Los embeddings precomputados están incluidos en el repositorio, ¡no necesitas configuración adicional!

## 🐳 Despliegue con Docker

Ver [DOCKER.md](DOCKER.md) para instrucciones completas.

### Inicio Rápido con Docker Compose

```bash
# 1. Configurar variables de entorno
cp .env.docker .env
# Editar .env y agregar tu MISTRAL_API_KEY

# 2. Ejecutar
docker-compose up -d

# 3. Verificar
curl http://localhost:5000/api/health
```

### Ejecutar con Docker

```bash
docker build -t transbot-api .
docker run -d -p 5000:5000 \
  -e MISTRAL_API_KEY=tu_api_key \
  transbot-api
```

## 📦 Estructura del Proyecto

```
transbot_api/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── render.yaml                     # Configuración para Render.com
├── Dockerfile                      # Para despliegue en Docker
├── articulos_ley_109.json          # Base de datos de artículos
├── precomputed_embeddings/         # Embeddings precomputados (en Git)
│   ├── embeddings.npy              # Vectores numpy
│   ├── index.json                  # Índice de artículos
│   └── metadata.json               # Metadatos del modelo
├── services/
│   ├── precomputed_embedding_service.py  # Servicio de embeddings
│   └── rag_service.py              # Servicio RAG con Mistral
└── precompute_embeddings.py        # Script para regenerar embeddings
```

## 🔄 Regenerar Embeddings

Solo necesitas regenerar los embeddings si actualizas `articulos_ley_109.json`:

```bash
python precompute_embeddings.py

# Luego hacer commit
git add precomputed_embeddings/
git commit -m "update: regenerar embeddings"
git push
```

## 🛠️ Tecnologías

- **Flask** - Framework web
- **Mistral AI** - Generación de respuestas con LLM
- **SentenceTransformers** - Modelo de embeddings multilingüe
- **NumPy + scikit-learn** - Búsqueda por similitud coseno
- **Gunicorn** - Servidor WSGI para producción

## 📝 Licencia

MIT

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un issue primero para discutir los cambios que te gustaría realizar.

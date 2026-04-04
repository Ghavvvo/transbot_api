# 🚀 Guía de Despliegue SIMPLIFICADA - Embeddings Precomputados

## ✅ NUEVA SOLUCIÓN: Embeddings Estáticos en Git

Ya **NO necesitas ChromaDB ni discos persistentes**. Los embeddings están precomputados y versionados en Git como archivos estáticos.

### 🎯 Ventajas de esta solución:

- ✅ **Funciona en plan GRATUITO** de Render.com
- ✅ **No necesita disco persistente** ($0 extra)
- ✅ **Deploy instantáneo** - sin tiempo de inicialización
- ✅ **Versionado en Git** - embeddings como código
- ✅ **Reproducible** - mismos embeddings siempre
- ✅ **Más rápido** - carga directa desde archivos

## 📋 Pasos para Implementar

### 1. Precomputar los Embeddings (UNA SOLA VEZ)

En tu máquina local, ejecuta:

```bash
python precompute_embeddings.py
```

Esto creará la carpeta `precomputed_embeddings/` con:
- `embeddings.npy` - Vectores precomputados (~2-5 MB)
- `index.json` - Mapeo de artículos
- `metadata.json` - Información del modelo

### 2. Versionar en Git

```bash
git add precomputed_embeddings/
git add precompute_embeddings.py
git add services/precomputed_embedding_service.py
git add app.py requirements.txt render.yaml Dockerfile .gitignore
git commit -m "feat: usar embeddings precomputados - elimina ChromaDB"
git push origin main
```

### 3. Desplegar en Render.com

#### Opción A: Blueprint (render.yaml)
1. En Render Dashboard → "Blueprints"
2. Conecta tu repositorio
3. Render detecta `render.yaml` automáticamente
4. Configura `MISTRAL_API_KEY`
5. ¡Deploy! 🎉

#### Opción B: Manual
1. New Web Service → Conecta repo
2. **Runtime:** Python
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
5. **Environment Variables:**
   - `MISTRAL_API_KEY` = tu_api_key
   - `FLASK_ENV` = production
6. **Plan:** Free ✅
7. Deploy

## 🔄 ¿Cuándo Regenerar los Embeddings?

Solo necesitas regenerar cuando:
- La ley cambie (nuevo artículo, modificación)
- Quieras cambiar el modelo de embeddings
- Actualices `articulos_ley_109.json`

Pasos:
```bash
# 1. Actualizar articulos_ley_109.json
# 2. Regenerar embeddings
python precompute_embeddings.py

# 3. Versionar y deploy
git add precomputed_embeddings/
git commit -m "update: regenerar embeddings con nueva ley"
git push
```

## 📊 Comparación: ChromaDB vs Precomputado

| Característica | ChromaDB | Precomputado |
|----------------|----------|--------------|
| **Costo Render** | $7/mes (disco) | $0 (gratis) |
| **Tiempo deploy** | 2-5 min | <30 seg |
| **Persistencia** | Disco externo | En código |
| **Versionado** | No | Sí (Git) |
| **Velocidad** | Medio | Rápido |
| **Setup** | Complejo | Simple |

## 🧪 Probar Localmente

```bash
# 1. Crear virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Precomputar embeddings (si no existen)
python precompute_embeddings.py

# 4. Ejecutar servidor
python app.py

# 5. Probar
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"¿Cuál es el límite de velocidad?\"}"
```

## 📦 Estructura de Archivos

```
transbot_api/
├── precomputed_embeddings/      ← NUEVO: Embeddings estáticos (va en Git)
│   ├── embeddings.npy          ← Vectores numpy (2-5 MB)
│   ├── index.json              ← Artículos + metadata
│   └── metadata.json           ← Info del modelo
├── services/
│   ├── precomputed_embedding_service.py  ← NUEVO: Servicio ligero
│   ├── embedding_service.py    ← VIEJO: Ya no se usa
│   └── rag_service.py          ← Sin cambios
├── app.py                      ← Actualizado
├── precompute_embeddings.py    ← NUEVO: Script de generación
├── articulos_ley_109.json      ← Fuente de datos
├── requirements.txt            ← Actualizado (+scikit-learn)
├── render.yaml                 ← Simplificado
└── Dockerfile                  ← Simplificado
```

## 🆘 Problemas Comunes

### "No se encontraron embeddings precomputados"
```bash
# Solución: Generar embeddings
python precompute_embeddings.py
```

### "Error: No module named 'sklearn'"
```bash
# Solución: Instalar scikit-learn
pip install scikit-learn==1.5.0
```

### Los embeddings son muy grandes para Git
Si `embeddings.npy` > 100 MB, considera:
1. **Git LFS** (Large File Storage)
2. **Descargar en build** desde S3/Google Drive
3. **Comprimir** el archivo numpy

Para este proyecto (~245 artículos), el archivo será ~2-5 MB ✅

## 🎯 Ventajas Técnicas

### Rendimiento
- **Carga:** ~0.5 seg (vs 5-10 seg ChromaDB)
- **Búsqueda:** Igual de rápida (numpy + cosine similarity)
- **Memoria:** Menor overhead

### Simplicidad
- Sin base de datos externa
- Sin configuración compleja
- Sin preocupaciones por persistencia

### DevOps
- Deploy atómico (código + datos juntos)
- Rollback fácil con Git
- No hay drift entre entornos

## 📝 Notas Finales

- ✅ **Plan gratis de Render** es suficiente
- ✅ **No necesitas pagar por discos**
- ✅ **Deployment más rápido y confiable**
- ✅ **Los embeddings son inmutables** (la ley no cambia constantemente)

¡Esta es la mejor solución para tu caso de uso! 🚀


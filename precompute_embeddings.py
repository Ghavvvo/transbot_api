#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para precomputar y guardar los embeddings como archivos estáticos
Esto permite versionar los embeddings en Git y elimina la necesidad de ChromaDB en producción
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

def precompute_embeddings():
    """Precomputa los embeddings y los guarda como archivos estáticos"""

    print("🚀 Precomputando embeddings para la Ley 109...")

    # Rutas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, "articulos_ley_109.json")
    output_dir = os.path.join(current_dir, "precomputed_embeddings")

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Cargar artículos
    print(f"📂 Cargando artículos desde: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"📖 {len(articles)} artículos cargados")

    # Inicializar modelo desde variable de entorno o default
    model_name = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
    print(f"🔧 Cargando modelo: {model_name}")
    model = SentenceTransformer(model_name)

    # Crear embeddings
    print("⚙️  Generando embeddings...")
    texts = [article['contenido'] for article in articles]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_tensor=False)

    # Guardar embeddings como numpy array
    embeddings_file = os.path.join(output_dir, "embeddings.npy")
    np.save(embeddings_file, embeddings)
    print(f"✅ Embeddings guardados en: {embeddings_file}")

    # Guardar índice (mapeo de ID a índice de embedding)
    index_data = {
        "articles": [
            {
                "id": article['id'],
                "contenido": article['contenido'],
                "embedding_index": i
            }
            for i, article in enumerate(articles)
        ],
        "model_name": model_name,
        "total_articles": len(articles),
        "embedding_dimension": embeddings.shape[1]
    }

    index_file = os.path.join(output_dir, "index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Índice guardado en: {index_file}")

    # Guardar también metadata compacta
    metadata_file = os.path.join(output_dir, "metadata.json")
    metadata = {
        "model_name": model_name,
        "total_articles": len(articles),
        "embedding_dimension": int(embeddings.shape[1]),
        "embeddings_shape": list(embeddings.shape),
        "file_size_mb": round(os.path.getsize(embeddings_file) / (1024 * 1024), 2)
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadata guardada en: {metadata_file}")

    # Mostrar estadísticas
    print("\n📊 Estadísticas:")
    print(f"   - Total de artículos: {len(articles)}")
    print(f"   - Dimensión de embeddings: {embeddings.shape[1]}")
    print(f"   - Tamaño del archivo: {metadata['file_size_mb']} MB")
    print(f"   - Modelo usado: {model_name}")

    print("\n✅ ¡Embeddings precomputados exitosamente!")
    print("   Estos archivos se pueden versionar en Git y usar directamente en producción.")
    print("   Ya no necesitas ChromaDB ni discos persistentes.")

if __name__ == "__main__":
    precompute_embeddings()


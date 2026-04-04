"""
Servicio de embeddings LIGERO que usa embeddings precomputados
"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import random
from sklearn.metrics.pairwise import cosine_similarity

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrecomputedEmbeddingService:
    def __init__(self, precomputed_dir: str = "./precomputed_embeddings", model_name: str = None):
        """
        Inicializa el servicio usando embeddings precomputados

        Args:
            precomputed_dir: Directorio con los embeddings precomputados
            model_name: Nombre del modelo de embeddings (opcional, usa env o default)
        """
        self.precomputed_dir = precomputed_dir
        # Usar modelo desde env, parámetro, o default
        self.model_name = model_name or os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
        self.model = None
        self.embeddings = None
        self.articles = None
        self.metadata = None

        self._load_precomputed_data()
        self._initialize_model()

    def _load_precomputed_data(self):
        """Carga los embeddings y metadata precomputados"""
        try:
            # Cargar embeddings
            embeddings_file = os.path.join(self.precomputed_dir, "embeddings.npy")
            logger.info(f"Cargando embeddings desde: {embeddings_file}")
            self.embeddings = np.load(embeddings_file)

            # Cargar índice con artículos
            index_file = os.path.join(self.precomputed_dir, "index.json")
            logger.info(f"Cargando índice desde: {index_file}")
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                self.articles = index_data['articles']

            # Cargar metadata
            metadata_file = os.path.join(self.precomputed_dir, "metadata.json")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

            logger.info(f"✅ Embeddings precomputados cargados: {len(self.articles)} artículos")
            logger.info(f"   Dimensión: {self.embeddings.shape[1]}, Tamaño: {self.metadata['file_size_mb']} MB")

        except FileNotFoundError as e:
            logger.error(f"❌ No se encontraron embeddings precomputados en {self.precomputed_dir}")
            logger.error("   Ejecuta 'python precompute_embeddings.py' primero")
            raise
        except Exception as e:
            logger.error(f"Error al cargar embeddings precomputados: {e}")
            raise

    def _initialize_model(self):
        """Inicializa el modelo solo para queries nuevas"""
        try:
            logger.info(f"Cargando modelo para queries: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("✅ Modelo cargado")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise

    def search_similar_articles(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Busca artículos similares usando embeddings precomputados

        Args:
            query: Texto de consulta
            n_results: Número de resultados a devolver

        Returns:
            Diccionario con los resultados de la búsqueda
        """
        try:
            logger.info(f"Buscando artículos similares para: '{query[:50]}...'")

            # Crear embedding para la query
            query_embedding = self.model.encode([query], convert_to_tensor=False)

            # Calcular similitudes con todos los embeddings precomputados
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]

            # Obtener top N resultados
            top_indices = np.argsort(similarities)[::-1][:n_results]

            # Formatear resultados
            results = {
                "query": query,
                "results": []
            }

            for idx in top_indices:
                article = self.articles[idx]
                similarity = float(similarities[idx])

                results["results"].append({
                    "id": article['id'],
                    "contenido": article['contenido'],
                    "similarity_score": similarity,
                    "distance": 1 - similarity
                })

            logger.info(f"✅ Encontrados {len(results['results'])} resultados")
            return results

        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            raise

    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un artículo específico por su ID

        Args:
            article_id: ID del artículo

        Returns:
            Diccionario con los datos del artículo o None si no existe
        """
        for article in self.articles:
            if article['id'] == article_id:
                return article
        return None

    def get_random_articles(self, n: int = 20) -> List[Dict[str, Any]]:
        """
        Obtiene N artículos aleatorios

        Args:
            n: Número de artículos a obtener

        Returns:
            Lista de artículos aleatorios
        """
        try:
            n = min(n, len(self.articles))
            selected = random.sample(self.articles, n)
            logger.info(f"Seleccionados {n} artículos aleatorios")
            return selected
        except Exception as e:
            logger.error(f"Error al obtener artículos aleatorios: {e}")
            return []

    def get_all_articles(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los artículos

        Returns:
            Lista con todos los artículos
        """
        return self.articles

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección

        Returns:
            Diccionario con estadísticas
        """
        return {
            "total_articulos": len(self.articles),
            "embedding_dimension": self.metadata['embedding_dimension'],
            "model_name": self.metadata['model_name'],
            "file_size_mb": self.metadata['file_size_mb']
        }


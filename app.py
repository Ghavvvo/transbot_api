from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import asyncio
from dotenv import load_dotenv
from services.precomputed_embedding_service import PrecomputedEmbeddingService
from services.rag_service import RAGService

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://ghavvvo.github.io", "http://20.29.200.78:5000"])

# Inicializar servicios
embedding_service = None
rag_service = None

# Cargar API Key de Mistral desde variables de entorno
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

if not MISTRAL_API_KEY:
    print("⚠️  ADVERTENCIA: MISTRAL_API_KEY no está configurada en las variables de entorno")
    print("   Por favor, crea un archivo .env con tu API key o configura la variable de entorno")
else:
    # No imprimir la key completa, solo confirmar que existe
    print(f"✅ MISTRAL_API_KEY configurada (longitud: {len(MISTRAL_API_KEY)} caracteres)")

@app.route('/api/generate-test', methods=['POST'])
def generate_traffic_test():
    """Endpoint para generar una prueba de tránsito con preguntas aleatorias"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not rag_svc:
            return jsonify({'error': 'Servicio RAG no disponible'}), 500

        data = request.get_json() if request.get_json() else {}
        num_questions = data.get('num_questions', 20)

        # Validar número de preguntas
        if num_questions < 1 or num_questions > 50:
            return jsonify({'error': 'El número de preguntas debe estar entre 1 y 50'}), 400

        # Obtener artículos aleatorios
        random_articles = embedding_svc.get_random_articles(num_questions)
        
        if not random_articles:
            return jsonify({'error': 'No se pudieron obtener artículos para generar la prueba'}), 500

        # Usar asyncio para la llamada asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            questions = loop.run_until_complete(rag_svc.generate_test_questions(random_articles))
            
            if not questions:
                return jsonify({'error': 'No se pudieron generar preguntas para la prueba'}), 500

            result = {
                'test_id': f"test_{int(asyncio.get_event_loop().time())}" if asyncio.get_event_loop() else "test_001",
                'total_questions': len(questions),
                'questions': questions,
                'generated_at': asyncio.get_event_loop().time() if asyncio.get_event_loop() else None,
                'articles_used': [article['id'] for article in random_articles]
            }
            
            return jsonify(result)
            
        finally:
            loop.close()

    except Exception as e:
        return jsonify({'error': f'Error al generar la prueba: {str(e)}'}), 500


def initialize_services():
    """Inicializa los servicios de embeddings y RAG"""
    global embedding_service, rag_service

    if embedding_service is None:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            precomputed_dir = os.path.join(current_dir, "precomputed_embeddings")

            # Usar servicio de embeddings precomputados
            embedding_service = PrecomputedEmbeddingService(
                precomputed_dir=precomputed_dir
            )
            print("✅ Servicio de embeddings precomputados inicializado")

            # Inicializar RAG Service
            rag_service = RAGService(MISTRAL_API_KEY, embedding_service)
            print("✅ Servicio RAG con Mistral AI inicializado")

        except Exception as e:
            print(f"❌ Error al inicializar servicios: {e}")
            embedding_service = None
            rag_service = None

    return embedding_service, rag_service

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    embedding_svc, rag_svc = initialize_services()

    if embedding_svc and rag_svc:
        stats = embedding_svc.get_collection_stats()
        return jsonify({
            'status': 'ok',
            'database_ready': True,
            'total_articles': stats.get('total_documents', 0),
            'rag_enabled': True,
            'llm_provider': 'Mistral AI'
        })

    return jsonify({
        'status': 'ok',
        'database_ready': False,
        'total_articles': 0,
        'rag_enabled': False
    })

@app.route('/api/chat', methods=['POST'])
def chat_with_rag():
    """Endpoint principal para chat RAG - genera respuestas conversacionales"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not rag_svc:
            return jsonify({'error': 'Servicio RAG no disponible'}), 500

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Se requiere el campo "query"'}), 400

        query = data['query']
        max_articles = data.get('max_articles', 5)

        if not query.strip():
            return jsonify({'error': 'La consulta no puede estar vacía'}), 400

        # Usar asyncio para la llamada asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(rag_svc.generate_response(query, max_articles))
            return jsonify(result)
        finally:
            loop.close()

    except Exception as e:
        return jsonify({'error': f'Error en el chat RAG: {str(e)}'}), 500

@app.route('/api/search', methods=['POST'])
def search_articles():
    """Busca artículos similares (modo original para compatibilidad)"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not embedding_svc:
            return jsonify({'error': 'Servicio de embeddings no disponible'}), 500

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Se requiere el campo "query"'}), 400

        query = data['query']
        n_results = data.get('n_results', 5)

        if not query.strip():
            return jsonify({'error': 'La consulta no puede estar vacía'}), 400

        results = embedding_svc.search_similar_articles(query, n_results)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Error en la búsqueda: {str(e)}'}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Obtiene un artículo específico por su ID"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not embedding_svc:
            return jsonify({'error': 'Servicio de embeddings no disponible'}), 500

        article = embedding_svc.get_article_by_id(str(article_id))
        if article:
            return jsonify(article)
        else:
            return jsonify({'error': 'Artículo no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': f'Error al obtener artículo: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_database_stats():
    """Obtiene estadísticas de la base de datos"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not embedding_svc:
            return jsonify({'error': 'Servicio de embeddings no disponible'}), 500

        stats = embedding_svc.get_collection_stats()
        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@app.route('/api/rag/info', methods=['GET'])
def get_rag_info():
    """Obtiene información sobre las capacidades del sistema RAG"""
    try:
        embedding_svc, rag_svc = initialize_services()
        if not rag_svc:
            return jsonify({'error': 'Servicio RAG no disponible'}), 500

        info = rag_svc.get_service_info()
        return jsonify(info)

    except Exception as e:
        return jsonify({'error': f'Error al obtener información RAG: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

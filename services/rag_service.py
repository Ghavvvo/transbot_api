"""
Servicio RAG (Retrieval-Augmented Generation) usando Mistral AI
"""

import os
from typing import Dict, Any, List, Optional
import logging
from mistralai import Mistral
from .embedding_service import EmbeddingService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, mistral_api_key: str, embedding_service: EmbeddingService):
        """
        Inicializa el servicio RAG con Mistral AI

        Args:
            mistral_api_key: API key de Mistral AI
            embedding_service: Servicio de embeddings ya inicializado
        """
        self.mistral_client = Mistral(api_key=mistral_api_key)
        self.embedding_service = embedding_service
        self.model = "mistral-small-latest"  # Modelo eficiente y rápido

        logger.info("RAG Service inicializado con Mistral AI")

    def _create_system_prompt(self) -> str:
        """Crea el prompt del sistema para instruir al LLM"""
        return """Eres un asistente especializado en la Ley 109 - Código de Seguridad Vial de Cuba. 

Tu función es ayudar a los usuarios respondiendo preguntas sobre esta legislación de tránsito de manera clara, precisa y útil.

INSTRUCCIONES IMPORTANTES:
1. Responde ÚNICAMENTE basándote en los artículos proporcionados como contexto
2. Si la información no está en los artículos proporcionados, indícalo claramente
5. Usa un lenguaje profesional pero accesible
6. Estructura tu respuesta de manera organizada
7. Si hay múltiples artículos relevantes, organiza la información lógicamente

FORMATO DE RESPUESTA:
- Responde en texto plano sin usar formato Markdown
- NO uses asteriscos (*), guiones bajos (_) ni otros símbolos de formato
- Comienza con una respuesta directa a la pregunta
- Luego explica de manera natural y detallada
- Incluye los detalles específicos de los artículos
- Si es necesario, proporciona contexto adicional

Recuerda: Tu objetivo es ser un consultor legal confiable y preciso para temas de tránsito en Cuba."""

    def _create_user_prompt(self, query: str, articles: List[Dict[str, Any]]) -> str:
        """
        Crea el prompt del usuario con la consulta y el contexto de artículos

        Args:
            query: Pregunta del usuario
            articles: Lista de artículos relevantes encontrados

        Returns:
            Prompt formateado para el usuario
        """
        context = "\n\n".join([
            f"**Artículo {article['id']}:**\n{article['contenido']}"
            for article in articles
        ])

        return f"""CONTEXTO (Artículos de la Ley 109):
{context}

PREGUNTA DEL USUARIO:
{query}

Por favor, responde basándote únicamente en los artículos proporcionados arriba."""

    async def generate_response(self, query: str, max_articles: int = 5) -> Dict[str, Any]:
        """
        Genera una respuesta RAG completa para la consulta del usuario

        Args:
            query: Pregunta del usuario
            max_articles: Número máximo de artículos a recuperar

        Returns:
            Diccionario con la respuesta generada y metadatos
        """
        try:
            logger.info(f"Generando respuesta RAG para: '{query[:50]}...'")

            # 1. RETRIEVAL: Buscar artículos relevantes
            search_results = self.embedding_service.search_similar_articles(
                query, max_articles
            )

            if not search_results["results"]:
                return {
                    "query": query,
                    "response": "Lo siento, no encontré información relevante en la Ley 109 para responder tu consulta. Intenta reformular tu pregunta o usar términos más específicos.",
                    "sources": [],
                    "confidence": 0.0
                }

            # 2. GENERATION: Generar respuesta con Mistral
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(query, search_results["results"])

            # Llamada a Mistral AI
            response = self.mistral_client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Respuestas más deterministas para temas legales
                max_tokens=1000
            )

            generated_text = response.choices[0].message.content

            # 3. Preparar respuesta con metadatos
            sources = []
            for article in search_results["results"]:
                sources.append({
                    "id": article["id"],
                    "contenido": article["contenido"],
                    "similarity_score": article["similarity_score"],
                    "relevance": "Alta" if article["similarity_score"] > 0.7 else
                               "Media" if article["similarity_score"] > 0.5 else "Baja"
                })

            # Calcular confianza promedio
            avg_confidence = sum(s["similarity_score"] for s in sources) / len(sources) if sources else 0

            result = {
                "query": query,
                "response": generated_text,
                "sources": sources,
                "confidence": avg_confidence,
                "model_used": self.model,
                "articles_consulted": len(sources)
            }

            logger.info(f"Respuesta RAG generada exitosamente. Artículos consultados: {len(sources)}")
            return result

        except Exception as e:
            logger.error(f"Error en generación RAG: {e}")
            return {
                "query": query,
                "response": f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }

    async def generate_test_questions(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Genera preguntas de prueba de tránsito basadas en artículos de la ley

        Args:
            articles: Lista de artículos para generar preguntas

        Returns:
            Lista de preguntas con opciones y respuesta correcta
        """
        try:
            logger.info(f"Generando preguntas de prueba para {len(articles)} artículos")

            # Leer el archivo example.txt para obtener el contexto de formato
            try:
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                example_file_path = os.path.join(current_dir, "example.txt")

                if os.path.exists(example_file_path):
                    with open(example_file_path, 'r', encoding='utf-8') as file:
                        example_context = file.read().strip()
                else:
                    # Contexto de respaldo si no existe el archivo
                    example_context = """1-A que distancia de la línea férrea el conductor está obligado a detener la marcha.
1-A menos de 10 metros.                      
2-En la vertical correspondiente.                
3-A no menos de 3 metros de la primera línea.

2-¿Cuál es la distancia que debe existir entre dos vehículos en marcha?
1-	Mantener 5 metros por cada 15 km/hora.              
2-	Mantener 2 metros por cada 10 km/hora.                           
3-	Mantener 6 metros por cada 20 km/hora."""
            except Exception as e:
                logger.warning(f"No se pudo leer example.txt: {e}")
                example_context = "Ejemplo no disponible"

            system_prompt = f"""Eres un experto en crear preguntas de examen de tránsito basadas en la Ley 109 - Código de Seguridad Vial de Cuba.

INSTRUCCIONES CRÍTICAS:
1. Para cada artículo proporcionado, crea UNA pregunta de opción múltiple
2. La pregunta debe ser clara, específica y basada directamente en el contenido del artículo
3. Proporciona exactamente 3 opciones de respuesta numeradas (1, 2, 3)
4. Una opción debe ser la correcta y las otras dos deben ser plausibles pero incorrectas
5. DEBES seguir EXACTAMENTE el formato mostrado en los ejemplos
6. NO agregues texto adicional, explicaciones o comentarios
7. SIEMPRE incluye la línea RESPUESTA_CORRECTA: después de cada pregunta
8. NO USES CORCHETES [] en ninguna parte del texto
9. Escribe las opciones en texto plano normal, sin símbolos especiales
10. Las opciones deben ser frases naturales y directas
11. CADA OPCIÓN DE RESPUESTA DEBE TENER UN MÁXIMO DE 11 PALABRAS - sé conciso y directo

FORMATO OBLIGATORIO (copia este formato exactamente):
1-¿Cuál es la pregunta sobre el artículo?
1-Primera opción de respuesta (máximo 11 palabras).
2-Segunda opción de respuesta (máximo 11 palabras).
3-Tercera opción de respuesta (máximo 11 palabras).
RESPUESTA_CORRECTA:1

EJEMPLOS DE REFERENCIA:
{example_context}

REGLAS DE FORMATO ESTRICTAS:
- Pregunta: Debe empezar con número-signo de interrogación y terminar con signo de interrogación
- Opciones: Deben ser texto directo sin corchetes ni comillas
- Opciones: MÁXIMO 11 palabras cada una - mantén las respuestas breves y precisas
- NO escribas [texto], escribe directamente: texto
- Ejemplo CORRECTO: "1-A menos de 10 metros."
- Ejemplo INCORRECTO: "1-[A menos de 10 metros.]"
- Ejemplo CORRECTO (longitud): "1-Mantener 5 metros por cada 15 km/hora."
- Ejemplo INCORRECTO (longitud): "1-Se debe mantener una distancia de 5 metros por cada 15 kilómetros por hora de velocidad."

IMPORTANTE: Responde ÚNICAMENTE con las preguntas en el formato mostrado, sin texto adicional. Usa el estilo y formato de los ejemplos proporcionados. Recuerda: máximo 11 palabras por opción."""

            questions = []

            # Procesar artículos de uno en uno para mayor precisión
            for i, article in enumerate(articles, 1):
                try:
                    user_prompt = f"""Basándote en el siguiente artículo de la Ley 109, genera UNA pregunta de examen siguiendo exactamente el formato de los ejemplos:

ARTÍCULO {article['id']}:
{article['contenido']}

Genera la pregunta número {i} siguiendo exactamente el formato mostrado en los ejemplos. La pregunta debe ser sobre el contenido específico de este artículo."""

                    # Llamada a Mistral AI
                    response = self.mistral_client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )

                    generated_text = response.choices[0].message.content
                    logger.info(f"Texto generado para artículo {article['id']}: {generated_text[:100]}...")

                    # Parsear la pregunta generada
                    parsed_question = self._parse_single_question(generated_text, article, i)
                    if parsed_question:
                        questions.append(parsed_question)
                        logger.info(f"Pregunta {i} generada exitosamente para artículo {article['id']}")
                    else:
                        logger.warning(f"No se pudo parsear la pregunta para artículo {article['id']}")

                except Exception as e:
                    logger.error(f"Error generando pregunta para artículo {article['id']}: {e}")
                    continue

            logger.info(f"Generadas {len(questions)} preguntas de prueba exitosamente")
            return questions

        except Exception as e:
            logger.error(f"Error en generación de preguntas de prueba: {e}")
            return []

    def _parse_single_question(self, generated_text: str, article: Dict[str, Any], question_number: int) -> Optional[Dict[str, Any]]:
        """
        Parsea una sola pregunta del texto generado

        Args:
            generated_text: Texto generado por el LLM
            article: Artículo original para referencia
            question_number: Número de la pregunta

        Returns:
            Pregunta estructurada o None si no se pudo parsear
        """
        try:
            lines = [line.strip() for line in generated_text.strip().split('\n') if line.strip()]

            question_text = None
            options = []
            correct_answer = None

            for line in lines:
                # Buscar la pregunta (puede empezar con número- o sin número)
                if question_text is None and ('?' in line or line.endswith('.')):
                    # Limpiar número inicial si existe
                    if '-' in line and line.split('-')[0].strip().isdigit():
                        question_text = line.split('-', 1)[1].strip()
                    else:
                        question_text = line.strip()

                # Buscar opciones (1-, 2-, 3-)
                elif line.startswith(('1-', '2-', '3-')) and len(options) < 3:
                    option_text = line[2:].strip()
                    # Limpiar corchetes y comillas si existen
                    option_text = option_text.strip('[]"\'')
                    if option_text:
                        options.append(option_text)

                # Buscar respuesta correcta
                elif 'RESPUESTA_CORRECTA' in line.upper() or 'CORRECTA' in line.upper():
                    try:
                        # Extraer el número de la respuesta correcta
                        parts = line.split(':')
                        if len(parts) > 1:
                            correct_answer = int(parts[1].strip())
                        else:
                            # Buscar dígitos en la línea
                            import re
                            numbers = re.findall(r'\d+', line)
                            if numbers:
                                correct_answer = int(numbers[0])
                    except:
                        correct_answer = 1  # Valor por defecto

            # Si no encontramos respuesta correcta, usar 1 por defecto
            if correct_answer is None:
                correct_answer = 1

            # Validar que tenemos todos los elementos necesarios
            if question_text and len(options) >= 3:
                return {
                    "question": question_text,
                    "options": options[:3],  # Solo tomar las primeras 3 opciones
                    "correct_answer": min(correct_answer, 3),  # Asegurar que esté entre 1-3
                    "article_id": article["id"],
                    "article_content": article["contenido"]
                }
            else:
                logger.warning(f"Pregunta incompleta: pregunta={question_text is not None}, opciones={len(options)}")
                return None

        except Exception as e:
            logger.error(f"Error parseando pregunta: {e}")
            return None

    def get_service_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el servicio RAG"""
        embedding_stats = self.embedding_service.get_collection_stats()

        return {
            "service_type": "RAG (Retrieval-Augmented Generation)",
            "llm_provider": "Mistral AI",
            "model": self.model,
            "embedding_model": embedding_stats.get("model_name", "N/A"),
            "total_articles": embedding_stats.get("total_documents", 0),
            "capabilities": [
                "Búsqueda semántica",
                "Generación de respuestas conversacionales",
                "Citas de artículos específicos",
                "Respuestas contextualizadas"
            ]
        }

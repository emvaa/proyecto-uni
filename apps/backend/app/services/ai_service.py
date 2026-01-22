import os
import json
from typing import Dict, List, Any, Optional
from groq import Groq
from ..settings import settings


class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)

    async def analyze_task_content(
        self,
        title: str,
        description: str,
        file_url: Optional[str] = None,
        content_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analiza el contenido de una tarea usando IA para generar:
        - Análisis del contenido
        - Explicación paso a paso
        - Solución propuesta
        """

        # Preparar el contenido para análisis
        content = f"Título: {title}\nDescripción: {description}"
        if content_text:
            content += f"\nContenido del archivo: {content_text[:2000]}"  # Limitar longitud

        prompt = f"""
        Analiza esta tarea universitaria y proporciona un análisis detallado:

        {content}

        Proporciona tu respuesta en formato JSON con la siguiente estructura:
        {{
            "analysis": {{
                "task_type": "tipo de tarea (homework/exam/project/etc)",
                "difficulty_level": "nivel de dificultad (1-5)",
                "estimated_time": "tiempo estimado en horas",
                "key_concepts": ["concepto1", "concepto2", ...],
                "prerequisites": ["prerequisito1", "prerequisito2", ...],
                "learning_objectives": ["objetivo1", "objetivo2", ...]
            }},
            "explanation": {{
                "step_by_step_guide": [
                    {{"step": 1, "title": "Paso 1", "description": "Descripción detallada del paso 1"}},
                    {{"step": 2, "title": "Paso 2", "description": "Descripción detallada del paso 2"}}
                ],
                "tips": ["tip1", "tip2", ...],
                "common_mistakes": ["error1", "error2", ...]
            }},
            "solution": {{
                "approach": "Enfoque recomendado para resolver",
                "key_steps": ["paso1", "paso2", ...],
                "expected_outcome": "Resultado esperado",
                "validation_methods": ["método1", "método2", ...]
            }},
            "estimated_difficulty": 3,
            "suggested_approach": "Breve descripción del enfoque recomendado",
            "key_concepts": ["concepto1", "concepto2"]
        }}

        Sé específico y educativo. Si es una tarea matemática, muestra el razonamiento paso a paso.
        Si es un ensayo, proporciona estructura y consejos de redacción.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )

            response_text = completion.choices[0].message.content or "{}"

            # Intentar parsear JSON
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # Si falla el parseo, crear una estructura básica
                return {
                    "analysis": {
                        "task_type": "other",
                        "difficulty_level": 3,
                        "estimated_time": "2 hours",
                        "key_concepts": ["Investigación requerida"],
                        "prerequisites": [],
                        "learning_objectives": ["Completar tarea asignada"]
                    },
                    "explanation": {
                        "step_by_step_guide": [
                            {"step": 1, "title": "Revisar contenido", "description": "Lee detenidamente la tarea"},
                            {"step": 2, "title": "Investigar", "description": "Busca información adicional si es necesario"},
                            {"step": 3, "title": "Resolver", "description": "Aplica los conocimientos para completar la tarea"}
                        ],
                        "tips": ["Toma notas mientras trabajas", "Revisa tu trabajo antes de entregar"],
                        "common_mistakes": ["No leer las instrucciones completas", "Entregar sin revisar"]
                    },
                    "solution": {
                        "approach": "Sigue las instrucciones proporcionadas",
                        "key_steps": ["Leer", "Ejecutar", "Revisar"],
                        "expected_outcome": "Tarea completada satisfactoriamente",
                        "validation_methods": ["Revisión personal", "Consulta con compañeros"]
                    },
                    "estimated_difficulty": 3,
                    "suggested_approach": "Lee las instrucciones y ejecuta paso a paso",
                    "key_concepts": ["Comprensión de instrucciones", "Aplicación de conocimientos"]
                }

        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Retornar estructura básica en caso de error
            return {
                "analysis": {
                    "task_type": "other",
                    "difficulty_level": 3,
                    "estimated_time": "2 hours",
                    "key_concepts": [],
                    "prerequisites": [],
                    "learning_objectives": []
                },
                "explanation": {
                    "step_by_step_guide": [],
                    "tips": [],
                    "common_mistakes": []
                },
                "solution": {
                    "approach": "Sigue las instrucciones del profesor",
                    "key_steps": [],
                    "expected_outcome": "Tarea completada",
                    "validation_methods": []
                },
                "estimated_difficulty": 3,
                "suggested_approach": "Lee y ejecuta las instrucciones",
                "key_concepts": []
            }

    def estimate_difficulty_priority(self, analysis: Dict[str, Any]) -> str:
        """Estima la prioridad basada en el análisis de IA"""
        difficulty = analysis.get("difficulty_level", 3)

        if difficulty >= 4:
            return "high"
        elif difficulty >= 2:
            return "medium"
        else:
            return "low"

    async def generate_quiz_questions(
        self,
        subject: str,
        topic: str,
        difficulty: int = 3,
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """Genera preguntas de quiz automáticamente"""

        prompt = f"""
        Genera {num_questions} preguntas de quiz sobre {topic} para la materia {subject}.
        Nivel de dificultad: {difficulty}/5 (1=fácil, 5=difícil)

        Formato requerido (JSON):
        [
            {{
                "question": "Pregunta aquí",
                "type": "multiple_choice|true_false|short_answer",
                "options": ["A) Opción1", "B) Opción2", "C) Opción3", "D) Opción4"] // solo para multiple_choice
                "correct_answer": "A) Opción1",
                "explanation": "Explicación breve de por qué es correcta",
                "difficulty": {difficulty}
            }}
        ]

        Incluye variedad de tipos de preguntas. Para matemáticas, incluye cálculo paso a paso.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )

            response_text = completion.choices[0].message.content or "[]"

            try:
                questions = json.loads(response_text)
                return questions if isinstance(questions, list) else []
            except json.JSONDecodeError:
                return []

        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            return []

    async def generate_flashcards(
        self,
        content: str,
        subject: str,
        num_cards: int = 10
    ) -> List[Dict[str, str]]:
        """Genera flashcards automáticamente del contenido"""

        prompt = f"""
        Analiza este contenido y genera {num_cards} flashcards para estudiar {subject}:

        CONTENIDO:
        {content[:3000]}

        Formato JSON:
        [
            {{
                "front": "Pregunta o concepto clave",
                "back": "Respuesta o explicación detallada"
            }}
        ]

        Enfócate en conceptos importantes, definiciones, fórmulas, y relaciones clave.
        Las flashcards deben ser efectivas para estudio espaciado.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1200
            )

            response_text = completion.choices[0].message.content or "[]"

            try:
                flashcards = json.loads(response_text)
                return flashcards if isinstance(flashcards, list) else []
            except json.JSONDecodeError:
                return []

        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return []

    async def analyze_study_pattern(
        self,
        study_sessions: List[Dict[str, Any]],
        quiz_scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza patrones de estudio para dar recomendaciones"""

        study_data = json.dumps({
            "sessions": study_sessions[-10:],  # Últimas 10 sesiones
            "quiz_scores": quiz_scores[-5:]    # Últimas 5 evaluaciones
        })

        prompt = f"""
        Analiza estos datos de estudio y proporciona recomendaciones:

        {study_data}

        Responde en JSON:
        {{
            "strengths": ["fortaleza1", "fortaleza2"],
            "weaknesses": ["debilidad1", "debilidad2"],
            "recommendations": ["recomendacion1", "recomendacion2"],
            "optimal_study_time": "hora óptima del día",
            "suggested_session_duration": "duración recomendada",
            "study_streak_maintenance": "cómo mantener racha de estudio"
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800
            )

            response_text = completion.choices[0].message.content or "{}"

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {}

        except Exception as e:
            print(f"Error analyzing study pattern: {str(e)}")
            return {}

    async def generate_chat_response(
        self,
        user_message: str,
        chat_type: str,
        mode: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Genera respuesta de chat contextual"""

        system_prompt = self._get_chat_system_prompt(chat_type, mode, context)

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = completion.choices[0].message.content or "Lo siento, no pude generar una respuesta."

            return {
                "content": content.strip(),
                "tokens_used": completion.usage.total_tokens if completion.usage else None,
                "model_used": settings.groq_model
            }

        except Exception as e:
            print(f"Error generating chat response: {str(e)}")
            return {
                "content": "Lo siento, hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo.",
                "error": str(e)
            }

    def _get_chat_system_prompt(self, chat_type: str, mode: str, context: str) -> str:
        """Genera el prompt del sistema basado en el tipo de chat"""

        base_prompt = "Eres UniAI, un tutor universitario inteligente y motivador. "

        if chat_type == "task":
            base_prompt += """
            Estás ayudando con una tarea específica. Usa el contexto proporcionado para dar respuestas relevantes y útiles.
            Si el estudiante pide explicaciones, sé detallado pero claro.
            Si pide ayuda para resolver, guía paso a paso sin dar la respuesta completa inmediatamente.
            """
        else:  # chat general
            base_prompt += """
            Estás en un chat general para consultas universitarias.
            Puedes ayudar con consejos de estudio, organización, motivación, o cualquier tema académico.
            Sé proactivo en ofrecer recursos útiles y estrategias de aprendizaje.
            """

        # Agregar contexto si existe
        if context.strip():
            base_prompt += f"\n\nCONTEXTO ADICIONAL:\n{context}"

        # Agregar modo de aprendizaje
        if mode == "review":
            base_prompt += "\n\nMODO REPASO: Resume primero y luego haz 3-5 preguntas para verificar comprensión."
        else:  # learn mode
            base_prompt += "\n\nMODO APRENDER: Explica conceptos paso a paso, da pistas y guía el aprendizaje."

        return base_prompt
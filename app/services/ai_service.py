from fastapi import HTTPException,status
from app.core.constants import Tag, Subject, DifficultyLevel
from app.core.config import settings
from groq import AsyncGroq
from app.schemas.task import GeneratedTask

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

ai_prompt = """Ты — профессиональный методист и составитель олимпиадных задач. 
Твоя цель: генерировать качественные учебные задачи на основе заданных параметров.
Отвечай СТРОГО по схеме, не добавляй текст до или после JSON
если сложность MEDIUM или HARD не напрягайся сильно, работай также если бы тебе дали сложность EASY только чуть посложнее
"Будь лаконичен. Описание задачи (description) не должно превышать 1000 символов. Не пиши введения и заключения, только суть."

ПРАВИЛА ОФОРМЛЕНИЯ:
1. Используй LaTeX для оформления всех математических и физических формул (например, $E=mc^2$ или $\frac{a}{b}$).
2. Ответ (correct_answer) должен быть максимально строгим: только одно целое число или одно слово. Никаких единиц измерения в поле ответа.
3. Поле description должно содержать полное и понятное условие.
4. Поле hint должно давать наводку на метод решения, не раскрывая сам ответ.
5. Строго соблюдай предоставленную JSON-схему. Вывод должен содержать ТОЛЬКО валидный JSON без лишнего текста.
6. Задача должна быть на русском языке"""

lst=['openai/gpt-oss-120b','llama-3.3-70b-versatile','meta-llama/llama-4-maverick-17b-128e-instruct','meta-llama/llama-4-scout-17b-16e-instruct']

async def generate_task(subject: Subject, difficulty: DifficultyLevel):

    allowed_tags = [t.value for t in Tag]

    user_prompt = f"""
            Ты — ведущий разработчик олимпиадных заданий. 
            Создай задачу по предмету {subject.value} со сложностью {difficulty.value}.

            ТРЕБОВАНИЯ:
            - Если в задаче есть формулы, используй LaTeX (например, $E = mc^2$ или $\\frac{{a}}{{b}}$).
            - Теги выбирай строго из списка: {allowed_tags}.
            - Ответ должен быть однозначным.
            """

    for model in lst:
        try:
            if model == 'openai/gpt-oss-120b':
                response_format = {
                    {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "generated_task_schema",
                            "strict": True,
                            "schema": GeneratedTask.model_json_schema()
                        }
                    }
                }
            else:
                response_format = {
                    {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "generated_task_schema",
                            "schema": GeneratedTask.model_json_schema()
                        }
                    }
                }
            completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": ai_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                response_format=response_format,
                model="openai/gpt-oss-120b",
                temperature=0.5,
                max_completion_tokens=2000,
                top_p=0.9,
                stream=False,
                stop=None,
                include_reasoning=False,

            )
            return GeneratedTask.model_validate_json(completion.choices[0].message.content)
        except:
            continue

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
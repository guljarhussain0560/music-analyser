import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("chatbot")


async def get_ai_answer(user_question: str) -> str:
    """Queries Maestro AI music analyst assistant via Groq LLM."""
    if not settings.GROQ_API_KEY:
        return "The AI assistant service is running in mock mode. Please set GROQ_API_KEY for live responses."

    system_prompt = (
        "You are 'Maestro', an expert AI music theorist and sound engineer integrated into an audio analysis engine.\n"
        "Explain musical parameters (BPM, key, mode, timbral dynamics, spectral balance) clearly, concisely, and analytically."
    )

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    }
    payload = {
        "model": settings.GROQ_LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Chatbot API error: {e}")
        raise AppException(f"AI Assistant unavailable: {e}", status_code=503)

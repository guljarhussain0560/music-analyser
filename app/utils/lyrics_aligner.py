import requests

from app.core.config import settings
from app.core.exceptions import TranscriptionError
from app.core.logging import get_logger

logger = get_logger("lyrics_aligner")


def rewrite_lyrics_with_timestamps(
    lrc_string: str, language: str, duration: float, user_prompt: str
) -> str:
    """
    Uses Groq LLM to rewrite timestamped LRC lyrics according to creative prompt instructions
    while maintaining exact timing cues.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured; returning unmodified lyrics.")
        return lrc_string

    system_prompt = (
        f"You are a creative songwriter and music producer. Your task is to rewrite song lyrics in LRC format.\n"
        f"Strict rules:\n"
        f"1. Keep all timestamp brackets [mm:ss.xx] and structure intact.\n"
        f"2. Rewrite lyrics in the language '{language}'.\n"
        f"3. Song duration is {duration} seconds.\n"
        f"4. User creative goal: {user_prompt}\n"
        f"5. Return ONLY the raw LRC output without any explanations, markdown code blocks, or conversational text."
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
            {"role": "user", "content": lrc_string},
        ],
        "temperature": 0.8,
        "max_tokens": 2048,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        res_json = response.json()
        rewritten = res_json["choices"][0]["message"]["content"].strip()
        return rewritten
    except Exception as e:
        logger.error(f"Failed rewriting lyrics via Groq LLM: {e}")
        raise TranscriptionError(f"Lyric rewriting failed: {e}")

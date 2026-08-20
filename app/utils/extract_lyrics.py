import time
from pathlib import Path
from typing import Any

import requests
from pydub import AudioSegment

from app.core.config import settings
from app.core.exceptions import TranscriptionError
from app.core.logging import get_logger
from app.utils.seg_to_lrc import convert_lyrics_to_lrc

logger = get_logger("transcription")


def transcribe_lyrics(audio_path: str, max_retries: int = 3) -> dict[str, Any]:
    """
    Transcribes spoken and sung lyrics using Groq Whisper-large-v3 model
    with exponential backoff retries and optimized downsampling.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is not configured; returning mock empty lyrics.")
        return {"language": "en", "duration": 0.0, "original_lrc": ""}

    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Optimize audio to lightweight mono MP3 for fast upload
    if path.suffix.lower() == ".wav":
        mp3_path = path.with_suffix(".transcribe.mp3")
        sound = AudioSegment.from_wav(str(path))
        sound = sound.set_channels(1).set_frame_rate(16000)
        sound.export(str(mp3_path), format="mp3", bitrate="32k")
    else:
        mp3_path = path

    api_url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
    data_payload = {"model": settings.GROQ_WHISPER_MODEL, "response_format": "verbose_json"}

    transcription_data = None
    for attempt in range(max_retries):
        try:
            with open(mp3_path, "rb") as f:
                files_payload = {"file": (mp3_path.name, f, "audio/mpeg")}
                response = requests.post(
                    api_url, headers=headers, data=data_payload, files=files_payload, timeout=120
                )
                response.raise_for_status()
                transcription_data = response.json()
                break
        except requests.exceptions.HTTPError as http_err:
            if 500 <= http_err.response.status_code < 600 and attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.warning(f"Groq API 5xx error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Groq transcription HTTP error: {http_err}")
                raise TranscriptionError(f"Transcription failed: {http_err}") from http_err
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
            else:
                logger.error(f"Groq transcription network failure: {e}")
                raise TranscriptionError(f"Network error during transcription: {e}") from e

    if not transcription_data:
        raise TranscriptionError("No transcription response received from Groq API.")

    language = transcription_data.get("language", "en")
    duration = transcription_data.get("duration", 0.0)
    raw_segments = transcription_data.get("segments", [])

    segments = [
        {
            "start": seg.get("start", 0.0),
            "end": seg.get("end", seg.get("start", 0.0) + 2.0),
            "text": seg.get("text", "").strip() or ".",
        }
        for seg in raw_segments
    ]
    original_lrc = convert_lyrics_to_lrc(segments)

    return {"language": language, "duration": duration, "original_lrc": original_lrc}

"""Audio extraction, transcription, downloading, and analytics utilities."""

from app.utils.analytics import (
    extract_bass_analytics,
    extract_drums_analytics,
    extract_flute_analytics,
    extract_guitar_analytics,
    extract_music_analytics,
    extract_other_analytics,
    extract_piano_analytics,
    extract_violin_analytics,
    extract_vocal_analytics,
)
from app.utils.chatbot import get_ai_answer
from app.utils.downloader import download_from_spotify, download_from_youtube
from app.utils.extract_lyrics import transcribe_lyrics
from app.utils.lyrics_aligner import rewrite_lyrics_with_timestamps
from app.utils.parallel_processor import run_analysis_in_parallel
from app.utils.seg_to_lrc import convert_lyrics_to_lrc
from app.utils.spleeter_wrapper import spleeter_5_stem_split

__all__ = [
    "download_from_youtube",
    "download_from_spotify",
    "transcribe_lyrics",
    "rewrite_lyrics_with_timestamps",
    "convert_lyrics_to_lrc",
    "spleeter_5_stem_split",
    "run_analysis_in_parallel",
    "get_ai_answer",
    "extract_music_analytics",
    "extract_vocal_analytics",
    "extract_bass_analytics",
    "extract_drums_analytics",
    "extract_piano_analytics",
    "extract_other_analytics",
    "extract_guitar_analytics",
    "extract_violin_analytics",
    "extract_flute_analytics",
]

"""Modular audio analytics subpackage providing specialized feature extraction."""

from app.utils.analytics.common import (
    downsample_array,
    get_feature_stats,
    round_floats,
    to_py_native,
)
from app.utils.analytics.full_song import extract_music_analytics
from app.utils.analytics.instruments import (
    extract_flute_analytics,
    extract_guitar_analytics,
    extract_other_analytics,
    extract_piano_analytics,
    extract_violin_analytics,
)
from app.utils.analytics.rhythm_bass import extract_bass_analytics, extract_drums_analytics
from app.utils.analytics.vocal import extract_vocal_analytics

__all__ = [
    "to_py_native",
    "round_floats",
    "get_feature_stats",
    "downsample_array",
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

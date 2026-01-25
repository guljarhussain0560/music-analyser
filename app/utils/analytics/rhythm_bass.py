import os
from typing import Any

import librosa
import numpy as np

from app.core.logging import get_logger
from app.utils.analytics.common import downsample_array, round_floats, to_py_native

logger = get_logger("analytics.rhythm_bass")


def extract_bass_analytics(audio_path: str) -> dict[str, Any]:
    """Extracts low-end power, dominant bass note, and rhythm stability."""
    if not os.path.exists(audio_path):
        return {"error": f"Bass audio file not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        duration_sec = float(librosa.get_duration(y=y, sr=sr))
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        rhythm_stability = float(np.std(np.diff(onsets))) if len(onsets) > 1 else 0.0

        chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)
        dominant_idx = int(np.argmax(np.mean(chromagram, axis=1)))
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)
        graph_times = downsample_array(times, 150)
        graph_values = downsample_array(rms, 150)

        result = {
            "rhythm_stability": rhythm_stability,
            "onset_density": len(onsets) / duration_sec if duration_sec > 0 else 0,
            "dominant_note": note_names[dominant_idx],
            "low_end_power": float(np.mean(rms)),
            "performance_graph": {
                "timestamps": [float(t) for t in graph_times],
                "values": [float(v) for v in graph_values],
                "value_type": "rms_energy",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        logger.error(f"Error in bass analysis: {e}")
        return {"error": f"Could not process bass: {e}"}


def extract_drums_analytics(audio_path: str) -> dict[str, Any]:
    """Extracts drum tempo, groove consistency, and kick-to-snare energy ratio."""
    if not os.path.exists(audio_path):
        return {"error": f"Drums audio file not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        tempo_val, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
        tempo = (
            float(tempo_val[0]) if isinstance(tempo_val, np.ndarray | list) else float(tempo_val)
        )
        groove_consistency = float(np.std(np.diff(beats))) if len(beats) > 1 else 0.0

        spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        kick_energy = float(np.sum(spec_centroid < 150))
        snare_cymbal_energy = float(np.sum(spec_centroid >= 150))

        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)
        graph_times = downsample_array(times, 150)
        graph_values = downsample_array(rms, 150)

        result = {
            "tempo_bpm": tempo,
            "groove_consistency": groove_consistency,
            "kick_to_snare_ratio": kick_energy / (snare_cymbal_energy + 1e-6),
            "performance_graph": {
                "timestamps": [float(t) for t in graph_times],
                "values": [float(v) for v in graph_values],
                "value_type": "rms_energy",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        logger.error(f"Error in drums analysis: {e}")
        return {"error": f"Could not process drums: {e}"}

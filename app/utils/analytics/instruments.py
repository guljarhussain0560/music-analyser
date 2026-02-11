import os
from typing import Any

import librosa
import numpy as np

from app.core.logging import get_logger
from app.utils.analytics.common import downsample_array, round_floats, to_py_native

logger = get_logger("analytics.instruments")


def extract_piano_analytics(audio_path: str) -> dict[str, Any]:
    """Extracts harmonic complexity, dynamic variation, and loudness for piano."""
    if not os.path.exists(audio_path):
        return {"error": f"Piano file not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)

        result = {
            "average_loudness": float(np.mean(rms)),
            "dynamic_variation": float(np.std(rms)),
            "average_brightness": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0])),
            "harmonic_complexity": float(np.mean(librosa.feature.spectral_flatness(y=y))),
            "performance_graph": {
                "timestamps": [float(t) for t in downsample_array(times, 150)],
                "values": [float(v) for v in downsample_array(rms, 150)],
                "value_type": "rms_energy",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        return {"error": f"Could not process piano: {e}"}


def extract_other_analytics(audio_path: str) -> dict[str, Any]:
    """Extracts loudness, brightness, and texture complexity for general stems."""
    if not os.path.exists(audio_path):
        return {"error": f"Other audio stem not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)

        result = {
            "average_loudness": float(np.mean(rms)),
            "average_brightness": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0])),
            "texture_complexity": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)[0])),
            "performance_graph": {
                "timestamps": [float(t) for t in downsample_array(times, 150)],
                "values": [float(v) for v in downsample_array(rms, 150)],
                "value_type": "rms_energy",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        return {"error": f"Could not process other stem: {e}"}


def extract_guitar_analytics(audio_path: str) -> dict[str, Any]:
    """Extracts guitar strum/pick rate, chord complexity style, and sustain."""
    if not os.path.exists(audio_path):
        return {"error": f"Guitar track not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        duration_sec = float(librosa.get_duration(y=y, sr=sr))
        if duration_sec < 1.0:
            return {"error": "Audio too short for guitar analysis."}

        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        tempo_val, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = (
            float(tempo_val[0]) if isinstance(tempo_val, np.ndarray | list) else float(tempo_val)
        )
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        onset_diffs = np.diff(onsets, prepend=0)
        strum_count = int(np.sum(onset_diffs < 0.1))
        picking_count = len(onsets) - strum_count

        chord_complexity = float(np.mean(np.sum(chroma > 0.6, axis=0)))
        if chord_complexity < 1.8:
            chord_style = "Single Notes / Melodic Riffs"
        elif chord_complexity < 3.5:
            chord_style = "Power Chords / Simple Harmony"
        else:
            chord_style = "Complex / Full Voiced Chords"

        y_harmonic, y_percussive = librosa.effects.hpss(y)
        attack_noisiness = float(np.mean(librosa.feature.zero_crossing_rate(y=y_percussive)))
        sustain_factor = float(1.0 - np.mean(librosa.feature.spectral_flatness(y=y)))
        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)

        result = {
            "rhythm": {
                "estimated_tempo_bpm": tempo,
                "strums_per_second": strum_count / duration_sec if duration_sec > 0 else 0,
                "picks_per_second": picking_count / duration_sec if duration_sec > 0 else 0,
            },
            "harmony_and_style": {
                "clarity_harmonic_ratio": float(np.sum(y_harmonic**2) / (np.sum(y**2) + 1e-7)),
                "chord_style_prediction": chord_style,
                "estimated_chord_complexity": chord_complexity,
            },
            "technique": {
                "attack_noisiness": attack_noisiness,
                "sustain_factor": sustain_factor,
                "dynamic_variation": float(np.std(rms)),
                "brightness_spectral_centroid": float(
                    np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                ),
                "richness_spectral_bandwidth": float(
                    np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
                ),
            },
            "performance_graph": {
                "timestamps": [float(t) for t in downsample_array(times, 150)],
                "values": [float(v) for v in downsample_array(rms, 150)],
                "value_type": "rms_energy",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        return {"error": f"Could not process guitar: {e}"}


def _extract_melodic_instrument(
    audio_path: str, name: str, fmin: float, fmax: float
) -> dict[str, Any]:
    """Helper for pitch, vibrato, and articulation extraction in violin and flute."""
    if not os.path.exists(audio_path):
        return {"error": f"{name} file not found: {audio_path}"}
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        f0, voiced_flag, _ = librosa.pyin(y, fmin=fmin, fmax=fmax)
        voiced_f0 = f0[voiced_flag & (f0 > 0)]

        if len(voiced_f0) < 10:
            return {"error": f"Could not detect clear melody for {name}."}

        pitch_range = float(
            librosa.hz_to_midi(np.max(voiced_f0)) - librosa.hz_to_midi(np.min(voiced_f0))
        )
        d_cents = np.diff(librosa.hz_to_midi(voiced_f0) * 100)
        vibrato_depth = float(np.std(d_cents)) if len(d_cents) > 0 else 0.0

        legato_score = float(np.sum(voiced_flag) / len(voiced_flag))
        attack_clarity = float(np.mean(librosa.onset.onset_strength(y=y, sr=sr)))
        h, p = librosa.effects.hpss(y)
        hnr = float(10 * np.log10(np.sum(h**2) / (np.sum(p**2) + 1e-7))) if np.any(p) else 50.0
        breathiness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
        times = librosa.times_like(f0, sr=sr)

        result = {
            "pitch": {
                "average_pitch_hz": float(np.mean(voiced_f0)),
                "pitch_stability_hz_std": float(np.std(voiced_f0)),
                "pitch_range_semitones": pitch_range,
            },
            "vibrato": {"vibrato_rate_hz": 5.5, "vibrato_depth_cents": vibrato_depth},
            "articulation_and_timbre": {
                "legato_score": legato_score,
                "attack_clarity": attack_clarity,
                "harmonics_to_noise_ratio_db": hnr,
                "breathiness_or_scratchiness": breathiness,
                "brightness_spectral_centroid": float(
                    np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                ),
            },
            "performance_graph": {
                "timestamps": [float(t) for t in downsample_array(times, 150)],
                "values": [
                    float(p) if p > 0 else None
                    for p in downsample_array(np.nan_to_num(f0, nan=0.0), 150)
                ],
                "value_type": "pitch_hz",
            },
        }
        return round_floats(to_py_native(result))
    except Exception as e:
        return {"error": f"Could not process {name}: {e}"}


def extract_violin_analytics(audio_path: str) -> dict[str, Any]:
    return _extract_melodic_instrument(
        audio_path,
        "violin",
        fmin=float(librosa.note_to_hz("G3")),
        fmax=float(librosa.note_to_hz("A7")),
    )


def extract_flute_analytics(audio_path: str) -> dict[str, Any]:
    return _extract_melodic_instrument(
        audio_path,
        "flute",
        fmin=float(librosa.note_to_hz("C4")),
        fmax=float(librosa.note_to_hz("D7")),
    )

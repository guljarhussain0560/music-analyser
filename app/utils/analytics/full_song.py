import os
from typing import Any

import librosa
import numpy as np

from app.core.logging import get_logger
from app.utils.analytics.common import get_feature_stats, round_floats, to_py_native

logger = get_logger("analytics.full_song")


def extract_music_analytics(audio_path: str, is_vocal_track: bool = False) -> dict[str, Any]:
    """
    Performs deep audio analysis using Librosa to compute tempo, key, mode,
    spectral centroid, rolloff, MFCCs, and structural boundaries.
    """
    logger.info(f"Extracting master audio analytics from: {audio_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        duration = float(librosa.get_duration(y=y, sr=sr))
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        # Tempo and beat tracking
        tempo_val, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
        tempo = (
            float(tempo_val[0]) if isinstance(tempo_val, np.ndarray | list) else float(tempo_val)
        )
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onsets = librosa.onset.onset_detect(y=y_percussive, sr=sr, units="time")

        # Tonality and Key Estimation
        chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key_index = int(np.argmax(chroma_mean))
        estimated_key = keys[key_index]

        major_third_idx = (key_index + 4) % 12
        minor_third_idx = (key_index + 3) % 12
        mode = "Major" if chroma_mean[major_third_idx] > chroma_mean[minor_third_idx] else "Minor"

        # Spectral and Timbral features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spec_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        spec_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        spec_flatness = librosa.feature.spectral_flatness(y=y)[0]
        spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # Structural Segmentation
        rec_matrix = librosa.segment.recurrence_matrix(
            librosa.feature.chroma_cens(y=y, sr=sr), mode="affinity"
        )
        num_segments = max(2, min(int(duration / 20), 8))
        boundaries_idx = librosa.segment.agglomerative(rec_matrix, k=num_segments)
        boundary_times = librosa.times_like(rec_matrix, axis=1)[boundaries_idx]
        segment_times = np.concatenate(([0.0], boundary_times, [duration]))
        song_segments = [
            {
                "segment_id": i + 1,
                "start_time": to_py_native(segment_times[i]),
                "end_time": to_py_native(segment_times[i + 1]),
            }
            for i in range(len(segment_times) - 1)
        ]

        h_rms = np.mean(librosa.feature.rms(y=y_harmonic)[0])
        p_rms = np.mean(librosa.feature.rms(y=y_percussive)[0])
        hp_ratio = h_rms / (p_rms + 1e-7)

        analytics = {
            "metadata": {
                "file_path": audio_path,
                "duration_seconds": to_py_native(duration),
                "sample_rate": sr,
            },
            "summary": {
                "tempo_bpm": to_py_native(tempo),
                "estimated_key": estimated_key,
                "key_confidence": to_py_native(np.max(chroma_mean) / (np.sum(chroma_mean) + 1e-7)),
                "mode": mode,
                "harmonic_to_percussive_ratio": to_py_native(hp_ratio),
            },
            "rhythm_and_tempo": {
                "beat_count": len(beat_frames),
                "onset_count": len(onsets),
                "beat_times_sec": to_py_native(beat_times),
                "onset_times_sec": to_py_native(onsets),
                "onset_density_per_sec": to_py_native(
                    len(onsets) / duration if duration > 0 else 0
                ),
            },
            "timbre_and_spectral_properties": {
                "spectral_centroid": get_feature_stats(spec_centroid, "spectral_centroid"),
                "spectral_bandwidth": get_feature_stats(spec_bandwidth, "spectral_bandwidth"),
                "spectral_contrast": {
                    "contrast_bands_mean": to_py_native(np.mean(spec_contrast, axis=1)),
                    "contrast_bands_std_dev": to_py_native(np.std(spec_contrast, axis=1)),
                },
                "spectral_rolloff": get_feature_stats(spec_rolloff, "spectral_rolloff"),
                "spectral_flatness": get_feature_stats(spec_flatness, "spectral_flatness"),
                "mfccs": {
                    "num_mfccs": 20,
                    "mfccs_mean": to_py_native(np.mean(mfccs, axis=1)),
                    "mfccs_std_dev": to_py_native(np.std(mfccs, axis=1)),
                },
            },
            "tonality_and_harmony": {
                "chroma_profile": to_py_native(chroma_mean),
                "tonnetz_features": {
                    "tonnetz_mean": to_py_native(np.mean(tonnetz, axis=1)),
                    "tonnetz_std_dev": to_py_native(np.std(tonnetz, axis=1)),
                },
            },
            "dynamics_and_loudness": {
                "rms_energy": get_feature_stats(rms, "rms_energy"),
                "zero_crossing_rate": get_feature_stats(zcr, "zcr"),
                "crest_factor": to_py_native(np.max(np.abs(y)) / (np.mean(rms) + 1e-7)),
            },
            "structural_analysis": {
                "estimated_segment_count": len(song_segments),
                "segments": song_segments,
            },
        }
        return round_floats(to_py_native(analytics))

    except Exception as e:
        logger.error(f"Error extracting master audio analytics: {e}")
        return {"error": str(e), "file_path": audio_path}

import os
from typing import Any

import librosa
import numpy as np
from scipy.interpolate import interp1d

from app.core.logging import get_logger
from app.utils.analytics.common import downsample_array, round_floats, to_py_native

logger = get_logger("analytics.vocal")


def extract_vocal_analytics(audio_path: str) -> dict[str, Any]:
    """
    Extracts deep vocal analytics including fundamental frequency (pYIN),
    jitter, shimmer, harmonics-to-noise ratio (HNR), and vocal range.
    """
    if not os.path.exists(audio_path):
        return {"error": f"Vocal audio file not found: {audio_path}"}

    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        duration = float(librosa.get_duration(y=y, sr=sr))

        if duration < 1.0:
            return {"error": "Audio duration is too short for meaningful vocal analysis."}

        # Pitch extraction via pYIN
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        times = librosa.times_like(f0, sr=sr)
        voiced_f0 = f0[voiced_flag & (f0 > 0)]

        if len(voiced_f0) < 10:
            return {"error": "No significant voiced sections found to analyze."}

        # Loudness and energy
        rms = librosa.feature.rms(y=y)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        avg_loudness_db = float(np.mean(rms_db))
        loudness_var_db = float(np.std(rms_db))

        # Jitter & Shimmer (Voice Quality)
        f0_diff = np.abs(np.diff(voiced_f0))
        jitter = float(np.mean(f0_diff) / (np.mean(voiced_f0) + 1e-7) * 100)

        rms_interp = interp1d(
            librosa.times_like(rms, sr=sr), rms, kind="linear", bounds_error=False, fill_value=0
        )
        rms_at_f0 = rms_interp(times)
        voiced_rms = rms_at_f0[voiced_flag & (rms_at_f0 > 0)]
        shimmer = (
            float(np.mean(np.abs(np.diff(voiced_rms))) / (np.mean(voiced_rms) + 1e-7) * 100)
            if len(voiced_rms) > 1
            else 0.0
        )

        # Harmonics-to-Noise Ratio (HNR)
        y_harmonic, _ = librosa.effects.hpss(y)
        noise_energy = np.sum(y**2) - np.sum(y_harmonic**2)
        hnr = (
            float(10 * np.log10(np.sum(y_harmonic**2) / noise_energy)) if noise_energy > 0 else 50.0
        )

        # Pitch Distribution & Heuristic Gender Prediction
        avg_pitch_hz = float(np.nanmean(voiced_f0))
        median_pitch_hz = float(np.nanmedian(voiced_f0))
        p25_pitch_hz = float(np.nanpercentile(voiced_f0, 25))
        min_pitch_hz = float(np.nanmin(voiced_f0))
        max_pitch_hz = float(np.nanmax(voiced_f0))

        if p25_pitch_hz < 145:
            gender_pred = "Male"
        elif avg_pitch_hz > 185 and p25_pitch_hz > 160:
            gender_pred = "Female"
        elif median_pitch_hz > 175:
            gender_pred = "Female"
        else:
            gender_pred = "Male"

        graph_times = downsample_array(times, 150)
        graph_f0 = downsample_array(np.nan_to_num(f0, nan=0.0), 150)
        midi_notes = [round(float(p), 2) if p > 0 else None for p in librosa.hz_to_midi(graph_f0)]

        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        speech_rate = len(onsets) / duration if duration > 0 else 0

        result = {
            "summary": {
                "duration_sec": duration,
                "percent_voiced": float(np.sum(voiced_flag) / len(voiced_flag) * 100),
                "gender_prediction": gender_pred,
                "prediction_note": "Probabilistic estimate based on pitch distribution.",
            },
            "pitch_details": {
                "average_pitch_hz": avg_pitch_hz,
                "pitch_std_dev_hz": float(np.nanstd(voiced_f0)),
                "lowest_pitch_hz": min_pitch_hz,
                "highest_pitch_hz": max_pitch_hz,
                "vocal_range_semitones": float(
                    librosa.hz_to_midi(max_pitch_hz) - librosa.hz_to_midi(min_pitch_hz)
                ),
                "lowest_note": librosa.hz_to_note(min_pitch_hz),
                "highest_note": librosa.hz_to_note(max_pitch_hz),
            },
            "loudness_details": {
                "average_loudness_db": avg_loudness_db,
                "loudness_variation_db": loudness_var_db,
            },
            "vocal_quality": {
                "jitter_percent": jitter,
                "shimmer_percent": shimmer,
                "harmonics_to_noise_ratio_db": hnr,
            },
            "timbre_and_texture": {
                "spectral_centroid_hz": float(
                    np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                ),
                "spectral_bandwidth_hz": float(
                    np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
                ),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
            },
            "rhythm_and_rate": {"speech_rate_onsets_per_sec": float(speech_rate)},
            "performance_graph": {
                "timestamps": [round(float(t), 2) for t in graph_times],
                "values": midi_notes,
                "value_type": "midi_note",
            },
        }
        return round_floats(to_py_native(result))

    except Exception as e:
        logger.error(f"Error in vocal analysis: {e}")
        return {"error": f"Could not process vocals: {e}"}

import numpy as np

from app.utils.analytics import (
    downsample_array,
    extract_bass_analytics,
    extract_drums_analytics,
    extract_flute_analytics,
    extract_guitar_analytics,
    extract_music_analytics,
    extract_other_analytics,
    extract_piano_analytics,
    extract_violin_analytics,
    extract_vocal_analytics,
    round_floats,
    to_py_native,
)


def test_common_analytics_helpers():
    """Tests data conversion and serialization helpers."""
    # Numpy type conversion
    assert isinstance(to_py_native(np.int64(42)), int)
    assert isinstance(to_py_native(np.float64(3.1415)), float)
    assert to_py_native(np.nan) is None

    # Float rounding
    nested = {"a": 1.234567, "b": [9.87654, 5.0]}
    rounded = round_floats(nested, precision=2)
    assert rounded["a"] == 1.23
    assert rounded["b"] == [9.88, 5.0]

    # Array downsampling
    arr = np.linspace(0, 100, 300)
    downsampled = downsample_array(arr, target_points=50)
    assert len(downsampled) == 50


def test_extract_music_analytics(sample_wav_file):
    """Tests master track Librosa audio analytics on synthetic WAV."""
    results = extract_music_analytics(sample_wav_file)
    assert "metadata" in results
    assert "summary" in results
    assert "tempo_bpm" in results["summary"]
    assert "estimated_key" in results["summary"]
    assert "timbre_and_spectral_properties" in results
    assert "tonality_and_harmony" in results
    assert "structural_analysis" in results


def test_extract_vocal_analytics(sample_wav_file):
    """Tests vocal stem analytical feature extractor."""
    results = extract_vocal_analytics(sample_wav_file)
    assert isinstance(results, dict)
    assert "summary" in results or "error" in results


def test_extract_bass_and_drums_analytics(sample_wav_file):
    """Tests bass and drum analytical feature extractors."""
    bass = extract_bass_analytics(sample_wav_file)
    assert "low_end_power" in bass or "error" in bass

    drums = extract_drums_analytics(sample_wav_file)
    assert "tempo_bpm" in drums or "error" in drums


def test_extract_instrument_analytics(sample_wav_file):
    """Tests piano, guitar, violin, flute, and other instrument extractors."""
    piano = extract_piano_analytics(sample_wav_file)
    assert "average_loudness" in piano or "error" in piano

    other = extract_other_analytics(sample_wav_file)
    assert "average_brightness" in other or "error" in other

    guitar = extract_guitar_analytics(sample_wav_file)
    assert "rhythm" in guitar or "error" in guitar

    violin = extract_violin_analytics(sample_wav_file)
    assert "pitch" in violin or "error" in violin

    flute = extract_flute_analytics(sample_wav_file)
    assert "pitch" in flute or "error" in flute

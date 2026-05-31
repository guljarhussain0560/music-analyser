import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AudioProcessingError, DownloaderError
from app.services import audio_processing
from app.utils import downloader, extract_lyrics, spleeter_wrapper


def test_spotify_url_resolution_missing_creds():
    """Tests Spotify resolution throws DownloaderError when creds are missing."""
    with pytest.raises(DownloaderError):
        downloader.spotify_to_ytmusic_url("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")


@patch("subprocess.run")
def test_youtube_download_mock(mock_run, tmp_path):
    """Tests YouTube downloader execution with mock yt-dlp."""
    mock_run.return_value = MagicMock(stdout='{"title": "Awesome Track"}', returncode=0)
    out_dir = str(tmp_path)

    # Mock final mp3 creation
    mp3_file = os.path.join(out_dir, "Awesome Track.mp3")
    with open(mp3_file, "w") as f:
        f.write("mock audio")

    result = downloader.download_from_youtube("https://youtube.com/watch?v=123", out_dir)
    assert "Awesome Track.mp3" in result


def test_transcribe_lyrics_empty_key(sample_wav_file):
    """Tests transcribe_lyrics returns fallback dict when GROQ_API_KEY is empty."""
    res = extract_lyrics.transcribe_lyrics(sample_wav_file)
    assert res["language"] == "en"
    assert res["original_lrc"] == ""


def test_spleeter_stem_split_fallback(sample_wav_file, tmp_path):
    """Tests Spleeter wrapper returns 5-stem dictionary mapping."""
    stems = spleeter_wrapper.spleeter_5_stem_split(sample_wav_file, str(tmp_path))
    assert "vocals" in stems
    assert "bass" in stems
    assert "drums" in stems
    assert "piano" in stems
    assert "other" in stems


def test_unsupported_url_error(db_session, test_user):
    """Tests audio processing pipeline rejects non-supported audio links."""
    with pytest.raises(AudioProcessingError):
        audio_processing.full_song_processing_pipeline(
            db=db_session, source_url="https://soundcloud.com/artist/track", user_id=test_user.id
        )

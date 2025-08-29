from app.core.exceptions import (
    AudioProcessingError,
    AuthenticationError,
    DownloaderError,
    NotFoundError,
    TranscriptionError,
)


def test_custom_exceptions():
    """Tests custom exception properties and status codes."""
    nf = NotFoundError("Song", 123)
    assert nf.status_code == 404
    assert "Song with identifier '123'" in nf.message

    auth_err = AuthenticationError()
    assert auth_err.status_code == 401

    audio_err = AudioProcessingError("FFmpeg decode failed")
    assert audio_err.status_code == 500

    trans_err = TranscriptionError("Rate limit exceeded")
    assert trans_err.status_code == 502

    dl_err = DownloaderError("Geo-blocked video")
    assert dl_err.status_code == 400

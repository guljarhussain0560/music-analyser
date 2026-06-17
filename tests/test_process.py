import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.dto import schemas
from app.services import crud


def test_get_lyrics_endpoint(client: TestClient, db_session, test_user):
    """Tests GET /api/process/get-lyrics/{song_id}."""
    song_in = schemas.SongCreateDTO(
        title="Harmonic Flow",
        owner_id=test_user.id,
        song_url="https://s3.amazonaws.com/audio.mp3",
        lyrics={
            "original_lrc": "[00:01.00]Line one\n[00:04.00]Line two",
            "language": "en",
            "duration": 10.0,
        },
    )
    song = crud.create_song(db_session, song_in)

    response = client.get(f"/api/process/get-lyrics/{song.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "[00:01.00]" in data["original_lrc"]


def test_get_lyrics_not_found(client: TestClient):
    """Tests GET /api/process/get-lyrics/99999 returns 404."""
    response = client.get("/api/process/get-lyrics/99999")
    assert response.status_code == 404


def test_rewrite_lyrics_endpoint(client: TestClient, db_session, test_user):
    """Tests POST /api/process/rewrite-lyrics/{song_id}."""
    song_in = schemas.SongCreateDTO(
        title="Acoustic Melody",
        owner_id=test_user.id,
        song_url="https://s3.amazonaws.com/audio.mp3",
        lyrics={"original_lrc": "[00:01.00]Original words", "language": "en", "duration": 5.0},
    )
    song = crud.create_song(db_session, song_in)

    payload = {"prompt": "Translate to poetic prose"}
    response = client.post(f"/api/process/rewrite-lyrics/{song.id}", json=payload)
    assert response.status_code == 200
    assert "lyrics" in response.json()


@patch("app.services.audio_processing.full_song_processing_pipeline")
def test_process_url_endpoint(mock_pipeline, client: TestClient, test_user):
    """Tests POST /api/process/process_url with mocked pipeline."""
    mock_pipeline.return_value = {"songs_id": 101, "splits_id": 202}

    payload = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "id": test_user.id}
    response = client.post("/api/process/process_url", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["songs_id"] == 101
    assert data["splits_id"] == 202


@patch("app.services.audio_processing.process_audio_file_pipeline")
def test_process_audio_file_endpoint(mock_pipeline, client: TestClient, test_user):
    """Tests POST /api/process/process_audio_file multipart upload."""
    mock_pipeline.return_value = {"songs_id": 303, "splits_id": 404}

    file_content = b"fake-audio-binary-data"
    files = {"audio_file": ("track.mp3", io.BytesIO(file_content), "audio/mpeg")}
    data = {"user_id": str(test_user.id)}

    response = client.post("/api/process/process_audio_file", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["songs_id"] == 303
    assert res_data["splits_id"] == 404

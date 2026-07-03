from fastapi.testclient import TestClient

from app.dto import schemas
from app.services import crud


def test_all_instrument_analytics_endpoints(client: TestClient, db_session, test_user):
    """Tests all GET /api/analytics/splits/{instrument}/{song_id} routes."""
    song_in = schemas.SongCreateDTO(
        title="Orchestral Suite",
        owner_id=test_user.id,
        song_url="https://s3.amazonaws.com/orchestral.mp3",
        lyrics={"original_lrc": "[00:01.00]Instrumental"},
    )
    song = crud.create_song(db_session, song_in)

    split_in = schemas.SplitCreateDTO(
        song_id=song.id,
        vocals_audio_url="https://s3.amazonaws.com/vocals.mp3",
        vocals_description={"average_pitch_hz": 220.0},
        bass_audio_url="https://s3.amazonaws.com/bass.mp3",
        bass_description={"low_end_power": 0.8},
        piano_audio_url="https://s3.amazonaws.com/piano.mp3",
        piano_description={"harmonic_complexity": 0.5},
        drum_audio_url="https://s3.amazonaws.com/drums.mp3",
        drum_description={"tempo_bpm": 120.0},
        other_audio_url="https://s3.amazonaws.com/other.mp3",
        other_description={"average_brightness": 1500.0},
        guitar_description={"chord_style_prediction": "Power Chords"},
        violin_description={"vibrato_rate_hz": 5.5},
        flute_description={"legato_score": 0.9},
    )
    crud.create_split(db_session, split_in)

    # Master song
    res_song = client.get(f"/api/analytics/songs/{song.id}")
    assert res_song.status_code == 200
    assert res_song.json()["title"] == "Orchestral Suite"

    # Vocals
    res = client.get(f"/api/analytics/splits/vocals/{song.id}")
    assert res.status_code == 200
    assert res.json()["vocals_audio_url"] == "https://s3.amazonaws.com/vocals.mp3"

    # Bass
    res = client.get(f"/api/analytics/splits/bass/{song.id}")
    assert res.status_code == 200
    assert res.json()["bass_audio_url"] == "https://s3.amazonaws.com/bass.mp3"

    # Piano
    res = client.get(f"/api/analytics/splits/piano/{song.id}")
    assert res.status_code == 200
    assert res.json()["piano_audio_url"] == "https://s3.amazonaws.com/piano.mp3"

    # Drums
    res = client.get(f"/api/analytics/splits/drums/{song.id}")
    assert res.status_code == 200
    assert res.json()["drum_audio_url"] == "https://s3.amazonaws.com/drums.mp3"

    # Other
    res = client.get(f"/api/analytics/splits/other/{song.id}")
    assert res.status_code == 200
    assert res.json()["other_audio_url"] == "https://s3.amazonaws.com/other.mp3"

    # Guitar
    res = client.get(f"/api/analytics/splits/guitar/{song.id}")
    assert res.status_code == 200
    assert res.json()["guitar_description"]["chord_style_prediction"] == "Power Chords"

    # Violin
    res = client.get(f"/api/analytics/splits/violin/{song.id}")
    assert res.status_code == 200
    assert res.json()["violin_description"]["vibrato_rate_hz"] == 5.5

    # Flute
    res = client.get(f"/api/analytics/splits/flute/{song.id}")
    assert res.status_code == 200
    assert res.json()["flute_description"]["legato_score"] == 0.9

    # Not found cases
    assert client.get("/api/analytics/songs/99999").status_code == 404
    assert client.get("/api/analytics/splits/vocals/99999").status_code == 404
    assert client.get("/api/analytics/splits/bass/99999").status_code == 404
    assert client.get("/api/analytics/splits/piano/99999").status_code == 404
    assert client.get("/api/analytics/splits/drums/99999").status_code == 404
    assert client.get("/api/analytics/splits/other/99999").status_code == 404
    assert client.get("/api/analytics/splits/guitar/99999").status_code == 404
    assert client.get("/api/analytics/splits/violin/99999").status_code == 404
    assert client.get("/api/analytics/splits/flute/99999").status_code == 404

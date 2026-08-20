from unittest.mock import patch

from app.services import audio_processing, crud


def fake_s3_upload(file_path, object_name=None):
    return f"https://s3.amazonaws.com/{object_name or 'audio.mp3'}"


def fake_process_stem(wav_path, mp3_dir, session_id):
    return "stem", f"https://s3.amazonaws.com/stems/{session_id}/stem.mp3"


def test_full_song_pipeline_youtube_mock(db_session, test_user, sample_wav_file):
    """
    End-to-end integration test of the full YouTube audio pipeline with mocked DSP & network calls.
    Verifies that execute_pipeline creates Song and Split database records without network calls.
    """
    with (
        patch("app.services.audio_processing.download_from_youtube") as mock_dl,
        patch("app.services.audio_processing.spleeter_5_stem_split") as mock_spleeter,
        patch("app.services.audio_processing.transcribe_lyrics") as mock_transcribe,
        patch(
            "app.services.audio_processing.s3_uploader.upload_file_to_s3",
            side_effect=fake_s3_upload,
        ),
        patch(
            "app.services.audio_processing.process_and_upload_stem", side_effect=fake_process_stem
        ),
        patch("app.services.audio_processing.run_analysis_in_parallel") as mock_parallel,
    ):
        mock_dl.return_value = sample_wav_file
        mock_spleeter.return_value = {
            "vocals": sample_wav_file,
            "bass": sample_wav_file,
            "drums": sample_wav_file,
            "piano": sample_wav_file,
            "other": sample_wav_file,
        }
        mock_transcribe.return_value = {
            "language": "en",
            "duration": 2.0,
            "segments": [{"start": 0.0, "end": 2.0, "text": "Integration test vocal line"}],
            "original_lrc": "[00:00.00]Integration test vocal line",
        }
        mock_parallel.return_value = {
            "vocal": {"average_pitch_hz": 220.0},
            "bass": {"low_end_power": 0.8},
            "drums": {"tempo_bpm": 120.0},
            "piano": {"harmonic_complexity": 0.5},
            "other": {"average_brightness": 1200.0},
            "guitar": {"chord_style_prediction": "Standard"},
            "violin": {"vibrato_rate_hz": 5.0},
            "flute": {"legato_score": 0.8},
        }

        result = audio_processing.full_song_processing_pipeline(
            db=db_session,
            source_url="https://youtube.com/watch?v=integration_test",
            user_id=test_user.id,
        )

        assert "songs_id" in result
        assert "splits_id" in result

        song = crud.get_song(db_session, result["songs_id"])
        assert song is not None
        assert song.owner_id == test_user.id
        assert song.lyrics["original_lrc"] == "[00:00.00]Integration test vocal line"

        split = crud.get_split_by_song_id(db_session, result["songs_id"])
        assert split is not None
        assert split.vocals_audio_url is not None


def test_process_audio_file_pipeline_mock(db_session, test_user, sample_wav_file):
    """
    End-to-end integration test of direct file upload pipeline.
    """
    with (
        patch("app.services.audio_processing.spleeter_5_stem_split") as mock_spleeter,
        patch("app.services.audio_processing.transcribe_lyrics") as mock_transcribe,
        patch(
            "app.services.audio_processing.s3_uploader.upload_file_to_s3",
            side_effect=fake_s3_upload,
        ),
        patch(
            "app.services.audio_processing.process_and_upload_stem", side_effect=fake_process_stem
        ),
        patch("app.services.audio_processing.run_analysis_in_parallel") as mock_parallel,
    ):
        mock_spleeter.return_value = {
            "vocals": sample_wav_file,
            "bass": sample_wav_file,
            "drums": sample_wav_file,
            "piano": sample_wav_file,
            "other": sample_wav_file,
        }
        mock_transcribe.return_value = {
            "language": "en",
            "duration": 2.0,
            "segments": [],
            "original_lrc": "[00:00.00]Instrumental",
        }
        mock_parallel.return_value = {
            "vocal": {"average_pitch_hz": 220.0},
            "bass": {"low_end_power": 0.8},
            "drums": {"tempo_bpm": 120.0},
            "piano": {"harmonic_complexity": 0.5},
            "other": {"average_brightness": 1200.0},
            "guitar": {"chord_style_prediction": "Standard"},
            "violin": {"vibrato_rate_hz": 5.0},
            "flute": {"legato_score": 0.8},
        }

        result = audio_processing.process_audio_file_pipeline(
            db=db_session, file_path=sample_wav_file, user_id=test_user.id
        )

        assert "songs_id" in result
        assert "splits_id" in result

        song = crud.get_song(db_session, result["songs_id"])
        assert song is not None

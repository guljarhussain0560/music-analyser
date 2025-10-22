from sqlalchemy.orm import Session

from app.dto import schemas
from app.services import crud


def test_user_crud_lifecycle(db_session: Session):
    """Tests full CRUD operations for User model."""
    # Create
    user_in = schemas.UserCreate(
        email="producer@beatlab.io",
        username="beatmaker",
        password="MySecretPassword123!",
        name="Beat Maker",
    )
    user = crud.create_user(db_session, user_in)
    assert user.id is not None
    assert user.email == "producer@beatlab.io"
    assert user.username == "beatmaker"

    # Read by ID
    fetched_by_id = crud.get_user(db_session, user.id)
    assert fetched_by_id is not None
    assert fetched_by_id.email == "producer@beatlab.io"

    # Read by Email
    fetched_by_email = crud.get_user_by_email(db_session, "producer@beatlab.io")
    assert fetched_by_email is not None
    assert fetched_by_email.id == user.id

    # Read by Username
    fetched_by_username = crud.get_user_by_username(db_session, "beatmaker")
    assert fetched_by_username is not None
    assert fetched_by_username.id == user.id

    # Update Password
    updated_user = crud.update_user_password(db_session, user.id, "NewSecurePassword456!")
    assert updated_user is not None
    assert updated_user.hashed_password != user_in.password


def test_song_and_split_crud(db_session: Session, test_user):
    """Tests creating and querying songs and stem splits."""
    # Create Song
    song_in = schemas.SongCreateDTO(
        title="Electronic Dream",
        owner_id=test_user.id,
        song_url="https://s3.amazonaws.com/songs/electronic_dream.mp3",
        lyrics={"original_lrc": "[00:01.00]Hello World"},
        description={"tempo_bpm": 128.0, "estimated_key": "A Minor"},
    )
    song = crud.create_song(db_session, song_in)
    assert song.id is not None
    assert song.title == "Electronic Dream"
    assert song.owner_id == test_user.id

    # Query Song
    fetched_song = crud.get_song(db_session, song.id)
    assert fetched_song is not None
    assert fetched_song.description["tempo_bpm"] == 128.0

    # Create Split
    split_in = schemas.SplitCreateDTO(
        song_id=song.id,
        vocals_audio_url="https://s3.amazonaws.com/stems/vocals.mp3",
        bass_audio_url="https://s3.amazonaws.com/stems/bass.mp3",
        vocals_description={"average_pitch_hz": 220.0},
        bass_description={"dominant_note": "A"},
    )
    split = crud.create_split(db_session, split_in)
    assert split.id is not None
    assert split.song_id == song.id

    # Query Split by Song ID
    fetched_split = crud.get_split_by_song_id(db_session, song.id)
    assert fetched_split is not None
    assert fetched_split.vocals_audio_url == "https://s3.amazonaws.com/stems/vocals.mp3"
    assert fetched_split.bass_description["dominant_note"] == "A"


def test_otp_crud_lifecycle(db_session: Session):
    """Tests OTP creation and validation."""
    email = "recovery@example.com"
    otp = "492817"

    record = crud.create_password_reset_otp(db_session, email=email, otp=otp, expires_minutes=10)
    assert record.id is not None
    assert record.is_used is False

    # Verify invalid OTP
    assert crud.verify_password_reset_otp(db_session, email=email, otp="000000") is False

    # Verify valid OTP
    assert crud.verify_password_reset_otp(db_session, email=email, otp=otp) is True

    # Ensure single-use: cannot verify again
    assert crud.verify_password_reset_otp(db_session, email=email, otp=otp) is False

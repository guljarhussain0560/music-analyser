import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.logging import get_logger
from app.dto import schemas
from app.services import audio_processing, crud
from app.utils.lyrics_aligner import rewrite_lyrics_with_timestamps

logger = get_logger("routes.process")
router = APIRouter(prefix="/process", tags=["Audio Processing"])


@router.post("/process_url", response_model=dict)
def process_song_url(request: schemas.SongRequest, db: Session = Depends(get_db)):
    """Processes a YouTube or Spotify audio link through the full ML pipeline."""
    user = crud.get_user(db, user_id=request.id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {request.id} not found.")

    logger.info(f"Received URL processing request for User {request.id}: {request.url}")
    results = audio_processing.full_song_processing_pipeline(
        db=db, source_url=request.url, user_id=request.id
    )
    if not results:
        raise HTTPException(status_code=500, detail="Song processing pipeline failed.")
    return results


@router.post("/process_audio_file", response_model=dict)
def process_audio_file(
    user_id: int = Form(...), audio_file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Processes an uploaded audio file directly through stem separation and analytics."""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

    temp_dir = tempfile.mkdtemp(prefix="audio_upload_")
    safe_filename = os.path.basename(audio_file.filename or "uploaded_audio.mp3")
    temp_file_path = os.path.join(temp_dir, safe_filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        logger.info(f"Processing uploaded audio '{safe_filename}' for User {user_id}")
        results = audio_processing.process_audio_file_pipeline(
            db=db, file_path=temp_file_path, user_id=user_id
        )
        if not results:
            raise HTTPException(status_code=500, detail="Uploaded audio processing failed.")
        return results

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        audio_file.file.close()


@router.get("/get-lyrics/{song_id}", response_model=dict)
def get_song_lyrics(song_id: int, db: Session = Depends(get_db)):
    """Retrieves extracted timestamped LRC lyrics for a song."""
    song = crud.get_lyrics_by_song_id(db, song_id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song with ID {song_id} not found")
    return song.lyrics or {}


@router.post("/rewrite-lyrics/{song_id}", response_model=schemas.RewriteResponse)
def rewrite_song_lyrics(
    song_id: int, request: schemas.RewriteRequest, db: Session = Depends(get_db)
):
    """Rewrites lyrics for a song according to user prompt while preserving LRC timestamps."""
    song = crud.get_lyrics_by_song_id(db, song_id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song with ID {song_id} not found")

    lyrics_data = song.lyrics or {}
    duration = float(lyrics_data.get("duration", 0.0))
    language = str(lyrics_data.get("language", "en"))
    lrc = str(lyrics_data.get("original_lrc", ""))

    if not lrc:
        raise HTTPException(
            status_code=400, detail="Song does not contain transcribed lyrics to rewrite."
        )

    new_lyrics = rewrite_lyrics_with_timestamps(
        lrc_string=lrc, language=language, duration=duration, user_prompt=request.prompt
    )
    return {"lyrics": new_lyrics}

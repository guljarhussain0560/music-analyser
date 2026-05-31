import os
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydub import AudioSegment
from sqlalchemy.orm import Session

from app.core.exceptions import AudioProcessingError
from app.core.logging import get_logger
from app.dto import schemas
from app.services import crud, s3_uploader
from app.utils import (
    download_from_spotify,
    download_from_youtube,
    extract_music_analytics,
    run_analysis_in_parallel,
    spleeter_5_stem_split,
    transcribe_lyrics,
)

logger = get_logger("audio_pipeline")


def process_and_upload_stem(wav_path: str, mp3_dir: str, session_id: str) -> tuple[str, str] | None:
    """Converts WAV stem to lightweight MP3 and uploads it to S3."""
    if not os.path.exists(wav_path):
        return None

    stem_name = os.path.splitext(os.path.basename(wav_path))[0]
    mp3_path = os.path.join(mp3_dir, f"{stem_name}.mp3")

    try:
        sound = AudioSegment.from_wav(wav_path)
        sound.export(mp3_path, format="mp3", bitrate="192k")

        s3_key = f"stems/{session_id}/{stem_name}.mp3"
        s3_url = s3_uploader.upload_file_to_s3(mp3_path, object_name=s3_key)
        return stem_name, s3_url or ""
    except Exception as e:
        logger.error(f"Failed converting/uploading stem {stem_name}: {e}")
        return None


def execute_pipeline(
    db: Session, audio_file_path: str, user_id: int, title: str, temp_dir: str
) -> dict[str, int]:
    """Executes parallel audio analysis, stem separation, transcription, and database sync."""
    start_time = time.time()
    logger.info(f"Starting parallel audio processing pipeline for '{title}' (User ID: {user_id})")

    stems_dir = os.path.join(temp_dir, "stems")
    os.makedirs(stems_dir, exist_ok=True)

    # Phase 1: Parallel I/O and ML (S3 Upload, Master Analytics, Spleeter Separation, Transcription)
    with ThreadPoolExecutor(max_workers=4) as executor:
        s3_future = executor.submit(
            s3_uploader.upload_file_to_s3,
            audio_file_path,
            f"songs/{user_id}/original_song/{uuid.uuid4()}{os.path.splitext(audio_file_path)[1]}",
        )
        analytics_future = executor.submit(extract_music_analytics, audio_file_path)
        spleeter_future = executor.submit(spleeter_5_stem_split, audio_file_path, stems_dir)
        lyrics_future = executor.submit(transcribe_lyrics, audio_file_path)

        s3_song_url = s3_future.result() or "http://local-audio-storage.invalid"
        music_desc = analytics_future.result()
        lyrics_data = lyrics_future.result()
        spleeter_results = spleeter_future.result()

    logger.info(
        "Phase 1 complete: Master analytics, stem separation, and lyric transcription ready."
    )

    # Phase 2: Initial Database Record
    song_dto = schemas.SongCreateDTO(
        title=title,
        owner_id=user_id,
        song_url=s3_song_url,
        lyrics=lyrics_data,
        description=music_desc,
    )
    new_song = crud.create_song(db=db, song=song_dto)

    # Phase 3: Stem Conversion & S3 Upload
    conv_mp3_dir = os.path.join(temp_dir, "stems_mp3")
    os.makedirs(conv_mp3_dir, exist_ok=True)
    session_id = str(uuid.uuid4())
    stem_urls: dict[str, str | None] = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(process_and_upload_stem, wav_path, conv_mp3_dir, session_id): stem
            for stem, wav_path in spleeter_results.items()
        }
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                stem_urls[res[0]] = res[1]

    # Phase 4: Parallel Multiprocessing Stem Analytics
    input_stem_dir = (
        os.path.dirname(list(spleeter_results.values())[0]) if spleeter_results else stems_dir
    )
    stem_analytics = run_analysis_in_parallel(input_stem_dir)

    # Phase 5: Persist Splits to Database
    split_dto = schemas.SplitCreateDTO(
        song_id=new_song.id,
        vocals_audio_url=stem_urls.get("vocals"),
        vocals_description=stem_analytics.get("vocal"),
        bass_audio_url=stem_urls.get("bass"),
        bass_description=stem_analytics.get("bass"),
        drum_audio_url=stem_urls.get("drums"),
        drum_description=stem_analytics.get("drums"),
        piano_audio_url=stem_urls.get("piano"),
        piano_description=stem_analytics.get("piano"),
        other_audio_url=stem_urls.get("other"),
        other_description=stem_analytics.get("other"),
        guitar_description=stem_analytics.get("guitar"),
        violin_description=stem_analytics.get("violin"),
        flute_description=stem_analytics.get("flute"),
    )
    new_split = crud.create_split(db=db, split=split_dto)

    elapsed = time.time() - start_time
    logger.info(
        f"Pipeline finished successfully in {elapsed:.2f}s (Song ID: {new_song.id}, Split ID: {new_split.id})"
    )

    return {"songs_id": new_song.id, "splits_id": new_split.id}


def full_song_processing_pipeline(db: Session, source_url: str, user_id: int) -> dict[str, int]:
    """Orchestrates URL download followed by complete audio pipeline."""
    with tempfile.TemporaryDirectory() as temp_dir:
        out_loc = os.path.join(temp_dir, "downloaded")
        if "youtube.com" in source_url or "youtu.be" in source_url:
            audio_path = download_from_youtube(source_url, out_loc)
        elif "spotify.com" in source_url:
            audio_path = download_from_spotify(source_url, out_loc)
        else:
            raise AudioProcessingError(
                "Unsupported source URL. Please provide YouTube or Spotify track link."
            )

        title = os.path.splitext(os.path.basename(audio_path))[0]
        return execute_pipeline(db, audio_path, user_id, title, temp_dir)


def process_audio_file_pipeline(db: Session, file_path: str, user_id: int) -> dict[str, int]:
    """Orchestrates pipeline for direct file uploads."""
    temp_dir = os.path.dirname(file_path)
    title = os.path.splitext(os.path.basename(file_path))[0]
    return execute_pipeline(db, file_path, user_id, title, temp_dir)

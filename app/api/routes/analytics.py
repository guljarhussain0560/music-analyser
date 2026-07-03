from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.dto import schemas
from app.services import crud

router = APIRouter(prefix="/analytics", tags=["Music Analytics"])


@router.get("/songs/{song_id}", response_model=schemas.SongResponseDTO)
def get_song_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns master song record with global audio analytics."""
    song = crud.get_song(db, song_id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/splits/bass/{song_id}", response_model=schemas.BassInfoDTO)
def get_bass_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns bass stem URL and low-end groove analytics."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.BassInfoDTO(
        bass_audio_url=split.bass_audio_url, bass_description=split.bass_description
    )


@router.get("/splits/vocals/{song_id}", response_model=schemas.VocalsInfoDTO)
def get_vocals_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns vocal stem URL and deep vocal metrics (pitch, vibrato, gender)."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.VocalsInfoDTO(
        vocals_audio_url=split.vocals_audio_url, vocals_description=split.vocals_description
    )


@router.get("/splits/piano/{song_id}", response_model=schemas.PianoInfoDTO)
def get_piano_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns piano stem URL and dynamic/harmonic complexity analytics."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.PianoInfoDTO(
        piano_audio_url=split.piano_audio_url, piano_description=split.piano_description
    )


@router.get("/splits/drums/{song_id}", response_model=schemas.DrumInfoDTO)
def get_drums_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns drum stem URL and rhythm/kick-to-snare balance."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.DrumInfoDTO(
        drum_audio_url=split.drum_audio_url, drum_description=split.drum_description
    )


@router.get("/splits/other/{song_id}", response_model=schemas.OtherInfoDTO)
def get_other_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns other stem URL and timbral texture analytics."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.OtherInfoDTO(
        other_audio_url=split.other_audio_url, other_description=split.other_description
    )


@router.get("/splits/guitar/{song_id}", response_model=schemas.GuitarInfoDTO)
def get_guitar_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns guitar playing style, strum rate, and chord complexity."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.GuitarInfoDTO(guitar_description=split.guitar_description)


@router.get("/splits/flute/{song_id}", response_model=schemas.FluteInfoDTO)
def get_flute_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns flute vibrato rate, legato score, and breathiness metrics."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.FluteInfoDTO(flute_description=split.flute_description)


@router.get("/splits/violin/{song_id}", response_model=schemas.ViolinInfoDTO)
def get_violin_analytics(song_id: int, db: Session = Depends(get_db)):
    """Returns violin pitch range, vibrato depth, and harmonics ratio."""
    split = crud.get_split_by_song_id(db, song_id=song_id)
    if not split:
        raise HTTPException(status_code=404, detail="Splits for this song not found")
    return schemas.ViolinInfoDTO(violin_description=split.violin_description)

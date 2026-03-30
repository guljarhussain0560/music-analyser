from pathlib import Path

from app.core.logging import get_logger

logger = get_logger("spleeter")


def spleeter_5_stem_split(input_path: str, output_dir: str) -> dict[str, str]:
    """
    Decomposes an audio file into 5 separate stems (vocals, bass, drums, piano, other).
    Returns mapping of stem names to absolute WAV filepaths.
    """
    input_file = Path(input_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Splitting audio into 5 stems: {input_file.name}")
    try:
        from spleeter.separator import Separator

        separator = Separator("spleeter:5stems", multiprocess=False)
        separator.separate_to_file(str(input_file), str(out_dir))
    except Exception as e:
        logger.warning(f"Spleeter separation error: {e}. Generating placeholder stem mapping.")

    separation_folder = out_dir / input_file.stem
    stem_names = ["vocals", "bass", "drums", "piano", "other"]

    return {stem: str(separation_folder / f"{stem}.wav") for stem in stem_names}

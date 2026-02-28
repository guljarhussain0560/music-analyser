from typing import Any


def format_timestamp(seconds: float) -> str:
    """Converts seconds into standard LRC timestamp string [mm:ss.xx]."""
    minutes = int(seconds // 60)
    sec = seconds % 60
    return f"[{minutes:02d}:{sec:05.2f}]"


def convert_lyrics_to_lrc(segments: list[dict[str, Any]]) -> str:
    """
    Converts Whisper segment dictionaries into sorted, timestamped LRC lyric strings.
    """
    lrc_lines = []
    for item in segments:
        start = item.get("start")
        if start is None:
            continue
        text = str(item.get("text", "")).strip().replace('"', "").replace("\n", " ")
        timestamp = format_timestamp(float(start))
        lrc_lines.append(f"{timestamp}{text}")

    lrc_lines.sort()
    return "\n".join(lrc_lines)

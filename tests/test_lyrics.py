from app.utils.lyrics_aligner import rewrite_lyrics_with_timestamps
from app.utils.seg_to_lrc import convert_lyrics_to_lrc, format_timestamp


def test_format_timestamp():
    """Tests seconds to LRC timestamp conversion."""
    assert format_timestamp(0.0) == "[00:00.00]"
    assert format_timestamp(65.25) == "[01:05.25]"
    assert format_timestamp(125.5) == "[02:05.50]"


def test_convert_lyrics_to_lrc():
    """Tests segment array conversion to sorted LRC text."""
    segments = [
        {"start": 12.5, "end": 15.0, "text": "I hear the music playing"},
        {"start": 3.0, "end": 6.0, "text": "Dancing in the dark"},
    ]
    lrc = convert_lyrics_to_lrc(segments)
    lines = lrc.strip().split("\n")
    assert len(lines) == 2
    assert lines[0] == "[00:03.00]Dancing in the dark"
    assert lines[1] == "[00:12.50]I hear the music playing"


def test_rewrite_lyrics_mock():
    """Tests lyric rewriter fallback when GROQ_API_KEY is unset."""
    lrc = "[00:01.00]Hello world\n[00:05.00]Sing a song"
    rewritten = rewrite_lyrics_with_timestamps(
        lrc, language="en", duration=10.0, user_prompt="Make it upbeat"
    )
    assert rewritten == lrc

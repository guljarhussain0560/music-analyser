from app.utils.downloader import sanitize_filename


def test_sanitize_filename():
    """Asserts invalid path characters are stripped from downloaded song titles."""
    dirty = 'My Song: Remix/Version? <Live> "2026" | *Super* \\ Clean'
    clean = sanitize_filename(dirty)
    assert clean == "My Song RemixVersion Live 2026  Super  Clean"
    assert "/" not in clean
    assert ":" not in clean
    assert "<" not in clean

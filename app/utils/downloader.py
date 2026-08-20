import json
import os
import re
import subprocess

from app.core.config import settings
from app.core.exceptions import DownloaderError
from app.core.logging import get_logger

logger = get_logger("downloader")


def sanitize_filename(filename: str) -> str:
    """Strips illegal file path characters to prevent traversal attacks."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()


def download_from_youtube(url: str, output_dir: str) -> str:
    """
    Downloads audio stream from YouTube using yt-dlp with optional cookie authentication.
    """
    logger.info(f"Starting YouTube audio download for: {url}")
    os.makedirs(output_dir, exist_ok=True)

    cookie_args = []
    if settings.YT_COOKIES_PATH and os.path.exists(settings.YT_COOKIES_PATH):
        cookie_args = ["--cookies", settings.YT_COOKIES_PATH]

    try:
        # Extract title and info
        info_cmd = ["yt-dlp", *cookie_args, "--dump-single-json", url]
        result = subprocess.run(
            info_cmd, check=True, capture_output=True, text=True, encoding="utf-8"
        )
        info = json.loads(result.stdout)
        title = info.get("title", "youtube_audio")
        clean_title = sanitize_filename(title)
        output_template = os.path.join(output_dir, f"{clean_title}.%(ext)s")
        final_mp3 = os.path.join(output_dir, f"{clean_title}.mp3")

        # Download & transcode
        download_cmd = [
            "yt-dlp",
            *cookie_args,
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "-o",
            output_template,
            url,
        ]
        subprocess.run(download_cmd, check=True, capture_output=True)
        logger.info(f"YouTube download complete: {final_mp3}")
        return final_mp3

    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        logger.error(f"yt-dlp YouTube download failed: {err_msg}")
        raise DownloaderError(f"YouTube download failed: {err_msg}") from e
    except Exception as e:
        logger.error(f"Unexpected error downloading from YouTube: {e}")
        raise DownloaderError(f"Could not download audio from YouTube: {e}") from e


def spotify_to_ytmusic_url(spotify_url: str) -> str:
    """Queries Spotify track metadata and resolves matching YouTube Music video URL."""
    if not settings.SPOTIPY_CLIENT_ID or not settings.SPOTIPY_CLIENT_SECRET:
        raise DownloaderError("Spotify client credentials not configured in environment.")

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        from ytmusicapi import YTMusic

        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=settings.SPOTIPY_CLIENT_ID, client_secret=settings.SPOTIPY_CLIENT_SECRET
            )
        )
        track_id = spotify_url.split("/")[-1].split("?")[0]
        track = sp.track(track_id)
        artist_name = track["artists"][0]["name"] if track.get("artists") else "Unknown"
        query = f"{track.get('name', '')} {artist_name}".strip()

        ytm = YTMusic()
        results = ytm.search(query, filter="songs")
        if results and len(results) > 0 and "videoId" in results[0]:
            return f"https://music.youtube.com/watch?v={results[0]['videoId']}"
        raise DownloaderError(f"No matching track found on YouTube Music for query: {query}")

    except Exception as e:
        logger.error(f"Failed resolving Spotify track to YouTube Music: {e}")
        raise DownloaderError(f"Spotify track resolution failed: {e}") from e


def download_from_spotify(url: str, output_dir: str) -> str:
    """Downloads audio for a Spotify URL by resolving and fetching the stream from YouTube Music."""
    logger.info(f"Initiating Spotify download: {url}")
    yt_url = spotify_to_ytmusic_url(url)
    return download_from_youtube(yt_url, output_dir)

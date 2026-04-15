import multiprocessing
import os
from typing import Any

from app.core.logging import get_logger
from app.utils.analytics import (
    extract_bass_analytics,
    extract_drums_analytics,
    extract_flute_analytics,
    extract_guitar_analytics,
    extract_other_analytics,
    extract_piano_analytics,
    extract_violin_analytics,
    extract_vocal_analytics,
)

logger = get_logger("parallel_processor")


def run_analysis_in_parallel(stems_output_dir: str) -> dict[str, Any]:
    """
    Executes all CPU-bound instrument and vocal stem analytics across
    multiprocessing worker pools for maximum throughput.
    """
    tasks = [
        ("vocal", extract_vocal_analytics, "vocals.wav"),
        ("bass", extract_bass_analytics, "bass.wav"),
        ("drums", extract_drums_analytics, "drums.wav"),
        ("piano", extract_piano_analytics, "piano.wav"),
        ("other", extract_other_analytics, "other.wav"),
        ("guitar", extract_guitar_analytics, "other.wav"),
        ("violin", extract_violin_analytics, "other.wav"),
        ("flute", extract_flute_analytics, "other.wav"),
    ]

    try:
        with multiprocessing.Pool() as pool:
            async_results = [
                pool.apply_async(func, args=(os.path.join(stems_output_dir, filename),))
                for _, func, filename in tasks
            ]
            results_list = [res.get() for res in async_results]

        return {task[0]: result for task, result in zip(tasks, results_list, strict=False)}
    except Exception as e:
        logger.error(
            f"Multiprocessing audio analysis error: {e}. Falling back to sequential execution."
        )
        results = {}
        for key, func, filename in tasks:
            full_path = os.path.join(stems_output_dir, filename)
            try:
                results[key] = func(full_path)
            except Exception as item_err:
                results[key] = {"error": str(item_err)}
        return results

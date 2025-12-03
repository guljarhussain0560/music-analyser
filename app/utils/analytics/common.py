from typing import Any

import numpy as np
from scipy.stats import kurtosis, skew


def to_py_native(obj: Any) -> Any:
    """
    Recursively converts numpy types and arrays within nested structures
    to native Python types for JSON serialization.
    """
    if obj is None:
        return None
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, int | np.integer):
        return int(obj)
    if isinstance(obj, bool | np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: to_py_native(v) for k, v in obj.items()}
    if isinstance(obj, np.ndarray | list):
        return [to_py_native(v) for v in obj]
    return obj


def round_floats(obj: Any, precision: int = 3) -> Any:
    """Recursively rounds float numbers within dictionaries or lists."""
    if isinstance(obj, dict):
        return {k: round_floats(v, precision) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(i, precision) for i in obj]
    if isinstance(obj, float):
        return round(obj, precision)
    return obj


def get_feature_stats(feature_vector: np.ndarray, feature_name: str) -> dict[str, Any]:
    """Calculates standard descriptive statistics for an audio feature vector."""
    flat = feature_vector.flatten()
    if flat.size == 0:
        return {}
    return {
        f"{feature_name}_mean": to_py_native(np.mean(flat)),
        f"{feature_name}_std_dev": to_py_native(np.std(flat)),
        f"{feature_name}_skewness": to_py_native(skew(flat)),
        f"{feature_name}_kurtosis": to_py_native(kurtosis(flat)),
        f"{feature_name}_median": to_py_native(np.median(flat)),
        f"{feature_name}_min": to_py_native(np.min(flat)),
        f"{feature_name}_max": to_py_native(np.max(flat)),
    }


def downsample_array(arr: np.ndarray, target_points: int = 150) -> np.ndarray:
    """
    Downsamples a 1D numpy array to a target length using chunk averaging
    for lightweight frontend graph visualization.
    """
    if arr is None or len(arr) <= target_points:
        return arr
    original_len = len(arr)
    chunk_size = max(1, original_len // target_points)
    trimmed_len = (original_len // chunk_size) * chunk_size
    arr_trimmed = np.nan_to_num(arr[:trimmed_len], nan=0.0)
    return arr_trimmed.reshape(-1, chunk_size).mean(axis=1)

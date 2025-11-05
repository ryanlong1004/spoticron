"""
Utility functions for Spoticron application.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import math


def format_duration(milliseconds: int) -> str:
    """
    Format duration from milliseconds to readable format.

    Args:
        milliseconds: Duration in milliseconds.

    Returns:
        Formatted duration string (e.g., "3:45", "1:23:45").
    """
    if milliseconds is None:
        return "0:00"

    seconds = milliseconds // 1000
    minutes = seconds // 60
    hours = minutes // 60

    remaining_seconds = seconds % 60
    remaining_minutes = minutes % 60

    if hours > 0:
        return f"{hours}:{remaining_minutes:02d}:{remaining_seconds:02d}"
    return f"{remaining_minutes}:{remaining_seconds:02d}"


def format_number(number: int) -> str:
    """
    Format large numbers with appropriate units.

    Args:
        number: Number to format.

    Returns:
        Formatted number string (e.g., "1.2K", "3.4M").
    """
    if number is None:
        return "0"

    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return str(number)


def calculate_listening_time_stats(durations: List[int]) -> Dict[str, Any]:
    """
    Calculate listening time statistics.

    Args:
        durations: List of track durations in milliseconds.

    Returns:
        Dictionary with listening time statistics.
    """
    if not durations:
        return {
            "total_ms": 0,
            "total_hours": 0,
            "average_track_length": 0,
            "median_track_length": 0,
        }

    total_ms = sum(durations)
    average_ms = total_ms / len(durations)

    # Calculate median
    sorted_durations = sorted(durations)
    n = len(sorted_durations)
    if n % 2 == 0:
        median_ms = (sorted_durations[n // 2 - 1] + sorted_durations[n // 2]) / 2
    else:
        median_ms = sorted_durations[n // 2]

    return {
        "total_ms": total_ms,
        "total_hours": total_ms / (1000 * 60 * 60),
        "average_track_length": average_ms,
        "median_track_length": median_ms,
        "total_tracks": len(durations),
    }


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator value.
        denominator: Denominator value.
        default: Default value to return if division by zero.

    Returns:
        Division result or default value.
    """
    if denominator == 0:
        return default
    return numerator / denominator


def get_time_range_label(time_range: str) -> str:
    """
    Get human-readable label for Spotify time range.

    Args:
        time_range: Spotify time range code.

    Returns:
        Human-readable time range label.
    """
    labels = {
        "short_term": "Last 4 Weeks",
        "medium_term": "Last 6 Months",
        "long_term": "All Time",
    }
    return labels.get(time_range, time_range)


def ensure_directory_exists(path: str) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path.

    Returns:
        Path object for the directory.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from file.

    Args:
        filepath: Path to JSON file.

    Returns:
        Loaded JSON data or None if failed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return None


def save_json_file(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to JSON file.

    Args:
        data: Data to save.
        filepath: Output file path.

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON file {filepath}: {e}")
        return False


def calculate_entropy(values: List[float]) -> float:
    """
    Calculate Shannon entropy for a list of values.

    Args:
        values: List of numeric values.

    Returns:
        Entropy value.
    """
    if not values:
        return 0.0

    total = sum(values)
    if total == 0:
        return 0.0

    entropy = 0.0
    for value in values:
        if value > 0:
            probability = value / total
            entropy -= probability * math.log2(probability)

    return entropy


def get_mood_from_features(audio_features: Dict[str, float]) -> str:
    """
    Determine mood based on audio features.

    Args:
        audio_features: Dictionary of audio features.

    Returns:
        Mood string.
    """
    if not audio_features:
        return "Unknown"

    energy = audio_features.get("energy", 0.5)
    valence = audio_features.get("valence", 0.5)
    danceability = audio_features.get("danceability", 0.5)

    # Simple mood classification
    if energy > 0.7 and valence > 0.7:
        return "Energetic & Happy"
    elif energy > 0.7 and valence < 0.3:
        return "Energetic & Intense"
    elif energy < 0.3 and valence > 0.7:
        return "Calm & Happy"
    elif energy < 0.3 and valence < 0.3:
        return "Calm & Melancholic"
    elif danceability > 0.8:
        return "Danceable"
    elif valence > 0.6:
        return "Upbeat"
    elif valence < 0.4:
        return "Melancholic"
    else:
        return "Balanced"


def generate_timestamp_filename(prefix: str, extension: str = "json") -> str:
    """
    Generate filename with timestamp.

    Args:
        prefix: Filename prefix.
        extension: File extension (without dot).

    Returns:
        Timestamped filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def batch_process(items: List[Any], batch_size: int = 50) -> List[List[Any]]:
    """
    Split items into batches for processing.

    Args:
        items: List of items to batch.
        batch_size: Size of each batch.

    Returns:
        List of batches.
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i : i + batch_size])
    return batches


def retry_on_error(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry function on error with exponential backoff.

    Args:
        func: Function to retry.
        max_retries: Maximum number of retries.
        delay: Initial delay between retries.

    Returns:
        Function result or raises last exception.
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay * (2**attempt))  # Exponential backoff
            else:
                break

    if last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("Function failed with no exception captured")


def validate_spotify_id(spotify_id: str) -> bool:
    """
    Validate Spotify ID format.

    Args:
        spotify_id: Spotify ID to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not spotify_id or not isinstance(spotify_id, str):
        return False

    # Spotify IDs are typically 22 characters long, base62 encoded
    return len(spotify_id) == 22 and spotify_id.isalnum()


def clean_text(text: str) -> str:
    """
    Clean text for safe file naming and display.

    Args:
        text: Text to clean.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""

    # Remove or replace problematic characters
    cleaned = text.replace("/", "_").replace("\\", "_").replace(":", "_")
    cleaned = cleaned.replace("<", "").replace(">", "").replace("|", "_")
    cleaned = cleaned.replace("?", "").replace("*", "").replace('"', "'")

    return cleaned.strip()


def percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value.
        new_value: New value.

    Returns:
        Percentage change.
    """
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0

    return ((new_value - old_value) / old_value) * 100


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum length including suffix.
        suffix: Suffix to add when truncating.

    Returns:
        Truncated text.
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")

    # Test duration formatting
    print(f"Duration: {format_duration(245000)}")  # Should be "4:05"

    # Test number formatting
    print(f"Number: {format_number(1500000)}")  # Should be "1.5M"

    # Test mood detection
    features = {"energy": 0.8, "valence": 0.9, "danceability": 0.7}
    print(f"Mood: {get_mood_from_features(features)}")

    print("Utility functions test completed.")

import json

from core.resources import storage_path

LEADERBOARD_FILE = storage_path("leaderboard.json")


def load_leaderboard_entries():
    _ensure_leaderboard_file()

    try:
        with LEADERBOARD_FILE.open("r", encoding="utf-8") as leaderboard_file:
            raw_entries = json.load(leaderboard_file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(raw_entries, list):
        return []

    entries = []
    for entry in raw_entries:
        normalized_entry = _normalize_entry(entry)
        if normalized_entry is not None:
            entries.append(normalized_entry)

    return sort_leaderboard_entries(entries)


def add_leaderboard_entry(class_name, texture_name, time_seconds, wave_reached):
    entries = load_leaderboard_entries()
    entries.append(
        {
            "class_name": class_name,
            "texture_name": texture_name,
            "time_seconds": round(float(time_seconds), 1),
            "wave_reached": int(wave_reached),
        }
    )
    save_leaderboard_entries(entries)


def save_leaderboard_entries(entries):
    LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LEADERBOARD_FILE.open("w", encoding="utf-8") as leaderboard_file:
        json.dump(sort_leaderboard_entries(entries), leaderboard_file, ensure_ascii=False, indent=2)


def sort_leaderboard_entries(entries):
    return sorted(
        entries,
        key=lambda entry: (-entry["wave_reached"], entry["time_seconds"], entry["class_name"]),
    )


def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds - (minutes * 60)
    return f"{minutes:02d}:{remaining_seconds:04.1f}"


def _ensure_leaderboard_file():
    if LEADERBOARD_FILE.exists():
        return

    LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEADERBOARD_FILE.write_text("[]", encoding="utf-8")


def _normalize_entry(entry):
    if not isinstance(entry, dict):
        return None

    class_name = entry.get("class_name")
    texture_name = entry.get("texture_name")
    if not isinstance(class_name, str) or not isinstance(texture_name, str):
        return None

    try:
        normalized_time = round(float(entry["time_seconds"]), 1)
        normalized_wave = int(entry["wave_reached"])
    except (KeyError, TypeError, ValueError):
        return None

    if normalized_wave < 1 or normalized_time < 0:
        return None

    return {
        "class_name": class_name,
        "texture_name": texture_name,
        "time_seconds": normalized_time,
        "wave_reached": normalized_wave,
    }

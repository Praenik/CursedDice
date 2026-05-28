import json

LEADERBOARD_FILE = "leaderboard.json"


def load_leaderboard_entries():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as leaderboard_file:
            saved_entries = json.load(leaderboard_file)
    except Exception:
        return []

    if type(saved_entries) != list:
        return []

    fixed_entries = []
    for entry in saved_entries:
        try:
            class_name = str(entry["class_name"])
            texture_name = str(entry["texture_name"])
            time_seconds = round(float(entry["time_seconds"]), 1)
            wave_reached = int(entry["wave_reached"])
        except Exception:
            continue

        if wave_reached < 1 or time_seconds < 0:
            continue

        fixed_entries.append(
            {
                "class_name": class_name,
                "texture_name": texture_name,
                "time_seconds": time_seconds,
                "wave_reached": wave_reached,
            }
        )

    return sort_leaderboard_entries(fixed_entries)


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
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as leaderboard_file:
        json.dump(sort_leaderboard_entries(entries), leaderboard_file, ensure_ascii=False, indent=2)


def sort_leaderboard_entries(entries):
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if is_better_score(entries[j], entries[i]):
                temp = entries[i]
                entries[i] = entries[j]
                entries[j] = temp
    return entries


def is_better_score(new_score, old_score):
    if new_score["wave_reached"] > old_score["wave_reached"]:
        return True
    if new_score["wave_reached"] < old_score["wave_reached"]:
        return False

    if new_score["time_seconds"] < old_score["time_seconds"]:
        return True
    if new_score["time_seconds"] > old_score["time_seconds"]:
        return False

    return new_score["class_name"] < old_score["class_name"]


def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds - (minutes * 60)
    return f"{minutes:02d}:{remaining_seconds:04.1f}"

#!/usr/bin/env python3
import json
import os
import random
import time
from glob import glob

# Configuration
SLEEP_SECONDS = 1       # interval between updates
DELTA_MIN = -35            # minimum change per step
DELTA_MAX = 35             # maximum change per step
MIN_VALUE = 0             # clamp lower bound (no negative values)
# MAX_VALUE = 100         # optional upper clamp; set to None to disable
MAX_VALUE = None

def update_value(v: float) -> float:
    """Return v slightly modified by a random delta and clamped."""
    delta = random.randint(DELTA_MIN, DELTA_MAX)
    new_v = v + delta
    if MIN_VALUE is not None:
        new_v = max(MIN_VALUE, new_v)
    if MAX_VALUE is not None:
        new_v = min(MAX_VALUE, new_v)
    return new_v

def process_file(path: str) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return

    if not isinstance(data, list):
        print(f"[WARN] {path} does not contain a list, skipping.")
        return

    changed = False
    for item in data:
        if not isinstance(item, dict):
            continue
        if "value" not in item:
            continue
        try:
            old_v = float(item["value"])
        except (TypeError, ValueError):
            continue

        new_v = update_value(old_v)
        if new_v != old_v:
            item["value"] = new_v
            changed = True

    if not changed:
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Updated {path}")
    except Exception as e:
        print(f"[WARN] Cannot write {path}: {e}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(base_dir, "chart*.json")

    print(f"[INFO] Watching JSON files matching: {pattern}")
    print(f"[INFO] Updating every {SLEEP_SECONDS} seconds. Press Ctrl+C to stop.")

    while True:
        files = sorted(glob(pattern))
        if not files:
            print("[WARN] No chart*.json files found.")
        for path in files:
            process_file(path)
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()


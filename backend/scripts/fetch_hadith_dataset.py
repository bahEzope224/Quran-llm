from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import urlopen


BASE_URL = "https://datasets-server.huggingface.co/rows"
DATASET = "meeAtif/hadith_datasets"
CONFIG = "default"
SPLIT = "train"
PAGE_SIZE = 100
TOTAL_ROWS = 33738
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "hadith_datasets_all_rows.json"
CHECKPOINT_PATH = Path(__file__).resolve().parents[1] / "data" / "hadith_datasets_all_rows.checkpoint.json"


def fetch_page(offset: int, length: int) -> dict:
    query = urlencode(
        {
            "dataset": DATASET,
            "config": CONFIG,
            "split": SPLIT,
            "offset": offset,
            "length": length,
        }
    )
    with urlopen(f"{BASE_URL}?{query}") as response:
        return json.loads(response.read().decode("utf-8"))


def load_checkpoint() -> list[dict]:
    if not CHECKPOINT_PATH.exists():
        return []

    payload = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    return payload.get("rows", [])


def save_checkpoint(rows: list[dict]) -> None:
    CHECKPOINT_PATH.write_text(
        json.dumps(
            {
                "dataset": DATASET,
                "config": CONFIG,
                "split": SPLIT,
                "count": len(rows),
                "rows": rows,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = load_checkpoint()
    start_offset = len(rows)
    if rows:
        print(f"Resuming from {start_offset}/{TOTAL_ROWS}")

    for offset in range(start_offset, TOTAL_ROWS, PAGE_SIZE):
        attempt = 0
        while True:
            try:
                payload = fetch_page(offset=offset, length=PAGE_SIZE)
                break
            except HTTPError as error:
                if error.code != 429:
                    raise

                attempt += 1
                wait_seconds = min(60, 2**attempt)
                print(f"HTTP 429 at offset {offset}, retrying in {wait_seconds}s")
                time.sleep(wait_seconds)

        batch = payload.get("rows", [])
        rows.extend(item.get("row", {}) for item in batch if item.get("row"))
        save_checkpoint(rows)
        print(f"Fetched {min(offset + PAGE_SIZE, TOTAL_ROWS)}/{TOTAL_ROWS}")

    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "dataset": DATASET,
                "config": CONFIG,
                "split": SPLIT,
                "count": len(rows),
                "rows": rows,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

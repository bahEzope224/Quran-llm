from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlretrieve


BASE_URL = "https://huggingface.co/datasets/meeAtif/hadith_datasets/resolve/main"
FILENAMES = [
    "Jami` at-Tirmidhi.json",
    "Sahih Muslim.json",
    "Sahih al-Bukhari.json",
    "Sunan Abi Dawud.json",
    "Sunan Ibn Majah.json",
    "Sunan an-Nasa'i.json",
]
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename in FILENAMES:
        encoded_name = quote(filename, safe="")
        url = f"{BASE_URL}/{encoded_name}?download=true"
        output_path = DATA_DIR / filename
        print(f"Downloading {filename}")
        urlretrieve(url, output_path)
        print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()

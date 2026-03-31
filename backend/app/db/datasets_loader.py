from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def list_available_datasets() -> list[str]:
    """Liste les datasets presents dans le dossier data."""
    return sorted(path.name for path in DATA_DIR.iterdir()) if DATA_DIR.exists() else []

import json
from datetime import datetime
from pathlib import Path
from threading import Lock

_LOG_PATH = Path("backend/data/conversation_logs.jsonl")
_LOG_LOCK = Lock()


def _ensure_log_path() -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def record_conversation(question: str, answer: str, sources: list[dict[str, str]], profile: dict[str, object], mode: str) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "question": question.strip(),
        "answer": answer.strip(),
        "mode": mode,
        "profile": {
            "legal_school": profile.get("legal_school"),
            "language": profile.get("language"),
            "mode": profile.get("mode"),
        },
        "sources": [
            {"type": source.get("type"), "ref": source.get("ref")}
            for source in sources
        ],
    }
    _ensure_log_path()
    with _LOG_LOCK:
        with _LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import FeedbackRequest

router = APIRouter(prefix="/admin", tags=["admin"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"

def get_all_feedbacks():
    """Recupere tous les feedbacks du fichier JSONL."""
    if not FEEDBACK_FILE.exists():
        return []
    
    feedbacks = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            feedbacks.append(json.loads(line))
    return feedbacks[::-1] # Plus recent en premier

@router.get("/stats")
async def get_stats():
    """Recupere les statistiques globales."""
    feedbacks = get_all_feedbacks()
    total = len(feedbacks)
    up = sum(1 for f in feedbacks if f.get("feedback") == "up")
    down = sum(1 for f in feedbacks if f.get("feedback") == "down")
    
    return {
        "total_feedbacks": total,
        "helpful_count": up,
        "unclear_count": down,
        "success_rate": (up / total * 100) if total > 0 else 0
    }

@router.get("/feedbacks")
async def list_feedbacks():
    """Liste detaillee des feedbacks."""
    return get_all_feedbacks()

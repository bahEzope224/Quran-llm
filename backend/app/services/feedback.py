import json
import logging
from datetime import datetime
from pathlib import Path

from app.models.schemas import FeedbackRequest
from app.core.exceptions import BaseAppException, ResourceNotFoundException

logger = logging.getLogger(__name__)

# Chemin vers le fichier de stockage (DATA_DIR defini par rapport a ce fichier)
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"


def save_feedback(payload: FeedbackRequest) -> bool:
    """Enregistre le feedback utilisateur dans un fichier JSONL."""
    try:
        # S'assurer que le dossier data existe
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Preparer les donnees enrichies
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": payload.question,
            "answer": payload.answer,
            "feedback": payload.feedback,
            "comment": payload.comment,
            "profile": payload.profile.dict() if payload.profile else None,
            "sources": [s.dict() for s in payload.sources] if payload.sources else [],
        }

        # Ecrire en mode append
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"Feedback '{payload.feedback}' enregistre pour la question: {payload.question[:50]}...")
        return True

    except Exception as e:
        raise BaseAppException(
            message="Impossible d'enregistrer votre retour d'experience.",
            location="feedback_service.save_feedback",
            details={"original_error": str(e), "file": str(FEEDBACK_FILE)}
        )

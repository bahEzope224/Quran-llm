import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import FeedbackRequest, PolicyDocument, PolicyUpdateRequest
from app.core.exceptions import ResourceNotFoundException, AuthException

from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/admin", 
    tags=["admin"],
    dependencies=[Depends(get_current_admin)]
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
BUG_FILE = DATA_DIR / "bug_log.json"
POLICY_FILE = DATA_DIR / "policies.json"

DEFAULT_POLICY_DATA = {
    "privacy_text": "Nous ne recueillons pas de données personnelles identifiables lors des conversations. Les discussions sont enregistrées de manière strictement anonyme pour améliorer la précision du modèle. Les données sont protégées dans une infrastructure conforme, avec des accès limités à l'équipe de maintenance.",
    "terms_text": "En utilisant ILM AI, vous reconnaissez que les réponses fournies ne remplacent pas un avis juridique ou religieux autorisé. Vous vous engagez à poser des questions respectueuses, à ne pas tenter d'abuser du service (spams, injections) et à signaler toute information incorrecte via la fonctionnalité de feedback. Le service est fourni tel quel sans garantie implicite de disponibilité, et vous acceptez que la responsabilité de l'équipe se limite à la correction de bugs signalés.",
}

def _load_policy_record() -> dict[str, str]:
    if POLICY_FILE.exists():
        try:
            raw = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
            return {
                "privacy_text": raw.get("privacy_text", DEFAULT_POLICY_DATA["privacy_text"]),
                "terms_text": raw.get("terms_text", DEFAULT_POLICY_DATA["terms_text"]),
                "updated_at": raw.get("updated_at"),
            }
        except json.JSONDecodeError:
            print(f"CRITICAL ERROR (Admin): Impossible de parser {POLICY_FILE}, reinitialisation des politiques.")
    record = {
        **DEFAULT_POLICY_DATA,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    _persist_policy_record(record)
    return record


def _persist_policy_record(record: dict[str, str | None]) -> None:
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    POLICY_FILE.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

def get_all_feedbacks():
    """Recupere tous les feedbacks du fichier JSONL sans risquer de crash 500."""
    if not FEEDBACK_FILE.exists():
        return []
    
    feedbacks = []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    feedbacks.append(json.loads(line))
                except json.JSONDecodeError:
                    # On ignore les lignes corrompues pour ne pas bloquer tout l'affichage
                    continue
    except Exception as e:
        print(f"CRITICAL ERROR (Admin): Impossible de lire {FEEDBACK_FILE}: {e}")
        return []
        
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

@router.get("/bugs")
async def list_bugs():
    """Recupere le journal de maintenance (Bug Log)."""
    if not BUG_FILE.exists():
        return []
    try:
        with open(BUG_FILE, "r", encoding="utf-8") as f:
            import json
            return json.load(f)
    except Exception as e:
        print(f"CRITICAL ERROR (Admin): Impossible de lire {BUG_FILE}: {e}")
        return []

@router.get("/history")
async def get_history():
    """Recupere l'historique des feedbacks par jour."""
    feedbacks = get_all_feedbacks()
    history = {}
    
    for f in feedbacks:
        date = f.get("timestamp", "").split("T")[0]
        if not date: continue
        
        if date not in history:
            history[date] = {"date": date, "up": 0, "down": 0, "total": 0}
        
        history[date]["total"] += 1
        if f.get("feedback") == "up":
            history[date]["up"] += 1
        elif f.get("feedback") == "down":
            history[date]["down"] += 1
            
    # Trier par date croissante
    return sorted(history.values(), key=lambda x: x["date"])

@router.delete("/feedback/{timestamp}")
async def delete_feedback(timestamp: str):
    """Supprime un feedback par son timestamp."""
    if not FEEDBACK_FILE.exists():
        raise ResourceNotFoundException(
            message="Le catalogue des feedbacks n'est pas encore genere.",
            location="admin_router.delete_feedback"
        )
    
    found = False
    temp_records = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("timestamp") == timestamp:
                found = True
                continue
            temp_records.append(record)
    
    if not found:
        raise ResourceNotFoundException(
            message=f"Impossible de trouver le feedback avec le timestamp {timestamp}.",
            location="admin_router.delete_feedback"
        )
        
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        for rec in temp_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    return {"status": "deleted"}


@router.get("/policies", response_model=PolicyDocument)
async def get_policies():
    return PolicyDocument(**_load_policy_record())


@router.patch("/policies", response_model=PolicyDocument)
async def update_policies(payload: PolicyUpdateRequest):
    if payload.privacy_text is None and payload.terms_text is None:
        raise HTTPException(
            status_code=400,
            detail="Au moins un champ (confidentialité ou CGU) doit être fourni.",
        )

    record = _load_policy_record()
    if payload.privacy_text is not None:
        record["privacy_text"] = payload.privacy_text.strip()
    if payload.terms_text is not None:
        record["terms_text"] = payload.terms_text.strip()

    record["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _persist_policy_record(record)
    return PolicyDocument(**record)

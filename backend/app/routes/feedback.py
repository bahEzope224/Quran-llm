from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Task
from pydantic import BaseModel
from datetime import datetime
from app.services.auth import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    dependencies=[Depends(get_current_user)]
)

class BugReport(BaseModel):
    title: str
    description: Optional[str] = None

@router.post("/bug")
async def report_bug(report: BugReport, db: Session = Depends(get_db)):
    """
    Signale un bug et le transforme directement en tâche Kanban.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Creation de la tache avec le prefixe [BUG]
    new_task = Task(
        title=f"[BUG] {report.title}",
        description=report.description,
        status="Nouvelle tâche",
        date=today,
        order=0 # Par defaut au sommet de la pile
    )
    
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"status": "success", "task_id": new_task.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la creation du ticket de bug : {str(e)}")

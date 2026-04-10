from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Feature, Task
from pydantic import BaseModel
from typing import List, Optional
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/management",
    tags=["management"],
    dependencies=[Depends(get_current_admin)]
)

# --- Schemas Pydantic ---

class FeatureBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "Moyenne"
    status: str = "À implémenter"

class FeatureCreate(FeatureBase):
    pass

class FeatureResponse(FeatureBase):
    id: str
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Nouvelle tâche"
    date: Optional[str] = None
    order: int = 0

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: str
    class Config:
        from_attributes = True

# --- Endpoints Features ---

@router.get("/features", response_model=List[FeatureResponse])
async def list_features(db: Session = Depends(get_db)):
    # Tri par priorite subjective (Haute > Moyenne > Basse)
    priority_order = {"Haute": 0, "Moyenne": 1, "Basse": 2}
    features = db.query(Feature).all()
    return sorted(features, key=lambda x: priority_order.get(x.priority, 1))

@router.post("/features", response_model=FeatureResponse)
async def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    db_feature = Feature(**feature.dict())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.patch("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(feature_id: str, feature_upd: FeatureCreate, db: Session = Depends(get_db)):
    db_feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature non trouvée")
    
    for key, value in feature_upd.dict().items():
        setattr(db_feature, key, value)
    
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.delete("/features/{feature_id}")
async def delete_feature(feature_id: str, db: Session = Depends(get_db)):
    db_feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature non trouvée")
    db.delete(db_feature)
    db.commit()
    return {"status": "deleted"}

# --- Endpoints Tasks (Kanban) ---

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.order).all()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_upd: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    for key, value in task_upd.dict().items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    db.delete(db_task)
    db.commit()
    return {"status": "deleted"}

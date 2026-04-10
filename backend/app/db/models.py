import uuid
from sqlalchemy import Column, String, DateTime, Enum, Integer
from sqlalchemy.sql import func
from .database import Base
import enum

class PriorityEnum(str, enum.Enum):
    HIGH = "Haute"
    MEDIUM = "Moyenne"
    LOW = "Basse"

class FeatureStatusEnum(str, enum.Enum):
    TO_IMPLEMENT = "À implémenter"
    IN_PROGRESS = "En cours"
    DEPLOYED = "Déployée"

class TaskStatusEnum(str, enum.Enum):
    NEW = "Nouvelle tâche"
    IN_PROGRESS = "En cours"
    DONE = "Terminée"

class Feature(Base):
    __tablename__ = "features"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, default=PriorityEnum.MEDIUM)
    status = Column(String, default=FeatureStatusEnum.TO_IMPLEMENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default=TaskStatusEnum.NEW)
    date = Column(String, nullable=True) # Date optionnelle
    order = Column(Integer, default=0) # Pour le tri dans le Kanban
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

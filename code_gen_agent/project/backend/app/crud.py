from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models, schemas

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: UUID) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.NewTask) -> models.Task:
    db_task = models.Task(description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: UUID, task_update: schemas.UpdateTask) -> Optional[models.Task]:
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        if task_update.description is not None:
            db_task.description = task_update.description
        if task_update.completed is not None:
            db_task.completed = task_update.completed
        
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: UUID) -> Optional[models.Task]:
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

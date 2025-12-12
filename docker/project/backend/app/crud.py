from sqlalchemy.orm import Session
from . import models, schemas

def get_todos(db: Session):
    return db.query(models.Todo).order_by(models.Todo.created_at.desc()).all()

def create_todo(db: Session, data: schemas.TodoCreate):
    obj = models.Todo(title=data.title)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def update_todo(db: Session, todo_id: int, data: schemas.TodoUpdate):
    obj = get_todo(db, todo_id)
    if not obj:
        return None
    if data.title is not None:
        obj.title = data.title
    if data.done is not None:
        obj.done = data.done
    db.commit()
    db.refresh(obj)
    return obj

def delete_todo(db: Session, todo_id: int):
    obj = get_todo(db, todo_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

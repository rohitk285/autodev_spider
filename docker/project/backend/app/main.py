from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from . import crud, schemas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def start():
    init_db()

@app.get("/todos", response_model=list[schemas.TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return crud.get_todos(db)

@app.post("/todos", response_model=schemas.TodoOut)
def create(data: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, data)

@app.put("/todos/{todo_id}", response_model=schemas.TodoOut)
def update(todo_id: int, data: schemas.TodoUpdate, db: Session = Depends(get_db)):
    out = crud.update_todo(db, todo_id, data)
    if not out:
        raise HTTPException(404, "Todo not found")
    return out

@app.delete("/todos/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_todo(db, todo_id)
    if not ok:
        raise HTTPException(404, "Todo not found")
    return {"status": "deleted"}

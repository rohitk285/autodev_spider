from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do Application API",
    version="1.0.0",
    description="API for managing To-Do tasks, including adding, marking as completed, deleting, and displaying tasks."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://api.todoapp.com"], # Adjust as needed for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tasks", response_model=List[schemas.Task], summary="Retrieve all tasks")
async def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        tasks = crud.get_tasks(db, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")

@app.post("/tasks", response_model=schemas.Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(task: schemas.NewTask, db: Session = Depends(get_db)):
    try:
        db_task = crud.create_task(db=db, task=task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")

@app.patch("/tasks/{id}", response_model=schemas.Task, summary="Update an existing task (e.g., mark as completed)")
async def update_task(id: UUID, task_update: schemas.UpdateTask, db: Session = Depends(get_db)):
    try:
        db_task = crud.get_task(db, task_id=id)
        if db_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID '{id}' not found.")
        
        updated_task = crud.update_task(db=db, task_id=id, task_update=task_update)
        return updated_task
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
async def delete_task(id: UUID, db: Session = Depends(get_db)):
    try:
        db_task = crud.get_task(db, task_id=id)
        if db_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID '{id}' not found.")
        
        crud.delete_task(db=db, task_id=id)
        return # 204 No Content response
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")

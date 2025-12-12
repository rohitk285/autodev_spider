import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone

# --- Mock Application Setup for Testing ---
# This section simulates the FastAPI application's core logic
# so that the TestClient has an app to interact with.
# In a real project, 'app' would be imported from your main application file.

app = FastAPI(title="To-Do Application API Mock")

# In-memory database for testing
tasks_db: Dict[uuid.UUID, Dict] = {}

# Pydantic models mirroring OpenAPI schemas
class TaskBase(BaseModel):
    description: str

class NewTask(TaskBase):
    pass

class Task(TaskBase):
    id: uuid.UUID
    completed: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UpdateTask(BaseModel):
    description: Optional[str] = None
    completed: Optional[bool] = None

# API Endpoints (simplified for testing)
@app.get("/v1/tasks", response_model=List[Task])
async def get_all_tasks():
    return list(tasks_db.values())

@app.post("/v1/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(new_task: NewTask):
    task_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    task_data = Task(
        id=task_id,
        description=new_task.description,
        completed=False,
        createdAt=now,
        updatedAt=now
    )
    tasks_db[task_id] = task_data.dict()
    return task_data

@app.patch("/v1/tasks/{task_id}", response_model=Task)
async def update_task(task_id: uuid.UUID, update_data: UpdateTask):
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    current_task = tasks_db[task_id]
    updated = False
    if update_data.description is not None:
        current_task["description"] = update_data.description
        updated = True
    if update_data.completed is not None:
        current_task["completed"] = update_data.completed
        updated = True

    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update.")

    current_task["updatedAt"] = datetime.now(timezone.utc)
    tasks_db[task_id] = current_task # Update in db
    return Task(**current_task)

@app.delete("/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: uuid.UUID):
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del tasks_db[task_id]
    return

# --- Test Client Setup ---
client = TestClient(app)

# --- Pytest Fixtures ---
@pytest.fixture(autouse=True)
def clear_tasks_db():
    """Fixture to clear the database before each test."""
    tasks_db.clear()
    yield

@pytest.fixture
def create_sample_task():
    """Fixture to create a sample task and return its ID."""
    response = client.post("/v1/tasks", json={"description": "Test task for update/delete"})
    assert response.status_code == 201
    return response.json()["id"]

# --- Test Cases ---

def test_get_all_tasks_empty():
    response = client.get("/v1/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task_success():
    task_data = {"description": "Buy groceries"}
    response = client.post("/v1/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Buy groceries"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data
    assert data["completed"] is False

def test_create_task_invalid_data():
    # Missing description
    response = client.post("/v1/tasks", json={})
    assert response.status_code == 422 # FastAPI's validation error for missing required field

def test_get_all_tasks_with_data():
    client.post("/v1/tasks", json={"description": "Task 1"})
    client.post("/v1/tasks", json={"description": "Task 2"})
    response = client.get("/v1/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["description"] == "Task 1"
    assert tasks[1]["description"] == "Task 2"

def test_update_task_description(create_sample_task):
    task_id = create_sample_task
    update_data = {"description": "Updated task description"}
    response = client.patch(f"/v1/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(task_id)
    assert data["description"] == "Updated task description"
    assert data["completed"] is False # Should remain false if not explicitly updated

def test_update_task_completed_status(create_sample_task):
    task_id = create_sample_task
    update_data = {"completed": True}
    response = client.patch(f"/v1/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(task_id)
    assert data["completed"] is True

def test_update_task_not_found():
    non_existent_id = uuid.uuid4()
    update_data = {"description": "Should not update"}
    response = client.patch(f"/v1/tasks/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_update_task_invalid_data(create_sample_task):
    task_id = create_sample_task
    # No fields provided for update
    response = client.patch(f"/v1/tasks/{task_id}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields provided for update."

def test_delete_task_success(create_sample_task):
    task_id = create_sample_task
    response = client.delete(f"/v1/tasks/{task_id}")
    assert response.status_code == 204
    # Verify it's actually deleted
    get_response = client.get("/v1/tasks")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

def test_delete_task_not_found():
    non_existent_id = uuid.uuid4()
    response = client.delete(f"/v1/tasks/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

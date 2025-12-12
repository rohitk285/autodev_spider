import pytest
from fastapi.testclient import TestClient
import os

# We will import the FastAPI app but patch the DB to use sqlite in-memory for tests

def _override_db_url_env():
    os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///:memory:'

_override_db_url_env()

from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(scope='module', autouse=True)
def setup_db():
    # Ensure tables are created for sqlite in-memory
    init_db()
    yield

def test_create_and_get_todo():
    res = client.post('/todos', json={'title': 'test item'})
    assert res.status_code == 201
    data = res.json()
    assert data['title'] == 'test item'
    tid = data['id']

    res2 = client.get('/todos')
    assert res2.status_code == 200
    todos = res2.json()
    assert any(t['id'] == tid for t in todos)

def test_update_and_delete():
    res = client.post('/todos', json={'title': 'to update'})
    assert res.status_code == 201
    tid = res.json()['id']

    resu = client.put(f'/todos/{tid}', json={'done': True})
    assert resu.status_code == 200
    assert resu.json()['done'] == True

    resdel = client.delete(f'/todos/{tid}')
    assert resdel.status_code == 204

    # ensure gone
    res_after = client.get('/todos')
    assert all(t['id'] != tid for t in res_after.json())

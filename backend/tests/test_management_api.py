from fastapi.testclient import TestClient
from app.main import app
from app.services.auth import get_current_admin
from app.db.database import get_db, SessionLocal, Base, engine
import pytest

# Mock auth
async def mock_admin():
    return {"id": "test_admin", "email": "admin@test.com"}

app.dependency_overrides[get_current_admin] = mock_admin

client = TestClient(app)

def test_features_crud():
    # Create
    response = client.post("/management/features", json={
        "title": "Test Feature",
        "description": "Desc",
        "priority": "Haute",
        "status": "À implémenter"
    })
    assert response.status_code == 200
    feature_id = response.json()["id"]
    
    # List
    response = client.get("/management/features")
    assert response.status_code == 200
    assert any(f["id"] == feature_id for f in response.json())
    
    # Delete
    response = client.delete(f"/management/features/{feature_id}")
    assert response.status_code == 200

def test_tasks_crud():
    # Create
    response = client.post("/management/tasks", json={
        "title": "Test Task",
        "description": "Desc",
        "status": "Nouvelle tâche"
    })
    assert response.status_code == 200
    task_id = response.json()["id"]
    
    # List
    response = client.get("/management/tasks")
    assert response.status_code == 200
    
    # Update
    response = client.patch(f"/management/tasks/{task_id}", json={
        "title": "Updated Task",
        "status": "En cours"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "En cours"
    
    # Delete
    response = client.delete(f"/management/tasks/{task_id}")
    assert response.status_code == 200

if __name__ == "__main__":
    test_features_crud()
    test_tasks_crud()
    print("All API tests passed!")

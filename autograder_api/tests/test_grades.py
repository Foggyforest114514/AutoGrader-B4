import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import ClassStudent, Submission

def test_get_my_grades(client, student_token):
    response = client.get(
        "/api/v1/grades/my",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_class_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/class/{test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_assignment_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/assignment/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200

def test_export_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/export/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200

def test_get_grade_statistics(client, teacher_token, test_data):
    from app.database import get_db
    
    db = next(get_db())
    
    submissions = db.query(Submission).filter(
        Submission.assignment_id == test_data["assignment"].assignment_id
    ).all()
    
    if submissions:
        response = client.get(
            f"/api/v1/grades/statistics/{test_data['assignment'].assignment_id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    db.close()
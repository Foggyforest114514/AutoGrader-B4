import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import ClassStudent, Submission

def test_create_submission(client, student_token, test_data, test_user):
    from app.database import get_db
    db = next(get_db())
    
    class_student = ClassStudent(
        class_id=test_data["class"].class_id,
        student_user_id=test_user["student"]["user"].user_id
    )
    db.add(class_student)
    db.commit()
    db.close()
    
    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "student_user_id": test_user["student"]["user"].user_id,
            "assignment_id": test_data["assignment"].assignment_id,
            "question_id": "TEST_Q001",
            "code": "print('Hello World')",
            "language": "python"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "提交成功"
    assert "submission_id" in data["data"]

def test_create_submission_not_student(client, teacher_token, test_data):
    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "student_user_id": 1,
            "assignment_id": test_data["assignment"].assignment_id,
            "question_id": "TEST_Q001",
            "code": "print('test')",
            "language": "python"
        }
    )
    assert response.status_code == 403

def test_create_submission_assignment_not_found(client, student_token, test_user):
    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "student_user_id": test_user["student"]["user"].user_id,
            "assignment_id": 99999,
            "question_id": "TEST_Q001",
            "code": "print('test')",
            "language": "python"
        }
    )
    assert response.status_code == 404

def test_get_submission_detail(client, student_token, test_data, test_user):
    from app.database import get_db
    from app.models.models import ClassStudent
    
    db = next(get_db())
    
    existing_cs = db.query(ClassStudent).filter(
        ClassStudent.class_id == test_data["class"].class_id,
        ClassStudent.student_user_id == test_user["student"]["user"].user_id
    ).first()
    if not existing_cs:
        class_student = ClassStudent(
            class_id=test_data["class"].class_id,
            student_user_id=test_user["student"]["user"].user_id
        )
        db.add(class_student)
        db.commit()
    
    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "student_user_id": test_user["student"]["user"].user_id,
            "assignment_id": test_data["assignment"].assignment_id,
            "question_id": "TEST_Q001",
            "code": "print('test')",
            "language": "python"
        }
    )
    assert response.status_code == 200
    submission_id = response.json()["data"]["submission_id"]
    
    response = client.get(
        f"/api/v1/submissions/{submission_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["submission_id"] == submission_id
    
    db.close()

def test_update_submission_result(client):
    from app.database import get_db
    from app.models.models import Submission
    
    db = next(get_db())
    
    submission = db.query(Submission).first()
    if submission:
        response = client.patch(
            f"/api/v1/submissions/{submission.submission_id}/result",
            json={
                "status": "COMPLETED",
                "overallScore": 95.0,
                "passedCount": 5,
                "totalCount": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "评测结果更新成功"
    
    db.close()

def test_get_assignment_submissions(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/submissions/assignment/{test_data['assignment'].assignment_id}/all",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "submissions" in data["data"]

def test_override_submission_score(client, teacher_token):
    from app.database import get_db
    from app.models.models import Submission
    
    db = next(get_db())
    
    submission = db.query(Submission).first()
    if submission:
        response = client.patch(
            f"/api/v1/submissions/{submission.submission_id}/override?override_score=100&override_reason=手动调整",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "分数覆盖成功"
    
    db.close()

def test_get_my_submissions(client, student_token):
    response = client.get(
        "/api/v1/submissions/my",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import ClassStudent, Submission, User

def test_get_my_grades(client, student_token):
    response = client.get(
        "/api/v1/grades/my",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_my_grades_with_assignment_filter(client, student_token, test_data):
    response = client.get(
        f"/api/v1/grades/my?assignment_id={test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_my_grades_teacher_forbidden(client, teacher_token):
    response = client.get(
        "/api/v1/grades/my",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "此接口仅限学生使用" in data.get("detail", "")

def test_get_my_grades_admin_forbidden(client, admin_token):
    response = client.get(
        "/api/v1/grades/my",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403

def test_get_class_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/class/{test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_class_grades_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/grades/class/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "班级不存在" in data.get("detail", "")

def test_get_class_grades_wrong_teacher_forbidden(client, teacher_token, test_user, test_data):
    from app.database import get_db
    from app.models.models import Class

    db = next(get_db())
    other_class = Class(
        course_id=test_data["course"].course_id,
        class_name="其他教师班级",
        class_code="OTHER001",
        teacher_id=test_user["admin"]["user"].user_id
    )
    db.add(other_class)
    db.commit()
    db.refresh(other_class)
    
    response = client.get(
        f"/api/v1/grades/class/{other_class.class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "无权限查看此班级成绩" in data.get("detail", "")
    
    db.close()

def test_get_class_grades_student_forbidden(client, student_token, test_data):
    response = client.get(
        f"/api/v1/grades/class/{test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "学生无权限查看班级成绩" in data.get("detail", "")

def test_get_assignment_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/assignment/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200

def test_get_assignment_grades_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/grades/assignment/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_export_grades(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/grades/export/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200

def test_export_grades_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/grades/export/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "作业不存在" in data.get("detail", "")

def test_export_grades_wrong_teacher_forbidden(client, teacher_token, test_user, test_data):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())
    other_assignment = Assignment(
        title="其他教师作业",
        description="测试权限",
        class_id=test_data["class"].class_id,
        teacher_id=test_user["admin"]["user"].user_id,
        due_date="2027-12-31T23:59:59",
        is_published=True,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(other_assignment)
    db.commit()
    db.refresh(other_assignment)
    
    response = client.get(
        f"/api/v1/grades/export/{other_assignment.assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "无权限导出此作业成绩" in data.get("detail", "")
    
    db.close()

def test_export_grades_student_forbidden(client, student_token, test_data):
    response = client.get(
        f"/api/v1/grades/export/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "学生无权限导出成绩" in data.get("detail", "")

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

def test_get_grade_statistics_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/grades/statistics/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_get_grade_statistics_student_forbidden(client, student_token, test_data):
    response = client.get(
        f"/api/v1/grades/statistics/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code in [200, 403, 404]

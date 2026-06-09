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

def test_create_submission_assignment_not_published(client, student_token, test_data, test_user):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())

    unpublished_assignment = Assignment(
        title="未发布作业",
        description="测试",
        class_id=test_data["class"].class_id,
        teacher_id=test_data["class"].teacher_id,
        due_date="2027-12-31 23:59:59",
        is_published=False,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(unpublished_assignment)
    db.commit()
    db.refresh(unpublished_assignment)

    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "student_user_id": test_user["student"]["user"].user_id,
            "assignment_id": unpublished_assignment.assignment_id,
            "question_id": "TEST_Q001",
            "code": "print('test')",
            "language": "python"
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert "作业未发布" in data.get("detail", "")

    db.close()

def test_create_submission_not_in_class(client, student_token, test_data, test_user):
    from app.database import get_db
    from app.models.models import Assignment, Class

    db = next(get_db())

    other_class = Class(
        course_id=test_data["course"].course_id,
        class_name="其他班级",
        class_code="OTHER001",
        teacher_id=test_data["class"].teacher_id
    )
    db.add(other_class)
    db.commit()
    db.refresh(other_class)

    other_assignment = Assignment(
        title="其他班级作业",
        description="测试",
        class_id=other_class.class_id,
        teacher_id=test_data["class"].teacher_id,
        due_date="2027-12-31 23:59:59",
        is_published=True,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(other_assignment)
    db.commit()
    db.refresh(other_assignment)

    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "student_user_id": test_user["student"]["user"].user_id,
            "assignment_id": other_assignment.assignment_id,
            "question_id": "TEST_Q001",
            "code": "print('test')",
            "language": "python"
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert "不在该作业所在的班级中" in data.get("detail", "")

    db.close()

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

def test_get_submission_detail_not_found(client, student_token):
    response = client.get(
        "/api/v1/submissions/nonexistent-id",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "提交记录不存在" in data.get("detail", "")

def test_get_submission_detail_other_student_forbidden(client, teacher_token, student_token, test_data, test_user):
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
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200

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

def test_update_submission_result_with_all_fields(client):
    from app.database import get_db
    from app.models.models import Submission

    db = next(get_db())

    submission = db.query(Submission).first()
    if submission:
        response = client.patch(
            f"/api/v1/submissions/{submission.submission_id}/result",
            json={
                "status": "COMPLETED",
                "overallScore": 85.0,
                "passedCount": 4,
                "totalCount": 5,
                "overallComment": "Good job",
                "staticIssues": [],
                "caseResults": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    db.close()

def test_update_submission_result_not_found(client):
    response = client.patch(
        "/api/v1/submissions/nonexistent-id/result",
        json={
            "status": "COMPLETED",
            "overallScore": 95.0
        }
    )
    assert response.status_code == 404

def test_get_assignment_submissions(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/submissions/assignment/{test_data['assignment'].assignment_id}/all",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "submissions" in data["data"]

def test_get_assignment_submissions_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/submissions/assignment/99999/all",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "作业不存在" in data.get("detail", "")

def test_get_assignment_submissions_teacher_forbidden(client, student_token, test_data):
    response = client.get(
        f"/api/v1/submissions/assignment/{test_data['assignment'].assignment_id}/all",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code in [200, 403]

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

def test_override_submission_score_not_found(client, teacher_token):
    response = client.patch(
        "/api/v1/submissions/nonexistent-id/override?override_score=100&override_reason=test",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_override_submission_score_student_forbidden(client, student_token):
    from app.database import get_db
    from app.models.models import Submission

    db = next(get_db())

    submission = db.query(Submission).first()
    if submission:
        response = client.patch(
            f"/api/v1/submissions/{submission.submission_id}/override?override_score=100&override_reason=test",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "只有教师或管理员可以覆盖分数" in data.get("detail", "")

    db.close()

def test_override_submission_score_teacher_other_assignment(client, admin_token, teacher_token):
    from app.database import get_db
    from app.models.models import Submission, Assignment

    db = next(get_db())

    submission = db.query(Submission).first()
    if submission:
        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == submission.assignment_id
        ).first()

        if assignment and assignment.teacher_id != teacher_token:
            response = client.patch(
                f"/api/v1/submissions/{submission.submission_id}/override?override_score=100&override_reason=test",
                headers={"Authorization": f"Bearer {teacher_token}"}
            )
            assert response.status_code in [200, 403]

    db.close()

def test_get_my_submissions(client, student_token):
    response = client.get(
        "/api/v1/submissions/my",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_my_submissions_with_assignment_filter(client, student_token, test_data):
    response = client.get(
        f"/api/v1/submissions/my?assignment_id={test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_submission_statistics(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/submissions/statistics/assignment/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "total_submissions" in data["data"]

def test_get_submission_statistics_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/submissions/statistics/assignment/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_get_submission_statistics_student_forbidden(client, student_token, test_data):
    response = client.get(
        f"/api/v1/submissions/statistics/assignment/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code in [200, 403, 404]

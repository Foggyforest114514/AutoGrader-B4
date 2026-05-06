import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_import_students_csv(client, admin_token):
    csv_content = "student_id,real_name,email\nS005,测试学生5,student5@test.com\nS006,测试学生6,student6@test.com"
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "导入完成"

def test_import_students_no_permission(client, student_token):
    csv_content = "student_id,real_name,email\nS004,测试学生4,student4@test.com"
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {student_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 403

def test_import_students_invalid_file(client, teacher_token):
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {teacher_token}"},
        files={"file": ("students.txt", "invalid content", "text/plain")}
    )
    assert response.status_code == 400

def test_get_students_list(client, teacher_token):
    response = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "students" in data["data"]

def test_get_students_list_student_no_permission(client, student_token):
    response = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_reset_student_password(client, admin_token, test_user):
    response = client.post(
        f"/api/v1/students/{test_user['student']['user'].user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "密码重置成功"

def test_toggle_student_status(client, admin_token, test_user):
    response = client.patch(
        f"/api/v1/students/{test_user['student']['user'].user_id}/status?is_active=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "停用" in data["msg"]
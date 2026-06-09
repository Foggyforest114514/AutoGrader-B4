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

def test_import_students_with_class_id(client, admin_token, test_data):
    csv_content = "student_id,real_name,email\nS007,测试学生7,student7@test.com"
    response = client.post(
        f"/api/v1/students/import?class_id={test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_import_students_csv_missing_fields(client, admin_token):
    csv_content = "student_id,real_name\nS008,测试学生8"
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["fail_count"] > 0

def test_import_students_csv_duplicate_student_id(client, admin_token, test_user):
    csv_content = f"student_id,real_name,email\n{test_user['student']['user'].username},重复学号,duplicate@test.com"
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["fail_count"] > 0

def test_import_students_teacher_role(client, teacher_token, test_data):
    csv_content = "student_id,real_name,email\nS009,测试学生9,student9@test.com"
    response = client.post(
        f"/api/v1/students/import?class_id={test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200

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

def test_import_students_excel_not_supported(client, teacher_token):
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {teacher_token}"},
        files={"file": ("students.xlsx", "fake excel content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Excel文件暂未支持" in str(data["data"]["fail_reasons"])

def test_import_students_invalid_encoding(client, teacher_token):
    response = client.post(
        "/api/v1/students/import",
        headers={"Authorization": f"Bearer {teacher_token}"},
        files={"file": ("students.csv", "学生,测试".encode("gbk"), "text/csv")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "文件编码错误" in data.get("detail", "")

def test_get_students_list(client, teacher_token):
    response = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "students" in data["data"]

def test_get_students_list_with_class_filter(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/students?class_id={test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_students_list_with_keyword(client, teacher_token):
    response = client.get(
        "/api/v1/students?keyword=test",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_students_list_pagination(client, teacher_token):
    response = client.get(
        "/api/v1/students?page=1&size=10",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["page"] == 1
    assert data["data"]["size"] == 10

def test_get_students_list_admin(client, admin_token):
    response = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {admin_token}"}
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

def test_reset_student_password_custom(client, admin_token, test_user):
    response = client.post(
        f"/api/v1/students/{test_user['student']['user'].user_id}/reset-password?new_password=custom123",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["new_password"] == "custom123"

def test_reset_student_password_not_found(client, admin_token):
    response = client.post(
        "/api/v1/students/99999/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "学生不存在" in data.get("detail", "")

def test_reset_student_password_teacher_allowed(client, teacher_token, test_user):
    response = client.post(
        f"/api/v1/students/{test_user['student']['user'].user_id}/reset-password",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200

def test_reset_student_password_student_forbidden(client, student_token, test_user):
    response = client.post(
        f"/api/v1/students/{test_user['student']['user'].user_id}/reset-password",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_toggle_student_status_disable(client, admin_token, test_user):
    response = client.patch(
        f"/api/v1/students/{test_user['student']['user'].user_id}/status?is_active=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "停用" in data["msg"]

def test_toggle_student_status_enable(client, admin_token, test_user):
    response = client.patch(
        f"/api/v1/students/{test_user['student']['user'].user_id}/status?is_active=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "启用" in data["msg"]

def test_toggle_student_status_not_found(client, admin_token):
    response = client.patch(
        "/api/v1/students/99999/status?is_active=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "学生不存在" in data.get("detail", "")

def test_toggle_student_status_teacher_forbidden(client, teacher_token, test_user):
    response = client.patch(
        f"/api/v1/students/{test_user['student']['user'].user_id}/status?is_active=false",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
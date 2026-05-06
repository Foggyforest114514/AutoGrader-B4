import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_classes_list_teacher(client, teacher_token, test_data):
    response = client.get(
        "/api/v1/classes",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_classes_list_student(client, student_token):
    response = client.get(
        "/api/v1/classes",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_classes_list_filtered(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/classes?course_id={test_data['course'].course_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_create_class_teacher(client, teacher_token, test_data):
    response = client.post(
        "/api/v1/classes",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "courseId": test_data["course"].course_id,
            "className": "新班级",
            "classCode": "NEW001"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "班级创建成功"
    assert "class_id" in data["data"]

def test_create_class_student(client, student_token, test_data):
    response = client.post(
        "/api/v1/classes",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "courseId": test_data["course"].course_id,
            "className": "学生班级",
            "classCode": "STU001"
        }
    )
    assert response.status_code == 403

def test_create_class_invalid_course(client, teacher_token):
    response = client.post(
        "/api/v1/classes",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "courseId": 99999,
            "className": "无效课程",
            "classCode": "INVALID"
        }
    )
    assert response.status_code == 404

def test_get_class_students(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/classes/{test_data['class'].class_id}/students",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_class_students_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/classes/99999/students",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_add_student_to_class(client, teacher_token, test_data, test_user):
    response = client.post(
        f"/api/v1/classes/{test_data['class'].class_id}/students",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"studentUserId": test_user["student"]["user"].user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "学生添加成功"

def test_add_student_already_in_class(client, teacher_token, test_data, test_user):
    response = client.post(
        f"/api/v1/classes/{test_data['class'].class_id}/students",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"studentUserId": test_user["student"]["user"].user_id}
    )
    assert response.status_code == 400 or response.status_code == 200

def test_add_student_no_permission(client, student_token, test_data, test_user):
    response = client.post(
        f"/api/v1/classes/{test_data['class'].class_id}/students",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"studentUserId": test_user["student"]["user"].user_id}
    )
    assert response.status_code == 403

def test_remove_student_from_class(client, teacher_token, test_data, test_user):
    response = client.delete(
        f"/api/v1/classes/{test_data['class'].class_id}/students/{test_user['student']['user'].user_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "学生移除成功"

def test_remove_student_not_found(client, teacher_token, test_data):
    response = client.delete(
        f"/api/v1/classes/{test_data['class'].class_id}/students/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_import_students_to_class(client, teacher_token, test_data):
    csv_content = "student_id,real_name,email\nS007,测试学生7,student7@test.com"
    response = client.post(
        f"/api/v1/classes/{test_data['class'].class_id}/students/import",
        headers={"Authorization": f"Bearer {teacher_token}"},
        files={"file": ("students.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "导入完成"
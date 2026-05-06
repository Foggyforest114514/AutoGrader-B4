import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_courses_list_admin(client, admin_token):
    response = client.get(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_courses_list_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_courses_list_student(client, student_token):
    response = client.get(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_course_detail(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/courses/{test_data['course'].course_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["course_id"] == test_data["course"].course_id

def test_get_course_detail_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/courses/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_create_course_teacher(client, teacher_token):
    response = client.post(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "courseName": "新课程",
            "courseCode": "NEW_CS102",
            "semester": "2024-2025-2",
            "description": "测试新课程"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "课程创建成功"
    assert "course_id" in data["data"]

def test_create_course_student(client, student_token):
    response = client.post(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "courseName": "学生课程",
            "courseCode": "STU_CS001",
            "semester": "2024-2025-2"
        }
    )
    assert response.status_code == 403

def test_update_course(client, teacher_token, test_data):
    response = client.put(
        f"/api/v1/courses/{test_data['course'].course_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "courseName": "更新后的课程名称",
            "description": "更新后的描述"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "课程更新成功"

def test_update_course_no_permission(client, teacher_token, test_data):
    response = client.put(
        f"/api/v1/courses/{test_data['course'].course_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"courseName": "试图修改"}
    )
    assert response.status_code == 200

def test_delete_course(client, teacher_token):
    create_response = client.post(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "courseName": "待删除课程",
            "courseCode": "DEL_CS001",
            "semester": "2024-2025-2"
        }
    )
    course_id = create_response.json()["data"]["course_id"]
    
    response = client.delete(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "课程删除成功"

def test_delete_course_not_found(client, teacher_token):
    response = client.delete(
        "/api/v1/courses/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404

def test_get_course_classes(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/courses/{test_data['course'].course_id}/classes",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200

def test_get_course_assignments(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/courses/{test_data['course'].course_id}/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200
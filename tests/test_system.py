import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_system_stats(client, admin_token):
    response = client.get(
        "/api/v1/system/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "total_users" in data["data"]
    assert "total_students" in data["data"]
    assert "total_courses" in data["data"]
    assert "total_submissions" in data["data"]

def test_get_system_stats_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/system/stats",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_system_stats_student(client, student_token):
    response = client.get(
        "/api/v1/system/stats",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_database_health(client, admin_token):
    response = client.get(
        "/api/v1/system/health",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "status" in data["data"]

def test_get_database_health_no_permission(client, teacher_token):
    response = client.get(
        "/api/v1/system/health",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403

def test_get_announcements(client, admin_token):
    response = client.get(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "announcements" in data["data"]

def test_get_announcements_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_announcements_student(client, student_token):
    response = client.get(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_create_announcement_admin(client, admin_token):
    response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "系统公告测试",
            "content": "这是一条测试公告",
            "course_id": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "公告发布成功"
    assert "announcement_id" in data["data"]
    return data["data"]["announcement_id"]

def test_create_announcement_teacher(client, teacher_token, test_data):
    response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "课程公告测试",
            "content": "这是一条课程测试公告",
            "course_id": test_data["course"].course_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "公告发布成功"
    return data["data"]["announcement_id"]

def test_create_announcement_student(client, student_token):
    response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "学生公告测试",
            "content": "学生不能发布公告"
        }
    )
    assert response.status_code == 403

def test_update_announcement(client, admin_token):
    create_response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "待更新公告",
            "content": "原始内容"
        }
    )
    announcement_id = create_response.json()["data"]["announcement_id"]
    
    response = client.put(
        f"/api/v1/system/announcements/{announcement_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "已更新公告",
            "content": "更新后的内容"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "公告更新成功"

def test_update_announcement_no_permission(client, teacher_token, admin_token):
    create_response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "管理员公告",
            "content": "管理员发布的公告"
        }
    )
    announcement_id = create_response.json()["data"]["announcement_id"]
    
    response = client.put(
        f"/api/v1/system/announcements/{announcement_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "试图修改",
            "content": "教师试图修改管理员公告"
        }
    )
    assert response.status_code == 403

def test_delete_announcement(client, admin_token):
    create_response = client.post(
        "/api/v1/system/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "待删除公告",
            "content": "这条公告将被删除"
        }
    )
    announcement_id = create_response.json()["data"]["announcement_id"]
    
    response = client.delete(
        f"/api/v1/system/announcements/{announcement_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "公告删除成功"

def test_delete_announcement_not_found(client, admin_token):
    response = client.delete(
        "/api/v1/system/announcements/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_get_system_logs(client, admin_token):
    response = client.get(
        "/api/v1/system/logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "logs" in data["data"]

def test_get_system_logs_no_permission(client, teacher_token):
    response = client.get(
        "/api/v1/system/logs",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
def test_create_assignment(client, teacher_token, test_data):
    response = client.post(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "第二次作业",
            "description": "测试作业",
            "classId": test_data["class"].class_id,
            "question_id": "TEST_Q001",
            "dueDate": "2024-12-31T23:59:59",
            "isPublished": False,
            "allowResubmit": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "作业创建成功"
    assert "assignment_id" in data["data"]

def test_get_assignments_list(client, teacher_token):
    response = client.get(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_assignment_detail(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/assignments/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_update_assignment(client, teacher_token, test_data):
    response = client.put(
        f"/api/v1/assignments/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "第一次作业-修改版"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "作业更新成功"
def test_get_current_user(client, admin_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "test_admin"
    assert data["data"]["role"] == "admin"

def test_get_current_user_student(client, student_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "test_student"
    assert data["data"]["role"] == "student"

def test_get_current_user_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "test_teacher"
    assert data["data"]["role"] == "teacher"

def test_update_user_info(client, admin_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": "newadmin@test.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "用户信息更新成功"

def test_update_user_email_duplicate(client, admin_token, test_user):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": test_user["teacher"]["user"].email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "邮箱已被使用" in data.get("detail", "")

def test_update_user_phone(client, admin_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"phone": "13800138000"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_update_user_avatar(client, admin_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"avatar": "https://example.com/avatar.jpg"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_update_user_password_success(client, admin_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "old_password": "admin123",
            "new_password": "newadmin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "用户信息更新成功"

def test_update_user_password_wrong_old(client, admin_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "old_password": "wrongpassword",
            "new_password": "newadmin123"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "旧密码错误" in data.get("detail", "")

def test_get_users_list_admin(client, admin_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "users" in data["data"]
    assert isinstance(data["data"]["users"], list)

def test_get_users_list_filter_by_role(client, admin_token):
    response = client.get(
        "/api/v1/users?role=student",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    for user in data["data"]["users"]:
        assert user["role"] == "student"

def test_get_users_list_pagination(client, admin_token):
    response = client.get(
        "/api/v1/users?page=1&size=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["page"] == 1
    assert data["data"]["size"] == 5

def test_get_users_list_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403

def test_create_teacher_success(client, admin_token):
    import uuid
    teacher_id = f"T{str(uuid.uuid4())[:8]}"
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "teacher_id": teacher_id,
            "email": f"{teacher_id}@test.com",
            "real_name": "新教师",
            "department": "计算机系",
            "initial_password": "teacher123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "教师账号创建成功"
    assert "user_id" in data["data"]

def test_create_teacher_duplicate_username(client, admin_token, test_user):
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "teacher_id": test_user["teacher"]["user"].username,
            "email": "newteacher@test.com",
            "real_name": "重复用户名教师",
            "department": "计算机系",
            "initial_password": "teacher123"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "用户名或邮箱已存在" in data.get("detail", "")

def test_create_teacher_duplicate_email(client, admin_token, test_user):
    import uuid
    teacher_id = f"T{str(uuid.uuid4())[:8]}"
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "teacher_id": teacher_id,
            "email": test_user["teacher"]["user"].email,
            "real_name": "重复邮箱教师",
            "department": "计算机系",
            "initial_password": "teacher123"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "用户名或邮箱已存在" in data.get("detail", "")

def test_create_teacher_teacher_forbidden(client, teacher_token):
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "teacher_id": "T999",
            "email": "newteacher@test.com",
            "real_name": "新教师",
            "department": "计算机系",
            "initial_password": "teacher123"
        }
    )
    assert response.status_code == 403

def test_deactivate_user_success(client, admin_token, test_user):
    response = client.post(
        f"/api/v1/users/{test_user['student']['user'].user_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "账号已停用"

def test_deactivate_user_not_found(client, admin_token):
    response = client.post(
        "/api/v1/users/99999/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "用户不存在" in data.get("detail", "")

def test_deactivate_user_teacher_forbidden(client, teacher_token, test_user):
    response = client.post(
        f"/api/v1/users/{test_user['student']['user'].user_id}/deactivate",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
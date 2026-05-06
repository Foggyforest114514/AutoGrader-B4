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

def test_get_users_list_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
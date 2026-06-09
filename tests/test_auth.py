def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "登录成功"
    assert "token" in data["data"]
    assert "refreshToken" in data["data"]
    assert data["data"]["role"] == "admin"

def test_login_failure_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "用户名或密码错误" in data.get("detail", "")

def test_login_failure_inactive_user(client, test_user):
    from app.database import get_db
    db = next(get_db())
    user = db.query(test_user["admin"]["user"].__class__).filter(
        test_user["admin"]["user"].__class__.username == "test_admin"
    ).first()
    user.is_active = False
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    assert response.status_code == 403
    
    user.is_active = True
    db.commit()
    db.close()

def test_logout_success(client, admin_token):
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "登出成功"

def test_refresh_token(client, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    refresh_token = login_response.json()["data"]["refreshToken"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refreshToken": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    assert "refreshToken" in data["data"]

def test_refresh_token_invalid(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refreshToken": "invalid_token"}
    )
    assert response.status_code == 401
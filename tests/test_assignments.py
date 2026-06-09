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

def test_create_assignment_with_publish(client, teacher_token, test_data):
    response = client.post(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "直接发布的作业",
            "description": "创建即发布",
            "classId": test_data["class"].class_id,
            "question_id": "TEST_Q001",
            "dueDate": "2024-12-31T23:59:59",
            "isPublished": True,
            "allowResubmit": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_create_assignment_student_forbidden(client, student_token, test_data):
    response = client.post(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "学生创建作业",
            "description": "测试权限",
            "classId": test_data["class"].class_id,
            "question_id": "TEST_Q001",
            "dueDate": "2024-12-31T23:59:59",
            "isPublished": False,
            "allowResubmit": True
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert "只有教师可以创建作业" in data.get("detail", "")

def test_create_assignment_wrong_class(client, teacher_token, test_user, test_data):
    from app.database import get_db
    from app.models.models import Class

    db = next(get_db())
    other_class = Class(
        course_id=test_data["course"].course_id,
        class_name="其他教师班级",
        class_code="OTHER999",
        teacher_id=test_user["admin"]["user"].user_id
    )
    db.add(other_class)
    db.commit()
    db.refresh(other_class)
    
    response = client.post(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "越权创建作业",
            "description": "在非自己班级",
            "classId": other_class.class_id,
            "question_id": "TEST_Q001",
            "dueDate": "2024-12-31T23:59:59",
            "isPublished": False,
            "allowResubmit": True
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert "只能在自己的班级下创建作业" in data.get("detail", "")
    
    db.close()

def test_create_assignment_class_not_found(client, teacher_token):
    response = client.post(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "不存在班级作业",
            "description": "测试",
            "classId": 99999,
            "question_id": "TEST_Q001",
            "dueDate": "2024-12-31T23:59:59",
            "isPublished": False,
            "allowResubmit": True
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "班级不存在" in data.get("detail", "")

def test_get_assignments_list(client, teacher_token):
    response = client.get(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_assignments_list_with_class_filter(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/assignments?class_id={test_data['class'].class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_assignments_list_student(client, student_token, test_data, test_user):
    from app.database import get_db
    from app.models.models import ClassStudent

    db = next(get_db())
    class_student = ClassStudent(
        class_id=test_data["class"].class_id,
        student_user_id=test_user["student"]["user"].user_id
    )
    db.add(class_student)
    db.commit()
    
    response = client.get(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    db.close()

def test_get_assignment_detail(client, teacher_token, test_data):
    response = client.get(
        f"/api/v1/assignments/{test_data['assignment'].assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_assignment_detail_not_found(client, teacher_token):
    response = client.get(
        "/api/v1/assignments/99999",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "作业不存在" in data.get("detail", "")

def test_get_assignment_detail_student_unpublished(client, student_token, test_data):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())
    unpublished = Assignment(
        title="未发布作业",
        description="学生看不了",
        class_id=test_data["class"].class_id,
        teacher_id=test_data["class"].teacher_id,
        due_date="2027-12-31T23:59:59",
        is_published=False,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(unpublished)
    db.commit()
    db.refresh(unpublished)
    
    response = client.get(
        f"/api/v1/assignments/{unpublished.assignment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "作业未发布" in data.get("detail", "")
    
    db.close()

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

def test_update_assignment_not_found(client, teacher_token):
    response = client.put(
        "/api/v1/assignments/99999",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "不存在的作业"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "作业不存在" in data.get("detail", "")

def test_update_assignment_other_teacher_forbidden(client, teacher_token, test_user, test_data):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())
    other_teacher = Assignment(
        title="其他教师的作业",
        description="测试权限",
        class_id=test_data["class"].class_id,
        teacher_id=test_user["admin"]["user"].user_id,
        due_date="2027-12-31T23:59:59",
        is_published=False,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(other_teacher)
    db.commit()
    db.refresh(other_teacher)
    
    response = client.put(
        f"/api/v1/assignments/{other_teacher.assignment_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "越权修改"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "无权限修改此作业" in data.get("detail", "")
    
    db.close()

def test_publish_assignment(client, teacher_token, test_data):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())
    unpublished = Assignment(
        title="待发布作业",
        description="测试发布",
        class_id=test_data["class"].class_id,
        teacher_id=test_data["class"].teacher_id,
        due_date="2027-12-31T23:59:59",
        is_published=False,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(unpublished)
    db.commit()
    db.refresh(unpublished)
    
    response = client.post(
        f"/api/v1/assignments/{unpublished.assignment_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "作业发布成功"
    
    db.close()

def test_publish_assignment_already_published(client, teacher_token, test_data):
    response = client.post(
        f"/api/v1/assignments/{test_data['assignment'].assignment_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "作业已发布" in data.get("detail", "")

def test_publish_assignment_not_found(client, teacher_token):
    response = client.post(
        "/api/v1/assignments/99999/publish",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "作业不存在" in data.get("detail", "")

def test_publish_assignment_other_teacher_forbidden(client, teacher_token, test_user, test_data):
    from app.database import get_db
    from app.models.models import Assignment

    db = next(get_db())
    other_teacher = Assignment(
        title="其他教师的作业",
        description="测试权限",
        class_id=test_data["class"].class_id,
        teacher_id=test_user["admin"]["user"].user_id,
        due_date="2027-12-31T23:59:59",
        is_published=False,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(other_teacher)
    db.commit()
    db.refresh(other_teacher)
    
    response = client.post(
        f"/api/v1/assignments/{other_teacher.assignment_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert "无权限发布此作业" in data.get("detail", "")
    
    db.close()

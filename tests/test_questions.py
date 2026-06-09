import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_questions_list(client, admin_token):
    response = client.get(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_get_questions_list_filtered(client, admin_token):
    response = client.get(
        "/api/v1/questions?type=COMMAND_LINE&difficulty=EASY&language=python",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_questions_list_teacher(client, teacher_token):
    response = client.get(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_get_questions_list_student(client, student_token):
    response = client.get(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

def test_create_question_admin(client, admin_token):
    response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "测试题目",
            "description": "这是一道测试题",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": [
                {
                    "input": "1 2",
                    "expected_output": "3",
                    "is_public": True,
                    "score_weight": 50
                },
                {
                    "input": "3 4",
                    "expected_output": "7",
                    "is_public": False,
                    "score_weight": 50
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "题目创建成功"
    assert "question_id" in data["data"]
    return data["data"]["question_id"]

def test_create_question_teacher(client, teacher_token):
    response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "教师创建题目",
            "description": "教师创建的测试题",
            "type": "COMMAND_LINE",
            "difficulty": "MEDIUM",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": [
                {
                    "input": "test",
                    "expected_output": "result",
                    "is_public": True,
                    "score_weight": 100
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    return data["data"]["question_id"]

def test_create_question_student(client, student_token):
    response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "学生题目",
            "description": "学生不能创建题目",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": []
        }
    )
    assert response.status_code == 403

def test_get_question_detail(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "详情测试题",
            "description": "测试详情",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "solution_code": "print('solution')",
            "test_cases": [
                {
                    "input": "input",
                    "expected_output": "output",
                    "is_public": True,
                    "score_weight": 100
                }
            ]
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.get(
        f"/api/v1/questions/{question_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["question_id"] == question_id
    assert "test_cases" in data["data"]

def test_get_question_detail_with_solution(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "带解答题目",
            "description": "有解答的题目",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "solution_code": "print('answer')",
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.get(
        f"/api/v1/questions/{question_id}?include_solution=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "solution_code" in data["data"]

def test_get_question_detail_student_no_solution(client, student_token, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "学生查看",
            "description": "学生无法看到解答",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "solution_code": "secret",
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.get(
        f"/api/v1/questions/{question_id}?include_solution=true",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "solution_code" not in data["data"]

def test_update_question(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "待更新题目",
            "description": "原始描述",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.put(
        f"/api/v1/questions/{question_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "已更新题目",
            "description": "更新后的描述",
            "time_limit": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "题目更新成功"

def test_update_question_no_permission(client, teacher_token, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "管理员题目",
            "description": "管理员创建",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.put(
        f"/api/v1/questions/{question_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "试图修改"}
    )
    assert response.status_code == 403

def test_delete_question(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "待删除题目",
            "description": "将被禁用",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.delete(
        f"/api/v1/questions/{question_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "题目已禁用"

def test_add_test_cases(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "添加测试用例题目",
            "description": "用于测试用例",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": []
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.post(
        f"/api/v1/questions/{question_id}/testcases",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=[
            {
                "input": "1",
                "expected_output": "1",
                "is_public": True,
                "score_weight": 50
            },
            {
                "input": "2",
                "expected_output": "4",
                "is_public": False,
                "score_weight": 50
            }
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "测试用例添加成功"

def test_get_question_test_cases(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "获取测试用例题目",
            "description": "获取测试用例",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": [
                {
                    "input": "input1",
                    "expected_output": "output1",
                    "is_public": True,
                    "score_weight": 50
                }
            ]
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    response = client.get(
        f"/api/v1/questions/{question_id}/testcases",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)

def test_delete_test_case(client, admin_token):
    create_response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "删除测试用例题目",
            "description": "删除测试用例",
            "type": "COMMAND_LINE",
            "difficulty": "EASY",
            "language": "python",
            "time_limit": 5,
            "memory_limit": 256,
            "test_cases": [
                {
                    "input": "to delete",
                    "expected_output": "delete me",
                    "is_public": True,
                    "score_weight": 100
                }
            ]
        }
    )
    question_id = create_response.json()["data"]["question_id"]
    
    get_response = client.get(
        f"/api/v1/questions/{question_id}/testcases",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    test_case_id = get_response.json()["data"][0]["test_case_id"]
    
    response = client.delete(
        f"/api/v1/questions/{question_id}/testcases/{test_case_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "测试用例删除成功"
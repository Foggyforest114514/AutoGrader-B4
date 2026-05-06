import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.models import User, Student, Teacher, Course, Class, Assignment, Question, ClassStudent, Submission
from app.auth import get_password_hash, verify_password
import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "mysql+pymysql://ag_dev:U2FuqkCFmVpjDBEN@mysql7.sqlpub.com:3312/autograder")

engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user():
    db = TestingSessionLocal()

    existing_admin = db.query(User).filter(User.username == "test_admin").first()
    if existing_admin:
        db.delete(existing_admin)
        db.commit()

    existing_teacher = db.query(User).filter(User.username == "test_teacher").first()
    if existing_teacher:
        db.delete(existing_teacher)
        db.commit()

    existing_student = db.query(User).filter(User.username == "test_student").first()
    if existing_student:
        db.delete(existing_student)
        db.commit()

    admin_user = User(
        username="test_admin",
        password_hash=get_password_hash("admin123"),
        email="admin@test.com",
        real_name="测试管理员",
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    db.flush()

    teacher_user = User(
        username="test_teacher",
        password_hash=get_password_hash("teacher123"),
        email="teacher@test.com",
        real_name="测试老师",
        role="teacher",
        is_active=True
    )
    db.add(teacher_user)
    db.flush()

    student_user = User(
        username="test_student",
        password_hash=get_password_hash("student123"),
        email="student@test.com",
        real_name="测试学生",
        role="student",
        is_active=True
    )
    db.add(student_user)
    db.flush()

    existing_teacher_profile = db.query(Teacher).filter(Teacher.user_id == teacher_user.user_id).first()
    if not existing_teacher_profile:
        teacher = Teacher(user_id=teacher_user.user_id, teacher_id="T001", department="计算机系")
        db.add(teacher)

    existing_student_profile = db.query(Student).filter(Student.user_id == student_user.user_id).first()
    if not existing_student_profile:
        student = Student(user_id=student_user.user_id, student_id="S001")
        db.add(student)

    db.commit()

    yield {
        "admin": {"user": admin_user, "password": "admin123"},
        "teacher": {"user": teacher_user, "password": "teacher123"},
        "student": {"user": student_user, "password": "student123"}
    }

    db.query(Teacher).filter(Teacher.user_id == teacher_user.user_id).delete()
    db.query(Student).filter(Student.user_id == student_user.user_id).delete()
    db.query(ClassStudent).filter(ClassStudent.student_user_id.in_([admin_user.user_id, teacher_user.user_id, student_user.user_id])).delete()
    db.query(Submission).filter(Submission.student_user_id.in_([admin_user.user_id, teacher_user.user_id, student_user.user_id])).delete()
    db.query(Assignment).filter(Assignment.teacher_id.in_([admin_user.user_id, teacher_user.user_id])).delete()
    db.query(Class).filter(Class.teacher_id.in_([admin_user.user_id, teacher_user.user_id])).delete()
    db.query(Course).filter(Course.teacher_id.in_([admin_user.user_id, teacher_user.user_id])).delete()
    db.query(User).filter(User.user_id.in_([admin_user.user_id, teacher_user.user_id, student_user.user_id])).delete()
    db.commit()

    db.close()

@pytest.fixture(scope="module")
def test_data(test_user):
    db = TestingSessionLocal()

    course = Course(
        course_code="TEST_CS101",
        course_name="测试Python编程基础",
        teacher_id=test_user["teacher"]["user"].user_id,
        semester="2024-2025-1",
        description="测试课程"
    )
    db.add(course)
    db.flush()

    class_info = Class(
        course_id=course.course_id,
        class_name="测试计科2401班",
        class_code="TEST_C2401",
        teacher_id=test_user["teacher"]["user"].user_id
    )
    db.add(class_info)
    db.flush()

    existing_question = db.query(Question).filter(Question.question_id == "TEST_Q001").first()
    if not existing_question:
        question = Question(
            question_id="TEST_Q001",
            title="测试Hello World",
            description="输出Hello World",
            type="COMMAND_LINE",
            difficulty="EASY",
            language="python",
            time_limit=5,
            memory_limit=256,
            is_active=True,
            created_by=test_user["admin"]["user"].user_id
        )
        db.add(question)
    else:
        question = existing_question
    db.flush()

    assignment = Assignment(
        title="测试第一次作业",
        description="完成Hello World程序",
        class_id=class_info.class_id,
        teacher_id=test_user["teacher"]["user"].user_id,
        due_date="2027-12-31 23:59:59",
        is_published=True,
        allow_resubmit=True,
        question_id="TEST_Q001"
    )
    db.add(assignment)
    db.commit()

    yield {
        "course": course,
        "class": class_info,
        "question": question,
        "assignment": assignment
    }

    db.close()

@pytest.fixture(scope="module")
def admin_token(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    return response.json()["data"]["token"]

@pytest.fixture(scope="module")
def teacher_token(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_teacher", "password": "teacher123"}
    )
    return response.json()["data"]["token"]

@pytest.fixture(scope="module")
def student_token(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_student", "password": "student123"}
    )
    return response.json()["data"]["token"]
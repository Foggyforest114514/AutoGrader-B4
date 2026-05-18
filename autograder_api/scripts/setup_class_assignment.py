import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/autograder")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

from app.models.models import User, Course, Class, ClassStudent, Assignment, Question, Student

db = SessionLocal()

try:
    print("=" * 60)
    print("开始执行：在课程181下创建班级、添加学生、创建作业")
    print("=" * 60)

    # 1. 查询课程信息
    course = db.query(Course).filter(Course.course_id == 181).first()
    if not course:
        print("错误：course_id=181 的课程不存在！")
        sys.exit(1)
    print(f"\n[课程] ID={course.course_id}, 名称={course.course_name}, 教师ID={course.teacher_id}, 学期={course.semester}")

    teacher_id = course.teacher_id

    # 2. 创建班级
    class_code = "TEST01"
    class_name = "测试班级01"

    existing_class = db.query(Class).filter(
        Class.course_id == 181,
        Class.class_code == class_code
    ).first()

    if existing_class:
        print(f"\n[班级] 已存在: ID={existing_class.class_id}, 名称={existing_class.class_name}")
        new_class = existing_class
    else:
        new_class = Class(
            course_id=181,
            class_name=class_name,
            class_code=class_code,
            teacher_id=teacher_id
        )
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        print(f"\n[班级] 创建成功: ID={new_class.class_id}, 名称={new_class.class_name}, 课序号={new_class.class_code}")

    class_id = new_class.class_id

    # 3. 将 user_id=661 的学生加入班级
    student_user = db.query(User).filter(User.user_id == 661).first()
    if not student_user:
        print("\n警告：user_id=661 的用户不存在，跳过添加学生")
    else:
        print(f"\n[学生] 用户信息: ID={student_user.user_id}, 用户名={student_user.username}, 角色={student_user.role.value}, 姓名={student_user.real_name}")

        existing_membership = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_user_id == 661
        ).first()

        if existing_membership:
            print(f"  该学生已在此班级中，跳过添加")
        else:
            new_membership = ClassStudent(
                class_id=class_id,
                student_user_id=661
            )
            db.add(new_membership)
            db.commit()
            print(f"  已成功添加到班级 class_id={class_id}")

    # 4. 从数据库选择一个题目
    question = db.query(Question).filter(Question.is_active == True).first()
    if not question:
        print("\n错误：数据库中没有可用的题目！")
    else:
        print(f"\n[题目] ID={question.question_id}, 标题={question.title}, 类型={question.type.value}, 难度={question.difficulty.value}, 语言={question.language}")

        # 5. 创建作业
        existing_assignment = db.query(Assignment).filter(
            Assignment.class_id == class_id,
            Assignment.question_id == question.question_id
        ).first()

        if existing_assignment:
            print(f"\n[作业] 已存在: ID={existing_assignment.assignment_id}, 标题={existing_assignment.title}")
        else:
            due_date = datetime.utcnow() + timedelta(days=14)
            new_assignment = Assignment(
                title=f"{question.title} - 作业",
                description=f"课程: {course.course_name}, 班级: {class_name}\n题目: {question.title}\n{question.description or ''}",
                class_id=class_id,
                teacher_id=teacher_id,
                due_date=due_date,
                is_published=True,
                allow_resubmit=True,
                question_id=question.question_id,
                published_at=datetime.utcnow()
            )
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)
            print(f"\n[作业] 创建成功!")
            print(f"  作业ID: {new_assignment.assignment_id}")
            print(f"  标题: {new_assignment.title}")
            print(f"  题目ID: {new_assignment.question_id}")
            print(f"  截止日期: {new_assignment.due_date}")
            print(f"  已发布: {new_assignment.is_published}")

    print("\n" + "=" * 60)
    print("执行完成！")
    print("=" * 60)

finally:
    db.close()

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import csv
import io
from app.database import get_db
from app.models.models import User, Course, Class, ClassStudent, Student
from app.schemas import ResponseModel
from app.auth import get_current_user, require_role, get_password_hash

router = APIRouter(prefix="/api/v1/students", tags=["学生管理"])

@router.post("/import", response_model=ResponseModel)
async def import_students(
    file: UploadFile = File(...),
    class_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师或管理员可以导入学生"
        )

    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV或Excel文件"
        )

    content = await file.read()

    success_count = 0
    fail_count = 0
    fail_reasons = []
    imported_students = []

    try:
        if file.filename.endswith('.csv'):
            decoded_content = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_content))

            for row_num, row in enumerate(reader, start=2):
                try:
                    student_id = row.get('student_id', '').strip()
                    real_name = row.get('real_name', '').strip()
                    email = row.get('email', '').strip()
                    initial_password = row.get('password', student_id + '123456').strip()

                    if not student_id or not real_name or not email:
                        fail_count += 1
                        fail_reasons.append(f"第{row_num}行: 缺少必填字段")
                        continue

                    existing_student = db.query(Student).filter(
                        Student.student_id == student_id
                    ).first()

                    if existing_student:
                        fail_count += 1
                        fail_reasons.append(f"第{row_num}行: 学号{student_id}已存在")
                        continue

                    existing_user = db.query(User).filter(
                        (User.username == student_id) | (User.email == email)
                    ).first()

                    if existing_user:
                        fail_count += 1
                        fail_reasons.append(f"第{row_num}行: 用户名或邮箱已存在")
                        continue

                    new_user = User(
                        username=student_id,
                        password_hash=get_password_hash(initial_password),
                        email=email,
                        real_name=real_name,
                        role="student",
                        is_active=True
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)

                    new_student = Student(
                        user_id=new_user.user_id,
                        student_id=student_id,
                        first_password_changed=False
                    )
                    db.add(new_student)
                    db.commit()

                    if class_id:
                        existing_class = db.query(Class).filter(
                            Class.class_id == class_id
                        ).first()

                        if existing_class:
                            if current_user.role == "teacher" and existing_class.teacher_id != current_user.user_id:
                                pass
                            else:
                                class_student = ClassStudent(
                                    class_id=class_id,
                                    student_user_id=new_user.user_id
                                )
                                db.add(class_student)
                                db.commit()

                    success_count += 1
                    imported_students.append({
                        "student_id": student_id,
                        "real_name": real_name,
                        "user_id": new_user.user_id
                    })

                except Exception as e:
                    fail_count += 1
                    fail_reasons.append(f"第{row_num}行: {str(e)}")

        else:
            fail_count = 1
            fail_reasons.append("Excel文件暂未支持，请使用CSV格式")

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件编码错误，请保存为UTF-8格式"
        )

    return ResponseModel(
        code=200,
        msg="导入完成",
        data={
            "success_count": success_count,
            "fail_count": fail_count,
            "fail_reasons": fail_reasons[:20],
            "imported_students": imported_students
        }
    )

@router.get("", response_model=ResponseModel)
async def get_students_list(
    class_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="学生无权限查看学生列表"
        )

    query = db.query(Student, User).join(User, Student.user_id == User.user_id)

    if class_id:
        class_students = db.query(ClassStudent.student_user_id).filter(
            ClassStudent.class_id == class_id
        ).all()
        student_ids = [cs.student_user_id for cs in class_students]
        query = query.filter(Student.user_id.in_(student_ids))

    if keyword:
        query = query.filter(
            (Student.student_id.contains(keyword)) |
            (User.real_name.contains(keyword)) |
            (User.email.contains(keyword))
        )

    total = query.count()
    results = query.offset((page - 1) * size).limit(size).all()

    students_data = []
    for student, user in results:
        student_classes = db.query(ClassStudent).filter(
            ClassStudent.student_user_id == student.user_id
        ).all()
        class_ids = [sc.class_id for sc in student_classes]

        classes_info = []
        for cid in class_ids:
            cls = db.query(Class).filter(Class.class_id == cid).first()
            if cls:
                course = db.query(Course).filter(Course.course_id == cls.course_id).first()
                classes_info.append({
                    "class_id": cls.class_id,
                    "class_name": cls.class_name,
                    "course_name": course.course_name if course else None
                })

        students_data.append({
            "user_id": user.user_id,
            "student_id": student.student_id,
            "real_name": user.real_name,
            "email": user.email,
            "is_active": user.is_active,
            "first_password_changed": student.first_password_changed,
            "classes": classes_info,
            "created_at": user.created_at.isoformat()
        })

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "students": students_data
        }
    )

@router.post("/{user_id}/reset-password", response_model=ResponseModel)
async def reset_student_password(
    user_id: int,
    new_password: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师或管理员可以重置学生密码"
        )

    student = db.query(Student).filter(Student.user_id == user_id).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    user = db.query(User).filter(User.user_id == user_id).first()

    if new_password:
        user.password_hash = get_password_hash(new_password)
    else:
        user.password_hash = get_password_hash(student.student_id + '123456')

    student.first_password_changed = False

    db.commit()

    return ResponseModel(
        code=200,
        msg="密码重置成功",
        data={
            "user_id": user_id,
            "new_password": new_password if new_password else student.student_id + '123456'
        }
    )

@router.patch("/{user_id}/status", response_model=ResponseModel)
async def toggle_student_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == user_id).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    user.is_active = is_active

    db.commit()

    status_text = "启用" if is_active else "停用"

    return ResponseModel(
        code=200,
        msg=f"学生账号已{status_text}",
        data={"user_id": user_id, "is_active": is_active}
    )

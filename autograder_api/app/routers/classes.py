from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User, Course, Class, ClassStudent, Student
from app.schemas import ClassCreate, StudentAddToClass, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/classes", tags=["班级管理"])

@router.get("", response_model=ResponseModel)
async def get_classes_list(
    course_id: int = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Class)

    if current_user.role == "teacher":
        query = query.filter(Class.teacher_id == current_user.user_id)
    elif current_user.role == "student":
        student_classes = db.query(ClassStudent.class_id).filter(
            ClassStudent.student_user_id == current_user.user_id
        ).all()
        class_ids = [cls.class_id for cls in student_classes]
        query = query.filter(Class.class_id.in_(class_ids))

    if course_id:
        query = query.filter(Class.course_id == course_id)

    total = query.count()
    classes = query.order_by(Class.created_at.desc()).offset((page - 1) * size).limit(size).all()

    classes_data = []
    for cls in classes:
        class_dict = {
            "class_id": cls.class_id,
            "course_id": cls.course_id,
            "course_name": cls.course.course_name,
            "class_name": cls.class_name,
            "class_code": cls.class_code,
            "teacher_id": cls.teacher_id,
            "teacher_name": cls.teacher.real_name,
            "created_at": cls.created_at.isoformat()
        }
        classes_data.append(class_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "classes": classes_data
        }
    )

@router.post("", response_model=ResponseModel)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师可以创建班级"
        )
    
    course = db.query(Course).filter(Course.course_id == class_data.courseId).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    if course.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能在自己的课程下创建班级"
        )
    
    existing_class = db.query(Class).filter(
        Class.course_id == class_data.courseId,
        Class.class_code == class_data.classCode
    ).first()
    
    if existing_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该课程下已存在相同课序号的班级"
        )
    
    new_class = Class(
        course_id=class_data.courseId,
        class_name=class_data.className,
        class_code=class_data.classCode,
        teacher_id=current_user.user_id
    )
    
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return ResponseModel(
        code=200,
        msg="班级创建成功",
        data={"class_id": new_class.class_id}
    )

@router.get("/{class_id}/students", response_model=ResponseModel)
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    students = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
    
    students_data = []
    for student_rel in students:
        student_user = student_rel.student
        student_profile = db.query(Student).filter(
            Student.user_id == student_user.user_id
        ).first()
        
        student_dict = {
            "user_id": student_user.user_id,
            "student_id": student_profile.student_id if student_profile else None,
            "real_name": student_user.real_name,
            "email": student_user.email,
            "joined_at": student_rel.joined_at.isoformat()
        }
        students_data.append(student_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=students_data
    )

@router.post("/{class_id}/students", response_model=ResponseModel)
async def add_student_to_class(
    class_id: int,
    student_data: StudentAddToClass,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    if class_info.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此班级"
        )
    
    existing = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_user_id == student_data.studentUserId
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学生已在该班级中"
        )
    
    new_student = ClassStudent(
        class_id=class_id,
        student_user_id=student_data.studentUserId
    )
    
    db.add(new_student)
    db.commit()
    
    return ResponseModel(
        code=200,
        msg="学生添加成功",
        data=None
    )

@router.post("/{class_id}/students/import", response_model=ResponseModel)
async def import_students(
    class_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    if class_info.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此班级"
        )
    
    success_count = 0
    fail_count = 0
    fail_reasons = []
    
    return ResponseModel(
        code=200,
        msg="导入完成",
        data={
            "success_count": success_count,
            "fail_count": fail_count,
            "fail_reasons": fail_reasons
        }
    )

@router.delete("/{class_id}/students/{student_user_id}", response_model=ResponseModel)
async def remove_student_from_class(
    class_id: int,
    student_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    if class_info.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此班级"
        )
    
    student_rel = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_user_id == student_user_id
    ).first()
    
    if not student_rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不在该班级中"
        )
    
    db.delete(student_rel)
    db.commit()
    
    return ResponseModel(
        code=200,
        msg="学生移除成功",
        data=None
    )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import User, Course, Class
from app.schemas import CourseCreate, CourseUpdate, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/courses", tags=["课程管理"])

@router.get("", response_model=ResponseModel)
async def get_courses_list(
    teacher_id: Optional[int] = Query(None),
    semester: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Course)
    
    if current_user.role == "teacher":
        query = query.filter(Course.teacher_id == current_user.user_id)
    elif current_user.role == "student":
        from app.models.models import ClassStudent
        student_classes = db.query(ClassStudent.class_id).filter(
            ClassStudent.student_user_id == current_user.user_id
        ).all()
        class_ids = [cls.class_id for cls in student_classes]
        course_ids = db.query(Class.course_id).filter(Class.class_id.in_(class_ids)).all()
        query = query.filter(Course.course_id.in_([c.course_id for c in course_ids]))
    
    if teacher_id:
        query = query.filter(Course.teacher_id == teacher_id)
    
    if semester:
        query = query.filter(Course.semester == semester)
    
    courses = query.all()
    
    courses_data = []
    for course in courses:
        course_dict = {
            "course_id": course.course_id,
            "course_code": course.course_code,
            "course_name": course.course_name,
            "teacher_id": course.teacher_id,
            "teacher_name": course.teacher.real_name,
            "semester": course.semester,
            "description": course.description,
            "created_at": course.created_at.isoformat()
        }
        courses_data.append(course_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=courses_data
    )

@router.post("", response_model=ResponseModel)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师可以创建课程"
        )
    
    existing_course = db.query(Course).filter(
        Course.course_code == course_data.courseCode,
        Course.semester == course_data.semester
    ).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该课程编号在当前学期已存在"
        )
    
    new_course = Course(
        course_code=course_data.courseCode,
        course_name=course_data.courseName,
        teacher_id=current_user.user_id,
        semester=course_data.semester,
        description=course_data.description
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return ResponseModel(
        code=200,
        msg="课程创建成功",
        data={"course_id": new_course.course_id}
    )

@router.get("/{course_id}", response_model=ResponseModel)
async def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    course_dict = {
        "course_id": course.course_id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "teacher_id": course.teacher_id,
        "teacher_name": course.teacher.real_name,
        "semester": course.semester,
        "description": course.description,
        "created_at": course.created_at.isoformat()
    }
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=course_dict
    )

@router.put("/{course_id}", response_model=ResponseModel)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    if course.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此课程"
        )
    
    if course_data.courseName:
        course.course_name = course_data.courseName
    
    if course_data.description is not None:
        course.description = course_data.description
    
    db.commit()
    db.refresh(course)
    
    return ResponseModel(
        code=200,
        msg="课程更新成功",
        data={"course_id": course.course_id}
    )

@router.delete("/{course_id}", response_model=ResponseModel)
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    if course.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此课程"
        )
    
    from app.models.models import Assignment
    published_assignments = db.query(Assignment).filter(
        Assignment.class_id.in_([c.class_id for c in course.classes]),
        Assignment.is_published == True
    ).first()
    
    if published_assignments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="课程下存在已发布的作业，无法删除"
        )
    
    db.delete(course)
    db.commit()
    
    return ResponseModel(
        code=200,
        msg="课程删除成功",
        data=None
    )

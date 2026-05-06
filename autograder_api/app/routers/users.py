from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import User, Student, Teacher
from app.schemas import (
    UserInfo, UserUpdate, TeacherCreate, ResponseModel
)
from app.auth import (
    get_current_user, 
    get_password_hash, 
    require_role
)

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_info = UserInfo.from_orm(current_user)
    
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
        if student:
            user_info.student_id = student.student_id
    elif current_user.role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == current_user.user_id).first()
        if teacher:
            user_info.teacher_id = teacher.teacher_id
            user_info.department = teacher.department
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=user_info.dict()
    )

@router.put("/me", response_model=ResponseModel)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_update.email
    
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    
    if user_update.avatar:
        current_user.avatar_url = user_update.avatar
    
    if user_update.old_password and user_update.new_password:
        from app.auth import verify_password
        if not verify_password(user_update.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        current_user.password_hash = get_password_hash(user_update.new_password)
    
    db.commit()
    db.refresh(current_user)
    
    return ResponseModel(
        code=200,
        msg="用户信息更新成功",
        data={"user_id": current_user.user_id}
    )

@router.get("", response_model=ResponseModel)
async def get_users_list(
    role: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    users_data = []
    for user in users:
        user_dict = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "real_name": user.real_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        
        if user.role == "student":
            student = db.query(Student).filter(Student.user_id == user.user_id).first()
            if student:
                user_dict["student_id"] = student.student_id
        elif user.role == "teacher":
            teacher = db.query(Teacher).filter(Teacher.user_id == user.user_id).first()
            if teacher:
                user_dict["teacher_id"] = teacher.teacher_id
                user_dict["department"] = teacher.department
        
        users_data.append(user_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "users": users_data
        }
    )

@router.post("", response_model=ResponseModel)
async def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    existing_teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_data.teacher_id
    ).first()
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工号已存在"
        )
    
    existing_user = db.query(User).filter(
        (User.username == teacher_data.teacher_id) | (User.email == teacher_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    new_user = User(
        username=teacher_data.teacher_id,
        password_hash=get_password_hash(teacher_data.initial_password),
        email=teacher_data.email,
        real_name=teacher_data.real_name,
        role="teacher"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    new_teacher = Teacher(
        user_id=new_user.user_id,
        teacher_id=teacher_data.teacher_id,
        department=teacher_data.department
    )
    db.add(new_teacher)
    db.commit()
    
    return ResponseModel(
        code=200,
        msg="教师账号创建成功",
        data={"user_id": new_user.user_id, "teacher_id": teacher_data.teacher_id}
    )

@router.post("/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.is_active = False
    db.commit()
    
    return ResponseModel(
        code=200,
        msg="账号已停用",
        data=None
    )

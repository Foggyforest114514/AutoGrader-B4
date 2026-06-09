from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.models import User, Student, Teacher
from app.schemas import UserLogin, TokenData, ResponseModel, PasswordReset, TokenRefresh, UserCreate
from app.auth import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token,
    get_current_user,
    get_password_hash
)

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/login", response_model=ResponseModel)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # 首先尝试通过用户名或邮箱查找
    user = db.query(User).filter(
        (User.username == user_login.username) | (User.email == user_login.username)
    ).first()
    
    # 如果没有找到，尝试通过学号查找学生
    if not user:
        student = db.query(Student).filter(Student.student_id == user_login.username).first()
        if student:
            user = db.query(User).filter(User.user_id == student.user_id).first()
    
    # 如果还没有找到，尝试通过工号查找教师
    if not user:
        teacher = db.query(Teacher).filter(Teacher.teacher_id == user_login.username).first()
        if teacher:
            user = db.query(User).filter(User.user_id == teacher.user_id).first()
    
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被停用"
        )
    
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": str(user.user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    token_data = TokenData(
        token=access_token,
        refreshToken=refresh_token,
        role=user.role.value,
        userId=str(user.user_id)
    )
    
    return ResponseModel(
        code=200,
        msg="登录成功",
        data=token_data.dict()
    )

@router.post("/logout", response_model=ResponseModel)
async def logout(current_user: User = Depends(get_current_user)):
    return ResponseModel(
        code=200,
        msg="登出成功",
        data=None
    )

@router.post("/register", response_model=ResponseModel)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    # 检查纯数字用户名
    if user_create.username.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为纯数字，请包含字母或中文"
        )

    existing_user = db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )

    # 检查用户名是否与已有学号/工号冲突
    conflict = db.query(Student).filter(Student.student_id == user_create.username).first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能与已有学号相同"
        )
    conflict = db.query(Teacher).filter(Teacher.teacher_id == user_create.username).first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能与已有工号相同"
        )
    
    if user_create.role not in ["student", "teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色类型"
        )
    
    if user_create.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账号只能由系统创建"
        )
    
    password = user_create.password

    new_user = User(
        username=user_create.username,
        password_hash=get_password_hash(password),
        email=user_create.email,
        real_name=user_create.real_name,
        phone=user_create.phone,
        role=user_create.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if user_create.role == "student":
        new_student = Student(
            user_id=new_user.user_id,
            student_id=user_create.student_id or user_create.username,
            first_password_changed=False
        )
        db.add(new_student)
        db.commit()
    
    if user_create.role == "teacher":
        new_teacher = Teacher(
            user_id=new_user.user_id,
            teacher_id=user_create.teacher_id or user_create.username,
            department=user_create.department
        )
        db.add(new_teacher)
        db.commit()
    
    return ResponseModel(
        code=200,
        msg="注册成功",
        data={"user_id": new_user.user_id, "role": new_user.role.value}
    )

@router.post("/refresh", response_model=ResponseModel)
async def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    payload = decode_token(token_refresh.refreshToken)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被停用"
        )
    
    access_token = create_access_token(data={"sub": str(user.user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    token_data = TokenData(
        token=access_token,
        refreshToken=refresh_token,
        role=user.role.value,
        userId=str(user.user_id)
    )
    
    return ResponseModel(
        code=200,
        msg="令牌刷新成功",
        data=token_data.dict()
    )

@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
    # 第一步：用户名 + 真实姓名 + 邮箱 三重验证
    user = db.query(User).filter(
        User.username == password_reset.username,
        User.real_name == password_reset.real_name,
        User.email == password_reset.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户信息不匹配，请检查用户名、姓名和邮箱"
        )

    # 第二步：非管理员需要验证学号/工号
    if user.role == "student":
        if not password_reset.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学生需要提供学号"
            )
        student = db.query(Student).filter(
            Student.user_id == user.user_id,
            Student.student_id == password_reset.student_id
        ).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学号不匹配"
            )
    elif user.role == "teacher":
        if not password_reset.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师需要提供工号"
            )
        teacher = db.query(Teacher).filter(
            Teacher.user_id == user.user_id,
            Teacher.teacher_id == password_reset.teacher_id
        ).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工号不匹配"
            )

    user.password_hash = get_password_hash(password_reset.new_password)
    db.commit()

    return ResponseModel(
        code=200,
        msg="密码重置成功",
        data={"username": user.username}
    )

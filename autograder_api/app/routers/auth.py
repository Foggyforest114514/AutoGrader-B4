from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.models import User
from app.schemas import UserLogin, TokenData, ResponseModel, PasswordReset, TokenRefresh
from app.auth import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token,
    get_current_user
)

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/login", response_model=ResponseModel)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == user_login.username) | (User.email == user_login.username)
    ).first()
    
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
        role=user.role,
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
        role=user.role,
        userId=str(user.user_id)
    )
    
    return ResponseModel(
        code=200,
        msg="令牌刷新成功",
        data=token_data.dict()
    )

@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == password_reset.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮箱未注册"
        )
    
    return ResponseModel(
        code=200,
        msg="密码重置邮件已发送",
        data=None
    )

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import User, Student
from app.auth import get_password_hash
from datetime import datetime

def test_register():
    print("="*50)
    print("测试注册功能")
    print("="*50)
    
    db = SessionLocal()
    
    try:
        test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
        test_email = f"{test_username}@example.com"
        
        print(f"\n尝试创建新用户: {test_username}")
        
        existing_user = db.query(User).filter(
            (User.username == test_username) | (User.email == test_email)
        ).first()
        
        if existing_user:
            print(f"用户已存在: {existing_user.username}")
            return
        
        new_user = User(
            username=test_username,
            password_hash=get_password_hash("test123456"),
            email=test_email,
            real_name="测试用户",
            phone="13800138000",
            role="student",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"用户创建成功! user_id={new_user.user_id}")
        
        new_student = Student(
            user_id=new_user.user_id,
            student_id=test_username,
            first_password_changed=False
        )
        db.add(new_student)
        db.commit()
        
        print(f"学生资料创建成功!")
        
        users_count = db.query(User).count()
        print(f"\n当前数据库总用户数: {users_count}")
        
        print("\n最近5个用户:")
        recent_users = db.query(User).order_by(User.user_id.desc()).limit(5).all()
        for u in recent_users:
            print(f"  - user_id={u.user_id}, username={u.username}, email={u.email}")
            
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_register()

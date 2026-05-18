from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.models import User, Assignment, Class, ClassStudent
from app.schemas import AssignmentCreate, AssignmentUpdate, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/assignments", tags=["作业管理"])

@router.get("", response_model=ResponseModel)
async def get_assignments_list(
    class_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Assignment)
    
    if current_user.role == "teacher":
        query = query.filter(Assignment.teacher_id == current_user.user_id)
    elif current_user.role == "student":
        student_classes = db.query(ClassStudent.class_id).filter(
            ClassStudent.student_user_id == current_user.user_id
        ).all()
        class_ids = [cls.class_id for cls in student_classes]
        query = query.filter(
            Assignment.class_id.in_(class_ids),
            Assignment.is_published == True
        )
    
    if class_id:
        query = query.filter(Assignment.class_id == class_id)
    
    assignments = query.all()
    
    assignments_data = []
    for assignment in assignments:
        assignment_dict = {
            "assignment_id": assignment.assignment_id,
            "title": assignment.title,
            "description": assignment.description,
            "class_id": assignment.class_id,
            "class_name": assignment.class_info.class_name,
            "teacher_id": assignment.teacher_id,
            "teacher_name": assignment.teacher.real_name,
            "due_date": assignment.due_date.isoformat(),
            "is_published": assignment.is_published,
            "allow_resubmit": assignment.allow_resubmit,
            "question_id": assignment.question_id,
            "created_at": assignment.created_at.isoformat()
        }
        assignments_data.append(assignment_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=assignments_data
    )

@router.post("", response_model=ResponseModel)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师可以创建作业"
        )
    
    class_info = db.query(Class).filter(Class.class_id == assignment_data.classId).first()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    if class_info.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能在自己的班级下创建作业"
        )
    
    new_assignment = Assignment(
        title=assignment_data.title,
        description=assignment_data.description,
        class_id=assignment_data.classId,
        teacher_id=current_user.user_id,
        due_date=assignment_data.dueDate,
        is_published=assignment_data.isPublished,
        allow_resubmit=assignment_data.allowResubmit,
        question_id=assignment_data.question_id
    )
    
    if assignment_data.isPublished:
        new_assignment.published_at = datetime.utcnow()
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return ResponseModel(
        code=200,
        msg="作业创建成功",
        data={"assignment_id": new_assignment.assignment_id}
    )

@router.get("/{assignment_id}", response_model=ResponseModel)
async def get_assignment_detail(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )
    
    if current_user.role == "student" and not assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="作业未发布"
        )
    
    assignment_dict = {
        "assignment_id": assignment.assignment_id,
        "title": assignment.title,
        "description": assignment.description,
        "class_id": assignment.class_id,
        "class_name": assignment.class_info.class_name,
        "teacher_id": assignment.teacher_id,
        "teacher_name": assignment.teacher.real_name,
        "due_date": assignment.due_date.isoformat(),
        "is_published": assignment.is_published,
        "allow_resubmit": assignment.allow_resubmit,
        "question_id": assignment.question_id,
        "created_at": assignment.created_at.isoformat(),
        "published_at": assignment.published_at.isoformat() if assignment.published_at else None
    }
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=assignment_dict
    )

@router.put("/{assignment_id}", response_model=ResponseModel)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )
    
    if assignment.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此作业"
        )
    
    if assignment_data.title:
        assignment.title = assignment_data.title
    
    if assignment_data.description is not None:
        assignment.description = assignment_data.description
    
    if assignment_data.dueDate:
        assignment.due_date = assignment_data.dueDate
    
    if assignment_data.allowResubmit is not None:
        assignment.allow_resubmit = assignment_data.allowResubmit
    
    db.commit()
    db.refresh(assignment)
    
    return ResponseModel(
        code=200,
        msg="作业更新成功",
        data={"assignment_id": assignment.assignment_id}
    )

@router.post("/{assignment_id}/publish", response_model=ResponseModel)
async def publish_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )
    
    if assignment.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限发布此作业"
        )
    
    if assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="作业已发布"
        )
    
    assignment.is_published = True
    assignment.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assignment)
    
    return ResponseModel(
        code=200,
        msg="作业发布成功",
        data={"assignment_id": assignment.assignment_id}
    )


@router.delete("/{assignment_id}", response_model=ResponseModel)
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )

    if assignment.teacher_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此作业"
        )

    db.delete(assignment)
    db.commit()

    return ResponseModel(
        code=200,
        msg="作业删除成功",
        data=None
    )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import User, Submission, Assignment, Class, ClassStudent, Student
from app.schemas import ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/grades", tags=["成绩管理"])

@router.get("/my", response_model=ResponseModel)
async def get_my_grades(
    assignment_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此接口仅限学生使用"
        )
    
    query = db.query(Submission).filter(
        Submission.student_user_id == current_user.user_id,
        Submission.status == "COMPLETED"
    )
    
    if assignment_id:
        query = query.filter(Submission.assignment_id == assignment_id)
    
    submissions = query.all()
    
    grades_data = []
    for submission in submissions:
        student_profile = db.query(Student).filter(
            Student.user_id == current_user.user_id
        ).first()
        
        grade_dict = {
            "student_id": student_profile.student_id if student_profile else None,
            "student_name": current_user.real_name,
            "assignment_id": submission.assignment_id,
            "assignment_title": submission.assignment.title,
            "score": submission.teacher_score_override or submission.overall_score,
            "submitted_at": submission.submitted_at.isoformat(),
            "status": submission.status
        }
        grades_data.append(grade_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=grades_data
    )

@router.get("/class/{class_id}", response_model=ResponseModel)
async def get_class_grades(
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
    
    if current_user.role == "teacher" and class_info.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此班级成绩"
        )
    elif current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="学生无权限查看班级成绩"
        )
    
    students = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
    
    assignments = db.query(Assignment).filter(
        Assignment.class_id == class_id,
        Assignment.is_published == True
    ).all()
    
    grades_data = []
    for student_rel in students:
        student_user = student_rel.student
        student_profile = db.query(Student).filter(
            Student.user_id == student_user.user_id
        ).first()
        
        student_grades = {
            "user_id": student_user.user_id,
            "student_id": student_profile.student_id if student_profile else None,
            "student_name": student_user.real_name,
            "assignments": []
        }
        
        total_score = 0
        for assignment in assignments:
            submission = db.query(Submission).filter(
                Submission.student_user_id == student_user.user_id,
                Submission.assignment_id == assignment.assignment_id,
                Submission.status == "COMPLETED"
            ).order_by(Submission.submitted_at.desc()).first()
            
            score = None
            if submission:
                score = submission.teacher_score_override or submission.overall_score
                if score:
                    total_score += score
            
            student_grades["assignments"].append({
                "assignment_id": assignment.assignment_id,
                "assignment_title": assignment.title,
                "score": score
            })
        
        student_grades["total_score"] = total_score
        grades_data.append(student_grades)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=grades_data
    )

@router.get("/export/{assignment_id}", response_model=ResponseModel)
async def export_assignment_grades(
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
    
    if current_user.role == "teacher" and assignment.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限导出此作业成绩"
        )
    elif current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="学生无权限导出成绩"
        )
    
    students = db.query(ClassStudent).filter(
        ClassStudent.class_id == assignment.class_id
    ).all()
    
    grades_data = []
    for student_rel in students:
        student_user = student_rel.student
        student_profile = db.query(Student).filter(
            Student.user_id == student_user.user_id
        ).first()
        
        submission = db.query(Submission).filter(
            Submission.student_user_id == student_user.user_id,
            Submission.assignment_id == assignment_id,
            Submission.status == "COMPLETED"
        ).order_by(Submission.submitted_at.desc()).first()
        
        grade_dict = {
            "student_id": student_profile.student_id if student_profile else None,
            "student_name": student_user.real_name,
            "score": submission.teacher_score_override or submission.overall_score if submission else None,
            "submitted_at": submission.submitted_at.isoformat() if submission else None,
            "status": submission.status if submission else "未提交"
        }
        grades_data.append(grade_dict)
    
    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "assignment_title": assignment.title,
            "grades": grades_data
        }
    )

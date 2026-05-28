from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
from app.database import get_db
from app.models.models import User, Submission, Assignment, ClassStudent
from app.schemas import SubmissionCreate, SubmissionResultUpdate, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/submissions", tags=["提交管理"])

@router.post("", response_model=ResponseModel)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有学生可以提交作业"
        )
    
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission_data.assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在"
        )
    
    if not assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="作业未发布"
        )
    
    student_in_class = db.query(ClassStudent).filter(
        ClassStudent.class_id == assignment.class_id,
        ClassStudent.student_user_id == current_user.user_id
    ).first()
    
    if not student_in_class:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不在该作业所在的班级中"
        )
    
    if datetime.utcnow() > assignment.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="作业已截止"
        )
    
    submission_id = str(uuid.uuid4())
    
    new_submission = Submission(
        submission_id=submission_id,
        student_user_id=current_user.user_id,
        question_id=submission_data.question_id,
        assignment_id=submission_data.assignment_id,
        code=submission_data.code,
        language=submission_data.language,
        status="PENDING"
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return ResponseModel(
        code=200,
        msg="提交成功",
        data={"submission_id": submission_id}
    )

@router.get("/my", response_model=ResponseModel)
async def get_my_submissions(
    assignment_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Submission).filter(
        Submission.student_user_id == current_user.user_id
    )

    if assignment_id:
        query = query.filter(Submission.assignment_id == assignment_id)

    submissions = query.order_by(Submission.submitted_at.desc()).all()

    submissions_data = []
    for submission in submissions:
        submission_dict = {
            "submission_id": submission.submission_id,
            "assignment_id": submission.assignment_id,
            "assignment_title": submission.assignment.title,
            "question_id": submission.question_id,
            "submitted_at": submission.submitted_at.isoformat(),
            "status": submission.status,
            "overall_score": submission.overall_score
        }
        submissions_data.append(submission_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data=submissions_data
    )

@router.get("/{submission_id}", response_model=ResponseModel)
async def get_submission_detail(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    if current_user.role == "student" and submission.student_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此提交记录"
        )
    
    submission_dict = {
        "submission_id": submission.submission_id,
        "student_user_id": submission.student_user_id,
        "student_name": submission.student.real_name,
        "question_id": submission.question_id,
        "assignment_id": submission.assignment_id,
        "assignment_title": submission.assignment.title,
        "code": submission.code,
        "language": submission.language,
        "submitted_at": submission.submitted_at.isoformat(),
        "status": submission.status,
        "overall_score": submission.overall_score,
        "passed_count": submission.passed_count,
        "total_count": submission.total_count,
        "overall_comment": submission.overall_comment,
        "static_issues": submission.static_issues,
        "case_results": submission.case_results,
        "teacher_score_override": submission.teacher_score_override,
        "override_reason": submission.override_reason
    }
    
    return ResponseModel(
        code=200,
        msg="成功",
        data=submission_dict
    )

@router.patch("/{submission_id}/result", response_model=ResponseModel)
async def update_submission_result(
    submission_id: str,
    result_data: SubmissionResultUpdate,
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    submission.status = result_data.status
    
    if result_data.overallScore is not None:
        submission.overall_score = result_data.overallScore
    
    if result_data.passedCount is not None:
        submission.passed_count = result_data.passedCount
    
    if result_data.totalCount is not None:
        submission.total_count = result_data.totalCount
    
    if result_data.overallComment is not None:
        submission.overall_comment = result_data.overallComment
    
    if result_data.staticIssues is not None:
        submission.static_issues = result_data.staticIssues
    
    if result_data.caseResults is not None:
        submission.case_results = result_data.caseResults
    
    db.commit()
    db.refresh(submission)
    
    return ResponseModel(
        code=200,
        msg="评测结果更新成功",
        data={"submission_id": submission_id}
    )

@router.get("/assignment/{assignment_id}/all", response_model=ResponseModel)
async def get_assignment_all_submissions(
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
            detail="无权限查看此作业的提交"
        )

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).order_by(Submission.submitted_at.desc()).all()

    submissions_data = []
    for submission in submissions:
        submission_dict = {
            "submission_id": submission.submission_id,
            "student_user_id": submission.student_user_id,
            "student_name": submission.student.real_name,
            "question_id": submission.question_id,
            "submitted_at": submission.submitted_at.isoformat(),
            "status": submission.status,
            "overall_score": submission.overall_score,
            "passed_count": submission.passed_count,
            "total_count": submission.total_count
        }
        submissions_data.append(submission_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "assignment_title": assignment.title,
            "total_submissions": len(submissions_data),
            "submissions": submissions_data
        }
    )

@router.patch("/{submission_id}/override", response_model=ResponseModel)
async def override_submission_score(
    submission_id: str,
    override_score: float,
    override_reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师或管理员可以覆盖分数"
        )

    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )

    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id
    ).first()

    if current_user.role == "teacher" and assignment.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能覆盖自己布置的作业的分数"
        )

    submission.teacher_score_override = override_score
    submission.override_reason = override_reason

    db.commit()
    db.refresh(submission)

    return ResponseModel(
        code=200,
        msg="分数覆盖成功",
        data={
            "submission_id": submission_id,
            "override_score": override_score
        }
    )

@router.get("/statistics/assignment/{assignment_id}", response_model=ResponseModel)
async def get_assignment_submission_statistics(
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
            detail="无权限查看此作业的统计"
        )

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.status == "COMPLETED"
    ).all()

    total_submissions = len(submissions)
    total_students = db.query(ClassStudent).filter(
        ClassStudent.class_id == assignment.class_id
    ).count()

    scores = [s.overall_score for s in submissions if s.overall_score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    passed_count = len([s for s in submissions if s.overall_score and s.overall_score >= 60])
    pass_rate = (passed_count / total_submissions * 100) if total_submissions > 0 else 0

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "assignment_id": assignment_id,
            "assignment_title": assignment.title,
            "total_students": total_students,
            "total_submissions": total_submissions,
            "submission_rate": (total_submissions / total_students * 100) if total_students > 0 else 0,
            "average_score": round(average_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "pass_rate": round(pass_rate, 2),
            "score_distribution": {
                "excellent": len([s for s in scores if s >= 90]),
                "good": len([s for s in scores if 80 <= s < 90]),
                "medium": len([s for s in scores if 70 <= s < 80]),
                "pass": len([s for s in scores if 60 <= s < 70]),
                "fail": len([s for s in scores if s < 60])
            }
        }
    )

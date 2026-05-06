from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models.models import User, Announcement, Course, Assignment, Submission, Class, ClassStudent, Student, SystemLog
from app.schemas import ResponseModel
from app.schemas_extend import (
    AnnouncementCreate, AnnouncementUpdate,
    SystemStats, DatabaseHealth
)
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1/system", tags=["系统管理"])

@router.get("/stats", response_model=ResponseModel)
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_students = db.query(Student).count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_courses = db.query(Course).count()
    total_classes = db.query(Class).count()
    total_assignments = db.query(Assignment).count()
    total_submissions = db.query(Submission).count()
    pending_submissions = db.query(Submission).filter(Submission.status == "PENDING").count()
    completed_submissions = db.query(Submission).filter(Submission.status == "COMPLETED").count()

    stats = SystemStats(
        total_users=total_users,
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        total_classes=total_classes,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        pending_submissions=pending_submissions,
        completed_submissions=completed_submissions
    )

    return ResponseModel(
        code=200,
        msg="成功",
        data=stats.dict()
    )

@router.get("/health", response_model=ResponseModel)
async def get_database_health(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))

        result = db.execute(text("SELECT @@max_connections as max_conn")).fetchone()
        max_conn = result[0] if result else 100

        result = db.execute(text("SHOW STATUS LIKE 'Threads_connected'")).fetchone()
        current_conn = int(result[1]) if result else 0

        health = DatabaseHealth(
            status="healthy",
            connection_count=current_conn,
            max_connections=max_conn,
            active_connections=current_conn
        )

        return ResponseModel(
            code=200,
            msg="成功",
            data=health.dict()
        )
    except Exception as e:
        return ResponseModel(
            code=200,
            msg="警告：数据库连接异常",
            data={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@router.get("/announcements", response_model=ResponseModel)
async def get_announcements(
    course_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Announcement)

    if course_id:
        query = query.filter(Announcement.course_id == course_id)
    elif current_user.role == "teacher":
        teacher_courses = db.query(Course.course_id).filter(
            Course.teacher_id == current_user.user_id
        ).all()
        course_ids = [c.course_id for c in teacher_courses]
        query = query.filter(
            (Announcement.course_id.in_(course_ids)) | (Announcement.course_id.is_(None))
        )
    elif current_user.role == "student":
        student_classes = db.query(ClassStudent.class_id).filter(
            ClassStudent.student_user_id == current_user.user_id
        ).all()
        class_ids = [cls.class_id for cls in student_classes]
        student_courses = db.query(Class.course_id).filter(
            Class.class_id.in_(class_ids)
        ).all()
        course_ids = [c.course_id for c in student_courses]
        query = query.filter(
            (Announcement.course_id.in_(course_ids)) | (Announcement.course_id.is_(None))
        )

    total = query.count()
    announcements = query.order_by(Announcement.created_at.desc()).offset((page - 1) * size).limit(size).all()

    announcements_data = []
    for announcement in announcements:
        course_name = None
        if announcement.course_id:
            course = db.query(Course).filter(Course.course_id == announcement.course_id).first()
            course_name = course.course_name if course else None

        creator = db.query(User).filter(User.user_id == announcement.created_by).first()

        announcement_dict = {
            "announcement_id": announcement.announcement_id,
            "course_id": announcement.course_id,
            "course_name": course_name,
            "title": announcement.title,
            "content": announcement.content,
            "created_by": announcement.created_by,
            "creator_name": creator.real_name if creator else None,
            "created_at": announcement.created_at.isoformat()
        }
        announcements_data.append(announcement_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "announcements": announcements_data
        }
    )

@router.post("/announcements", response_model=ResponseModel)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师或管理员可以发布公告"
        )

    if announcement_data.course_id:
        course = db.query(Course).filter(Course.course_id == announcement_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )

        if current_user.role == "teacher" and course.teacher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能在自己负责的课程下发布公告"
            )

    new_announcement = Announcement(
        course_id=announcement_data.course_id,
        title=announcement_data.title,
        content=announcement_data.content,
        created_by=current_user.user_id
    )

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    return ResponseModel(
        code=200,
        msg="公告发布成功",
        data={
            "announcement_id": new_announcement.announcement_id
        }
    )

@router.put("/announcements/{announcement_id}", response_model=ResponseModel)
async def update_announcement(
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    announcement = db.query(Announcement).filter(
        Announcement.announcement_id == announcement_id
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )

    if current_user.role == "teacher" and announcement.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己发布的公告"
        )
    elif current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="学生无权限修改公告"
        )

    if announcement_data.title is not None:
        announcement.title = announcement_data.title

    if announcement_data.content is not None:
        announcement.content = announcement_data.content

    db.commit()
    db.refresh(announcement)

    return ResponseModel(
        code=200,
        msg="公告更新成功",
        data={"announcement_id": announcement_id}
    )

@router.delete("/announcements/{announcement_id}", response_model=ResponseModel)
async def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    announcement = db.query(Announcement).filter(
        Announcement.announcement_id == announcement_id
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )

    if current_user.role == "teacher" and announcement.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己发布的公告"
        )
    elif current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="学生无权限删除公告"
        )

    db.delete(announcement)
    db.commit()

    return ResponseModel(
        code=200,
        msg="公告删除成功",
        data=None
    )

@router.get("/logs", response_model=ResponseModel)
async def get_system_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    query = db.query(SystemLog)

    if user_id:
        query = query.filter(SystemLog.user_id == user_id)

    if action:
        query = query.filter(SystemLog.action == action)

    if start_date:
        query = query.filter(SystemLog.created_at >= start_date)

    if end_date:
        query = query.filter(SystemLog.created_at <= end_date)

    total = query.count()
    logs = query.order_by(SystemLog.created_at.desc()).offset((page - 1) * size).limit(size).all()

    logs_data = []
    for log in logs:
        log_dict = {
            "log_id": log.log_id,
            "user_id": log.user_id,
            "username": log.user.username if log.user else None,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat()
        }
        logs_data.append(log_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "logs": logs_data
        }
    )

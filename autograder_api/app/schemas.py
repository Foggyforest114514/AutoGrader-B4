from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class ResponseModel(BaseModel):
    code: int = 200
    msg: str = "成功"
    data: Optional[Any] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    token: str
    refreshToken: str
    role: str
    userId: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=8)
    email: EmailStr
    real_name: str
    phone: Optional[str] = None
    role: UserRole
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None
    department: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None

class UserInfo(BaseModel):
    user_id: int
    username: str
    email: str
    real_name: str
    role: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeacherCreate(BaseModel):
    teacher_id: str
    real_name: str
    email: EmailStr
    department: Optional[str] = None
    initial_password: str

class CourseCreate(BaseModel):
    courseName: str
    courseCode: str
    semester: str
    description: Optional[str] = None

class CourseUpdate(BaseModel):
    courseName: Optional[str] = None
    description: Optional[str] = None

class CourseInfo(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    teacher_id: int
    semester: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassCreate(BaseModel):
    courseId: int
    className: str
    classCode: str

class ClassInfo(BaseModel):
    class_id: int
    course_id: int
    class_name: str
    class_code: str
    teacher_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentAddToClass(BaseModel):
    studentUserId: int

class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    classId: int
    question_id: str
    dueDate: datetime
    isPublished: bool = False
    allowResubmit: bool = True

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    dueDate: Optional[datetime] = None
    allowResubmit: Optional[bool] = None

class AssignmentInfo(BaseModel):
    assignment_id: int
    title: str
    description: Optional[str] = None
    class_id: int
    teacher_id: int
    due_date: datetime
    is_published: bool
    allow_resubmit: bool
    question_id: str
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    student_user_id: int
    question_id: str
    assignment_id: int
    code: str
    language: str = "python"

class SubmissionResultUpdate(BaseModel):
    status: SubmissionStatus
    overallScore: Optional[float] = None
    passedCount: Optional[int] = None
    totalCount: Optional[int] = None
    overallComment: Optional[str] = None
    staticIssues: Optional[List[Dict[str, Any]]] = None
    caseResults: Optional[List[Dict[str, Any]]] = None

class SubmissionInfo(BaseModel):
    submission_id: str
    student_user_id: int
    question_id: str
    assignment_id: int
    code: str
    language: str
    submitted_at: datetime
    status: str
    overall_score: Optional[float] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None
    overall_comment: Optional[str] = None
    static_issues: Optional[List[Dict[str, Any]]] = None
    case_results: Optional[List[Dict[str, Any]]] = None
    teacher_score_override: Optional[float] = None
    override_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class GradeInfo(BaseModel):
    student_id: str
    student_name: str
    assignment_id: int
    assignment_title: str
    score: Optional[float] = None
    submitted_at: Optional[datetime] = None
    status: str

class PasswordReset(BaseModel):
    email: EmailStr

class TokenRefresh(BaseModel):
    refreshToken: str

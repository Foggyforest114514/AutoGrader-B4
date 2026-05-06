from sqlalchemy import Column, BigInteger, String, Text, DateTime, Boolean, Enum, Float, JSON, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    real_name = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    courses = relationship("Course", back_populates="teacher")
    classes = relationship("Class", back_populates="teacher")
    assignments = relationship("Assignment", back_populates="teacher")
    submissions = relationship("Submission", back_populates="student")
    class_memberships = relationship("ClassStudent", back_populates="student")

class Student(Base):
    __tablename__ = "students"
    
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    first_password_changed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="student_profile")

class Teacher(Base):
    __tablename__ = "teachers"
    
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    teacher_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    
    user = relationship("User", back_populates="teacher_profile")

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(100), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    semester = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (UniqueConstraint('course_code', 'semester', name='uniq_course'),)
    
    teacher = relationship("User", back_populates="courses")
    classes = relationship("Class", back_populates="course")

class Class(Base):
    __tablename__ = "classes"
    
    class_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    class_code = Column(String(20), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (UniqueConstraint('course_id', 'class_code', name='uniq_class'),)
    
    course = relationship("Course", back_populates="classes")
    teacher = relationship("User", back_populates="classes")
    students = relationship("ClassStudent", back_populates="class_info")
    assignments = relationship("Assignment", back_populates="class_info")

class ClassStudent(Base):
    __tablename__ = "class_students"
    
    class_id = Column(BigInteger, ForeignKey('classes.class_id', ondelete='CASCADE'), primary_key=True)
    student_user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True, index=True)
    joined_at = Column(DateTime, server_default=func.now())
    
    class_info = relationship("Class", back_populates="students")
    student = relationship("User", back_populates="class_memberships")

class Assignment(Base):
    __tablename__ = "assignments"
    
    assignment_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    class_id = Column(BigInteger, ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False, index=True)
    teacher_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    due_date = Column(DateTime, nullable=False)
    is_published = Column(Boolean, default=False)
    allow_resubmit = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime, nullable=True)
    question_id = Column(String(50), nullable=False)
    
    teacher = relationship("User", back_populates="assignments")
    class_info = relationship("Class", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    
    submission_id = Column(String(64), primary_key=True)
    student_user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = Column(String(50), nullable=False, index=True)
    assignment_id = Column(BigInteger, ForeignKey('assignments.assignment_id', ondelete='CASCADE'), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(20), default='python')
    submitted_at = Column(DateTime, server_default=func.now())
    status = Column(Enum(SubmissionStatus), nullable=False, index=True)
    overall_score = Column(Float, nullable=True)
    passed_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    overall_comment = Column(Text, nullable=True)
    static_issues = Column(JSON, nullable=True)
    case_results = Column(JSON, nullable=True)
    teacher_score_override = Column(Float, nullable=True)
    override_reason = Column(Text, nullable=True)
    
    student = relationship("User", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")

class QuestionType(str, enum.Enum):
    COMMAND_LINE = "COMMAND_LINE"
    FILE_IO = "FILE_IO"
    INTERFACE = "INTERFACE"

class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Question(Base):
    __tablename__ = "questions"
    
    question_id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(QuestionType), nullable=False, index=True)
    difficulty = Column(Enum(Difficulty), nullable=False, index=True)
    language = Column(String(20), nullable=False, index=True)
    time_limit = Column(Integer, default=5)
    memory_limit = Column(Integer, default=256)
    starter_code = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(BigInteger, ForeignKey('users.user_id', ondelete='SET NULL'))
    
    test_cases = relationship("TestCase", back_populates="question")

class TestCase(Base):
    __tablename__ = "test_cases"
    
    test_case_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    question_id = Column(String(50), ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False, index=True)
    input = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)
    score_weight = Column(Float, default=1.0)
    
    question = relationship("Question", back_populates="test_cases")

class Announcement(Base):
    __tablename__ = "announcements"
    
    announcement_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(BigInteger, ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = Column(DateTime, server_default=func.now())

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    config_key = Column(String(100), primary_key=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), default="string")
    description = Column(String(500), nullable=True)

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User")

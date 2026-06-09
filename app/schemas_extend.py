from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    COMMAND_LINE = "COMMAND_LINE"
    FILE_IO = "FILE_IO"
    INTERFACE = "INTERFACE"

class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Language(str, Enum):
    PYTHON = "python"
    SHELL = "shell"

class TestCaseBase(BaseModel):
    input: str
    expected_output: str
    is_public: bool = False
    score_weight: float = 1.0

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseInfo(BaseModel):
    test_case_id: int
    question_id: str
    input: str
    expected_output: str
    is_public: bool
    score_weight: float

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: QuestionType
    difficulty: Difficulty
    language: Language
    time_limit: int = 5
    memory_limit: int = 256
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None

class QuestionCreate(QuestionBase):
    test_cases: List[TestCaseCreate] = []

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    starter_code: Optional[str] = None
    is_active: Optional[bool] = None

class QuestionInfo(BaseModel):
    question_id: str
    title: str
    description: Optional[str] = None
    type: str
    difficulty: str
    language: str
    time_limit: int
    memory_limit: int
    starter_code: Optional[str] = None
    is_active: bool
    created_at: datetime
    test_cases: Optional[List[TestCaseInfo]] = None

    class Config:
        from_attributes = True

class QuestionListItem(BaseModel):
    question_id: str
    title: str
    type: str
    difficulty: str
    language: str
    test_cases_count: int
    is_active: bool

    class Config:
        from_attributes = True

class AnnouncementBase(BaseModel):
    title: str
    content: str

class AnnouncementCreate(AnnouncementBase):
    course_id: Optional[int] = None

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class AnnouncementInfo(BaseModel):
    announcement_id: int
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    title: str
    content: str
    created_by: int
    creator_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class SystemConfigInfo(BaseModel):
    config_key: str
    config_value: str
    config_type: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_courses: int
    total_classes: int
    total_assignments: int
    total_submissions: int
    pending_submissions: int
    completed_submissions: int

class DatabaseHealth(BaseModel):
    status: str
    connection_count: int
    max_connections: int
    active_connections: int

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import uuid4
from app.database import get_db
from app.models.models import User, Question, TestCase, QuestionType, Difficulty
from app.schemas import ResponseModel
from app.schemas_extend import (
    QuestionCreate, QuestionUpdate, QuestionInfo, QuestionListItem,
    TestCaseCreate, TestCaseInfo
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/questions", tags=["题库管理"])


@router.get("", response_model=ResponseModel)
async def get_questions_list(
    type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Question)

    if current_user.role != "admin":
        query = query.filter(Question.is_active == True)

    if type:
        query = query.filter(Question.type == type)

    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    if language:
        query = query.filter(Question.language == language)

    if keyword:
        query = query.filter(Question.title.ilike(f"%{keyword}%"))

    total = query.count()
    questions = query.order_by(Question.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # 批量获取测试用例计数，避免 N+1
    question_ids = [q.question_id for q in questions]
    tc_counts = {}
    if question_ids:
        from sqlalchemy import func as sa_func
        rows = db.query(TestCase.question_id, sa_func.count(TestCase.test_case_id)).filter(
            TestCase.question_id.in_(question_ids)
        ).group_by(TestCase.question_id).all()
        tc_counts = {row[0]: row[1] for row in rows}

    questions_data = []
    for question in questions:
        questions_data.append({
            "question_id": question.question_id,
            "title": question.title,
            "type": question.type.value,
            "difficulty": question.difficulty.value,
            "language": question.language,
            "test_cases_count": tc_counts.get(question.question_id, 0),
            "is_active": question.is_active,
            "created_at": question.created_at.isoformat()
        })

    return ResponseModel(
        code=200,
        msg="成功",
        data={
            "total": total,
            "page": page,
            "size": size,
            "questions": questions_data
        }
    )


@router.post("", response_model=ResponseModel)
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以创建题目"
        )

    question_id = str(uuid4())[:8]

    new_question = Question(
        question_id=question_id,
        title=question_data.title,
        description=question_data.description,
        type=QuestionType(question_data.type),
        difficulty=Difficulty(question_data.difficulty),
        language=question_data.language,
        time_limit=question_data.time_limit,
        memory_limit=question_data.memory_limit,
        starter_code=question_data.starter_code,
        solution_code=question_data.solution_code,
        created_by=current_user.user_id
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    for tc_data in question_data.test_cases:
        new_test_case = TestCase(
            question_id=question_id,
            input=tc_data.input,
            expected_output=tc_data.expected_output,
            is_public=tc_data.is_public,
            score_weight=tc_data.score_weight
        )
        db.add(new_test_case)
    
    db.commit()

    return ResponseModel(
        code=200,
        msg="题目创建成功",
        data={"question_id": question_id}
    )


@router.get("/{question_id}", response_model=ResponseModel)
async def get_question_detail(
    question_id: str,
    include_test_cases: bool = Query(True),
    include_solution: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if not question.is_active and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="题目已禁用"
        )

    question_dict = {
        "question_id": question.question_id,
        "title": question.title,
        "description": question.description,
        "type": question.type.value,
        "difficulty": question.difficulty.value,
        "language": question.language,
        "time_limit": question.time_limit,
        "memory_limit": question.memory_limit,
        "starter_code": question.starter_code,
        "is_active": question.is_active,
        "created_at": question.created_at.isoformat()
    }

    if include_solution and current_user.role in ["teacher", "admin"]:
        question_dict["solution_code"] = question.solution_code

    if include_test_cases:
        test_cases = db.query(TestCase).filter(
            TestCase.question_id == question_id
        ).all()
        
        test_cases_data = []
        for tc in test_cases:
            tc_dict = {
                "test_case_id": tc.test_case_id,
                "input": tc.input,
                "expected_output": tc.expected_output,
                "is_public": tc.is_public,
                "score_weight": tc.score_weight
            }
            if not tc.is_public and current_user.role not in ["teacher", "admin"]:
                tc_dict["expected_output"] = "***"
            test_cases_data.append(tc_dict)
        
        question_dict["test_cases"] = test_cases_data

    return ResponseModel(
        code=200,
        msg="成功",
        data=question_dict
    )


@router.put("/{question_id}", response_model=ResponseModel)
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此题目"
        )

    if question_data.title:
        question.title = question_data.title
    
    if question_data.description is not None:
        question.description = question_data.description
    
    if question_data.time_limit:
        question.time_limit = question_data.time_limit
    
    if question_data.memory_limit:
        question.memory_limit = question_data.memory_limit
    
    if question_data.starter_code is not None:
        question.starter_code = question_data.starter_code
    
    if question_data.is_active is not None:
        question.is_active = question_data.is_active

    db.commit()
    db.refresh(question)

    return ResponseModel(
        code=200,
        msg="题目更新成功",
        data={"question_id": question.question_id}
    )


@router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此题目"
        )

    question.is_active = False
    db.commit()

    return ResponseModel(
        code=200,
        msg="题目已禁用"
    )


@router.post("/{question_id}/testcases", response_model=ResponseModel)
async def add_test_cases(
    question_id: str,
    test_cases: List[TestCaseCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限添加测试用例"
        )

    added_count = 0
    for tc_data in test_cases:
        new_test_case = TestCase(
            question_id=question_id,
            input=tc_data.input,
            expected_output=tc_data.expected_output,
            is_public=tc_data.is_public,
            score_weight=tc_data.score_weight
        )
        db.add(new_test_case)
        added_count += 1
    
    db.commit()

    return ResponseModel(
        code=200,
        msg="测试用例添加成功",
        data={"added_count": added_count}
    )


@router.get("/{question_id}/testcases", response_model=ResponseModel)
async def get_question_test_cases(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    test_cases = db.query(TestCase).filter(
        TestCase.question_id == question_id
    ).all()

    test_cases_data = []
    for tc in test_cases:
        tc_dict = {
            "test_case_id": tc.test_case_id,
            "input": tc.input,
            "expected_output": tc.expected_output,
            "is_public": tc.is_public,
            "score_weight": tc.score_weight
        }
        if not tc.is_public and current_user.role not in ["teacher", "admin"]:
            tc_dict["expected_output"] = "***"
        test_cases_data.append(tc_dict)

    return ResponseModel(
        code=200,
        msg="成功",
        data=test_cases_data
    )


@router.delete("/{question_id}/testcases/{test_case_id}", response_model=ResponseModel)
async def delete_test_case(
    question_id: str,
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除测试用例"
        )

    test_case = db.query(TestCase).filter(
        TestCase.test_case_id == test_case_id,
        TestCase.question_id == question_id
    ).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )

    db.delete(test_case)
    db.commit()

    return ResponseModel(
        code=200,
        msg="测试用例删除成功"
    )
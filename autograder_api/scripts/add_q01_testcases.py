import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text

e = create_engine(os.getenv('DATABASE_URL'))

with e.connect() as conn:
    # Delete old test cases for Q01 if any
    conn.execute(text("DELETE FROM test_cases WHERE question_id='Q01'"))

    # Add test case: send mail with correct subject format
    conn.execute(text("""
        INSERT INTO test_cases (question_id, input, expected_output, is_public, score_weight)
        VALUES ('Q01', NULL, 'echo "作业提交内容" | mail -s "20250001_第1次作业" linuxos_assignment@163.com', 1, 1.0)
    """))
    conn.commit()

    print("Q01 测试用例已添加")

    # Verify
    for tc in conn.execute(text("SELECT * FROM test_cases WHERE question_id='Q01'")).fetchall():
        print(tc._mapping)

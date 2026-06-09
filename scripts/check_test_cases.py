import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
e = create_engine(os.getenv('DATABASE_URL'))

with e.connect() as conn:
    print("=== test_cases 表结构 ===")
    for c in conn.execute(text("SHOW COLUMNS FROM test_cases")).fetchall():
        print(f"  {c[0]:25s} {c[1]}")

    print("\n=== Q01 测试用例 ===")
    for tc in conn.execute(text("SELECT * FROM test_cases WHERE question_id='Q01'")).fetchall():
        print(tc._mapping)

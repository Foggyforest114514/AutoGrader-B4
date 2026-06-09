import bcrypt

hash_from_db = "$2b$12$QUJ.5v81jw6b3RxZ6R8iSuBfabYjnbBbxtSKwk0DDhM6xTqX8qlbS"
password = "password123"

result = bcrypt.checkpw(password.encode('utf-8'), hash_from_db.encode('utf-8'))
print(f"bcrypt direct check: {result}")

new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"new hash generated: {new_hash[:60]}...")

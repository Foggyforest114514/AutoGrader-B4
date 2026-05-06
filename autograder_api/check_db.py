import pymysql

conn = pymysql.connect(
    host='mysql7.sqlpub.com', 
    port=3312, 
    user='ag_dev', 
    password='U2FuqkCFmVpjDBEN', 
    database='autograder'
)
cursor = conn.cursor()
cursor.execute("SELECT username, role, email FROM users LIMIT 10")
users = cursor.fetchall()
print("数据库中的用户列表:")
for user in users:
    print(f"  - 用户名: {user[0]}, 角色: {user[1]}, 邮箱: {user[2]}")

cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"\n用户总数: {count}")

conn.close()
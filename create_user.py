import os
import hashlib
from dotenv import load_dotenv
import pathlib
import sqlite3

# 加载项目根目录的.env文件
base_dir = pathlib.Path(__file__).parent
load_dotenv(base_dir / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# 密码哈希函数
def get_password_hash(password):
    """使用SHA256进行密码哈希"""
    # 截断密码到128字节
    password = password[:128]
    # 使用SECRET_KEY作为盐
    salted_password = password + SECRET_KEY
    return hashlib.sha256(salted_password.encode()).hexdigest()

# 连接数据库
conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 创建新用户
username = "testuser2"
email = "test2@example.com"
password = "123456"
hashed_password = get_password_hash(password)

# 插入新用户
cursor.execute('''
    INSERT INTO users (username, email, password_hash, created_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
''', (username, email, hashed_password))

conn.commit()
print(f"Created user: {username} with email: {email}")
print(f"Password: {password}")
print(f"Hashed password: {hashed_password}")

# 验证用户是否创建成功
cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
user = cursor.fetchone()
if user:
    print(f"User created successfully: {user}")
else:
    print("Failed to create user")

conn.close()

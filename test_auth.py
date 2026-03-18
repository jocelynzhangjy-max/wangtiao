import os
import hashlib
from dotenv import load_dotenv
import pathlib
import sqlite3

# 加载项目根目录的.env文件
base_dir = pathlib.Path(__file__).parent
load_dotenv(base_dir / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

print(f"SECRET_KEY: {SECRET_KEY}")
print(f"SECRET_KEY length: {len(SECRET_KEY)}")

# 测试密码哈希
def get_password_hash(password):
    """使用SHA256进行密码哈希"""
    # 截断密码到128字节
    password = password[:128]
    # 使用SECRET_KEY作为盐
    salted_password = password + SECRET_KEY
    print(f"Salted password: {salted_password}")
    print(f"Salted password length: {len(salted_password)}")
    return hashlib.sha256(salted_password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """验证密码"""
    # 截断密码到128字节
    plain_password = plain_password[:128]
    # 使用SECRET_KEY作为盐
    salted_password = plain_password + SECRET_KEY
    return hashlib.sha256(salted_password.encode()).hexdigest() == hashed_password

# 测试密码
password = "123456"
hashed = get_password_hash(password)
print(f"Password: {password}")
print(f"Hashed: {hashed}")
print(f"Hashed length: {len(hashed)}")

# 连接数据库查看用户信息
conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, email, password_hash FROM users')
users = cursor.fetchall()

print("\nDatabase users:")
for user in users:
    user_id, username, email, db_hash = user
    print(f"User ID: {user_id}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"DB Hash: {db_hash}")
    print(f"Verification result: {verify_password(password, db_hash)}")
    print(f"Hash match: {hashed == db_hash}")
    print()

conn.close()

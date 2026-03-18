import os
import hashlib
from dotenv import load_dotenv
import pathlib

# 加载项目根目录的.env文件
base_dir = pathlib.Path(__file__).parent
load_dotenv(base_dir / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

print(f"SECRET_KEY: {SECRET_KEY}")

# 测试密码哈希
def get_password_hash(password):
    """使用SHA256进行密码哈希"""
    # 截断密码到128字节
    password = password[:128]
    # 使用SECRET_KEY作为盐
    salted_password = password + SECRET_KEY
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

# 验证数据库中的密码哈希
db_hash = "0b8c070135a1797c45ef88bdcb97107905c12432ce864fde8d551603cdb98b97"
print(f"DB Hash: {db_hash}")
print(f"Verification result: {verify_password(password, db_hash)}")

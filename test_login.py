import os
import hashlib
from dotenv import load_dotenv
import pathlib
import sqlite3

# 加载项目根目录的.env文件
base_dir = pathlib.Path(__file__).parent
load_dotenv(base_dir / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-authentication")
print(f"SECRET_KEY: {SECRET_KEY}")

# 密码哈希函数
def get_password_hash(password):
    """使用SHA256进行密码哈希"""
    password = password[:128]
    salted_password = password + SECRET_KEY
    return hashlib.sha256(salted_password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """验证密码"""
    plain_password = plain_password[:128]
    salted_password = plain_password + SECRET_KEY
    computed_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    print(f"  Input password: {plain_password}")
    print(f"  Computed hash: {computed_hash}")
    print(f"  Stored hash: {hashed_password}")
    print(f"  Match: {computed_hash == hashed_password}")
    return computed_hash == hashed_password

# 连接数据库
conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 获取最近注册的用户
cursor.execute('SELECT id, username, email, password_hash FROM users ORDER BY id DESC LIMIT 1')
user = cursor.fetchone()

if user:
    user_id, username, email, db_hash = user
    print(f"\nTesting user: {username} ({email})")
    print(f"Stored hash: {db_hash}")
    
    # 测试常见密码
    test_passwords = ['123456', 'password', 'admin', '123456789', 'test']
    
    for pwd in test_passwords:
        print(f"\nTrying password: '{pwd}'")
        if verify_password(pwd, db_hash):
            print(f"  ✓ SUCCESS! Password is: {pwd}")
            break
    else:
        print("\n✗ None of the test passwords matched")
        
    # 计算新哈希对比
    print(f"\nGenerating hash for '123456':")
    new_hash = get_password_hash('123456')
    print(f"  New hash: {new_hash}")
    print(f"  Matches DB: {new_hash == db_hash}")

conn.close()

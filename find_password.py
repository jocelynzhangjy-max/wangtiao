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
def verify_password(plain_password, hashed_password):
    """验证密码"""
    plain_password = plain_password[:128]
    salted_password = plain_password + SECRET_KEY
    computed_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    return computed_hash == hashed_password

# 连接数据库
conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 获取特定用户
target_email = '1057438016@qq.com'
cursor.execute('SELECT id, username, email, password_hash FROM users WHERE email = ?', (target_email,))
user = cursor.fetchone()

if user:
    user_id, username, email, db_hash = user
    print(f"\nTesting user: {username} ({email})")
    print(f"Stored hash: {db_hash}")
    
    # 测试常见密码
    test_passwords = ['123456', 'password', 'admin', '123456789', 'test', 'jocelyn', 'Jocelyn', '1057438016', 'qq123456', '123456qq']
    
    found = False
    for pwd in test_passwords:
        if verify_password(pwd, db_hash):
            print(f"\n✓ SUCCESS! Password is: '{pwd}'")
            found = True
            break
    
    if not found:
        print("\n✗ None of the common passwords matched")
        print("\nTrying more passwords...")
        # 尝试更多组合
        more_passwords = ['12345678', '1234567890', 'qwerty', 'abc123', 'password123', 'iloveyou', 'welcome', 'monkey', 'dragon', 'master']
        for pwd in more_passwords:
            if verify_password(pwd, db_hash):
                print(f"\n✓ SUCCESS! Password is: '{pwd}'")
                found = True
                break
        
        if not found:
            print("\n✗ Still no match. The password is not in the common list.")

conn.close()

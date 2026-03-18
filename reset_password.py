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

# 连接数据库
conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 重置特定用户的密码
target_email = '1057438016@qq.com'
new_password = '123456'
new_hash = get_password_hash(new_password)

print(f"\nResetting password for: {target_email}")
print(f"New password: {new_password}")
print(f"New hash: {new_hash}")

# 更新密码
cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (new_hash, target_email))
conn.commit()

if cursor.rowcount > 0:
    print(f"✓ Password reset successful for {target_email}")
else:
    print(f"✗ User not found: {target_email}")

conn.close()

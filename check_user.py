import sqlite3

conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 查询所有用户
print("All users:")
cursor.execute("SELECT id, username, email, password_hash FROM users")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
    print(f"  Hash: {row[3][:50]}...")
    print()

# 查询特定用户
print("\nSearching for 1057438016@qq.com:")
cursor.execute("SELECT * FROM users WHERE email = ?", ('1057438016@qq.com',))
user = cursor.fetchone()
if user:
    print(f"Found: {user}")
else:
    print("Not found")

conn.close()

import sqlite3

conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 查看所有用户
print("All users:")
cursor.execute("SELECT id, username, email FROM users")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")

conn.close()

import sqlite3

conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 查看agents表结构
print("Agents table schema:")
cursor.execute("PRAGMA table_info(agents)")
for row in cursor.fetchall():
    print(f"  {row}")

# 查看users表结构
print("\nUsers table schema:")
cursor.execute("PRAGMA table_info(users)")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()

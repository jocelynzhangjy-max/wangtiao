import os
import sqlite3

# 关闭所有数据库连接
import gc
gc.collect()

db_path = 'agentgateway.db'

# 尝试删除数据库文件
try:
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted {db_path}")
    else:
        print(f"{db_path} does not exist")
except Exception as e:
    print(f"Error deleting database: {e}")
    print("Trying to create new tables anyway...")

# 重新创建数据库表
from backend.database import engine, Base
from backend.models import User, Agent, Tool, Conversation, Message

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")

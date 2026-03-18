import sqlite3

conn = sqlite3.connect('agentgateway.db')
cursor = conn.cursor()

# 添加缺失的列到agents表
columns_to_add = [
    ("sandbox_id", "VARCHAR(100)"),
    ("sandbox_status", "VARCHAR(20)"),
    ("sandbox_config", "JSON"),
    ("identity_token", "VARCHAR(500)"),
    ("identity_tags", "JSON"),
    ("last_identity_refresh", "DATETIME"),
    ("collaboration_mode", "VARCHAR(50)"),
    ("team_id", "VARCHAR(100)"),
    ("role", "VARCHAR(100)"),
    ("trust_level", "INTEGER"),
    ("collaboration_history", "JSON"),
    ("shared_resources", "JSON"),
    ("status", "VARCHAR(20)"),
    ("last_activity", "DATETIME"),
    ("reputation_score", "FLOAT"),
    ("reputation_history", "JSON"),
    ("behavior_analysis", "JSON"),
    ("risk_level", "VARCHAR(20)")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE agents ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column already exists: {col_name}")
        else:
            print(f"Error adding column {col_name}: {e}")

conn.commit()
conn.close()
print("\nMigration completed!")

from backend.database import engine, Base
from backend.models import User, Agent, Tool, Conversation, Message

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")

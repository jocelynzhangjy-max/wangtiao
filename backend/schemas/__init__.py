from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Agent schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: str
    model_id: str
    config_json: Optional[Dict[str, Any]] = {}

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    model_id: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None

class Agent(AgentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    title: str
    agent_id: int

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Tool schemas
class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    config_json: Optional[Dict[str, Any]] = {}

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None

class Tool(ToolBase):
    id: int
    
    class Config:
        from_attributes = True

# AgentTool schemas
class AgentToolBase(BaseModel):
    agent_id: int
    tool_id: int
    config_json: Optional[Dict[str, Any]] = {}

class AgentToolCreate(AgentToolBase):
    pass

class AgentTool(AgentToolBase):
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

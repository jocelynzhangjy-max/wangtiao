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

# 影子网络系统schemas
class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource_type: str
    resource_pattern: str
    action: str
    enable_intent_audit: Optional[bool] = True
    risk_threshold: Optional[str] = "medium"
    is_active: Optional[bool] = True
    priority: Optional[int] = 100

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_pattern: Optional[str] = None
    action: Optional[str] = None
    enable_intent_audit: Optional[bool] = None
    risk_threshold: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class Policy(PolicyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NetworkRequestBase(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = {}
    body: Optional[str] = None

class NetworkRequestCreate(NetworkRequestBase):
    agent_id: int

class NetworkRequest(NetworkRequestBase):
    id: int
    agent_id: int
    status_code: Optional[int] = None
    response_headers: Optional[Dict[str, Any]] = {}
    response_body: Optional[str] = None
    intent_analysis: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    policy_action: Optional[str] = None
    policy_id: Optional[int] = None
    blocked_reason: Optional[str] = None
    request_time: datetime
    response_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    log_type: str
    event: str
    details: Optional[Dict[str, Any]] = {}
    description: Optional[str] = None
    risk_level: Optional[str] = "low"
    is_alert: Optional[bool] = False

class AuditLogCreate(AuditLogBase):
    user_id: int
    agent_id: Optional[int] = None

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    alert_type: str
    severity: str
    status: Optional[str] = "open"
    related_request_id: Optional[int] = None
    evidence: Optional[Dict[str, Any]] = {}

class AlertCreate(AlertBase):
    agent_id: Optional[int] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None

class Alert(AlertBase):
    id: int
    agent_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SandboxBase(BaseModel):
    agent_id: int
    container_name: Optional[str] = None
    cpu_limit: Optional[str] = "1.0"
    memory_limit: Optional[str] = "512m"

class SandboxCreate(SandboxBase):
    pass

class Sandbox(SandboxBase):
    id: int
    container_id: Optional[str] = None
    network_namespace: Optional[str] = None
    ip_address: Optional[str] = None
    network_rules: Optional[List[Dict[str, Any]]] = []
    status: str
    status_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 仪表盘统计数据
class DashboardStats(BaseModel):
    agents: Dict[str, int]
    policies: int
    active_alerts: int
    gateway: Dict[str, int]

# 信誉系统schemas
class ReputationScore(BaseModel):
    agent_id: int
    agent_name: str
    total_score: float
    security_score: float
    collaboration_score: float
    resource_score: float
    response_score: float
    consistency_score: float
    last_updated: str

class BehaviorReport(BaseModel):
    agent_id: int
    agent_name: str
    report_period: str
    total_requests: int
    total_logs: int
    total_alerts: int
    behavior_patterns: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]

class ReputationSummary(BaseModel):
    user_id: int
    total_agents: int
    average_reputation_score: float
    top_performers: List[ReputationScore]
    low_performers: List[ReputationScore]
    last_updated: str

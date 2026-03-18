from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Boolean, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

# 策略动作枚举
class PolicyAction(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"
    QUARANTINE = "quarantine"

# 风险等级枚举
class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# 沙箱状态枚举
class SandboxStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    agents = relationship("Agent", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    policies = relationship("Policy", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    agent_type = Column(String(50), nullable=False)  # OpenAI, Anthropic, etc.
    model_id = Column(String(100), nullable=False)
    config_json = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 沙箱相关
    sandbox_id = Column(String(100), unique=True, index=True)
    sandbox_status = Column(Enum(SandboxStatus), default=SandboxStatus.PENDING)
    sandbox_config = Column(JSON, default={})
    
    # 动态身份标签
    identity_token = Column(String(500))
    identity_tags = Column(JSON, default=[])
    last_identity_refresh = Column(DateTime(timezone=True))
    
    # 协作相关字段
    collaboration_mode = Column(String(50), default="independent")  # independent, collaborative, leader, follower
    team_id = Column(String(100), index=True)  # 团队标识
    role = Column(String(100))  # 智能体角色
    trust_level = Column(Integer, default=50)  # 信任等级 0-100
    collaboration_history = Column(JSON, default=[])  # 协作历史
    shared_resources = Column(JSON, default=[])  # 共享资源
    
    # 智能体状态
    status = Column(String(20), default="active")  # active, idle, busy, error
    last_activity = Column(DateTime(timezone=True))
    
    # 信誉系统相关
    reputation_score = Column(Float, default=50.0)  # 信誉评分 0-100
    reputation_history = Column(JSON, default=[])  # 信誉历史记录
    behavior_analysis = Column(JSON, default={})  # 行为分析数据
    risk_level = Column(String(20), default="medium")  # 风险等级: low, medium, high
    
    # 关系
    user = relationship("User", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent")
    agent_tools = relationship("AgentTool", back_populates="agent")
    network_requests = relationship("NetworkRequest", back_populates="agent")
    audit_logs = relationship("AuditLog", back_populates="agent")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, tool
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")

class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    type = Column(String(20), nullable=False)  # builtin, custom
    config_json = Column(JSON, default={})
    
    # 关系
    agent_tools = relationship("AgentTool", back_populates="tool")

class AgentTool(Base):
    __tablename__ = "agent_tools"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), primary_key=True)
    config_json = Column(JSON, default={})
    
    # 关系
    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")

# ========== 影子网络系统新增模型 ==========

class Policy(Base):
    """动态策略控制规则"""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 策略条件
    resource_type = Column(String(50), nullable=False)  # api, database, file, network
    resource_pattern = Column(String(500), nullable=False)  # 正则表达式或URL模式
    action = Column(Enum(PolicyAction), nullable=False)
    
    # 意图审计配置
    enable_intent_audit = Column(Boolean, default=True)
    intent_rules = Column(JSON, default=[])  # 意图规则列表
    
    # 风险阈值
    risk_threshold = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    
    # 状态
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)  # 优先级，数字越小优先级越高
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="policies")

class NetworkRequest(Base):
    """网络请求记录"""
    __tablename__ = "network_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # 请求信息
    method = Column(String(10), nullable=False)
    url = Column(String(2000), nullable=False)
    headers = Column(JSON, default={})
    body = Column(Text)
    
    # 响应信息
    status_code = Column(Integer)
    response_headers = Column(JSON, default={})
    response_body = Column(Text)
    
    # 审计结果
    intent_analysis = Column(Text)  # LLM意图分析结果
    risk_level = Column(Enum(RiskLevel))
    risk_score = Column(Integer)  # 0-100
    
    # 策略执行结果
    policy_action = Column(Enum(PolicyAction))
    policy_id = Column(Integer, ForeignKey("policies.id"))
    blocked_reason = Column(Text)
    
    # 时间戳
    request_time = Column(DateTime(timezone=True), server_default=func.now())
    response_time = Column(DateTime(timezone=True))
    
    # 关系
    agent = relationship("Agent", back_populates="network_requests")

class AuditLog(Base):
    """审计日志"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # 日志类型
    log_type = Column(String(50), nullable=False)  # network, policy, identity, system
    event = Column(String(100), nullable=False)
    
    # 详细信息
    details = Column(JSON, default={})
    description = Column(Text)
    
    # 风险信息
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    is_alert = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="audit_logs")
    agent = relationship("Agent", back_populates="audit_logs")

class Alert(Base):
    """告警记录"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # 告警信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    alert_type = Column(String(50), nullable=False)  # anomaly, policy_violation, security
    severity = Column(Enum(RiskLevel), nullable=False)
    
    # 状态
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    
    # 相关数据
    related_request_id = Column(Integer, ForeignKey("network_requests.id"))
    evidence = Column(JSON, default={})
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

class Sandbox(Base):
    """沙箱实例管理"""
    __tablename__ = "sandboxes"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, unique=True)
    
    # 容器信息
    container_id = Column(String(100), unique=True)
    container_name = Column(String(100))
    network_namespace = Column(String(100))
    
    # 网络配置
    ip_address = Column(String(50))
    network_rules = Column(JSON, default=[])
    
    # 资源限制
    cpu_limit = Column(String(20), default="1.0")
    memory_limit = Column(String(20), default="512m")
    
    # 状态
    status = Column(Enum(SandboxStatus), default=SandboxStatus.PENDING)
    status_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    stopped_at = Column(DateTime(timezone=True))

class AgentTeam(Base):
    """智能体团队管理"""
    __tablename__ = "agent_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 团队配置
    collaboration_policy = Column(JSON, default={})
    security_level = Column(String(20), default="medium")  # low, medium, high
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User")

class TeamMember(Base):
    """团队成员管理"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(100), ForeignKey("agent_teams.team_id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    role = Column(String(100), nullable=False)  # leader, member, observer
    permissions = Column(JSON, default={})  # 权限配置
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    agent = relationship("Agent")
    team = relationship("AgentTeam")

# SDN模型
class SDNTopology(Base):
    __tablename__ = "sdn_topologies"
    
    id = Column(Integer, primary_key=True, index=True)
    topology_id = Column(String(100), unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="active")  # active, inactive, maintenance
    topology_data = Column(JSON, default={
        "switches": [],
        "links": [],
        "hosts": []
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="sdn_topologies")
    links = relationship("SDNLink", back_populates="topology", cascade="all, delete-orphan")
    flows = relationship("SDNFlow", back_populates="topology", cascade="all, delete-orphan")

class SDNLink(Base):
    __tablename__ = "sdn_links"
    
    id = Column(Integer, primary_key=True, index=True)
    topology_id = Column(String(100), ForeignKey("sdn_topologies.topology_id"), nullable=False)
    source_switch = Column(String(100), nullable=False)
    destination_switch = Column(String(100), nullable=False)
    bandwidth = Column(Integer, default=1000)  # 带宽（Mbps）
    status = Column(String(20), default="active")  # active, down, maintenance
    latency = Column(Float, default=0.1)  # 延迟（毫秒）
    utilization = Column(Float, default=0.0)  # 利用率（0-1）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    topology = relationship("SDNTopology", back_populates="links")

class SDNFlow(Base):
    __tablename__ = "sdn_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    topology_id = Column(String(100), ForeignKey("sdn_topologies.topology_id"), nullable=False)
    switch_id = Column(String(100), nullable=False)
    priority = Column(Integer, default=100)
    match = Column(JSON, default={})
    actions = Column(JSON, default=[])
    status = Column(String(20), default="active")  # active, inactive, expired
    timeout = Column(Integer, default=300)  # 超时时间（秒）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    topology = relationship("SDNTopology", back_populates="flows")

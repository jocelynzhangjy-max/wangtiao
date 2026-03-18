"""
影子网络系统API路由
提供沙箱管理、策略控制、审计日志和告警管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..auth.auth import get_current_active_user
from ..models import (
    User, Agent, Policy, NetworkRequest, AuditLog, Alert,
    Sandbox, PolicyAction, RiskLevel
)
from ..core.sandbox import sandbox_manager
from ..core.policy_engine import policy_engine
from ..core.gateway import agent_gateway
from ..core.alert_system import alert_system
from ..core.identity_manager import identity_manager

router = APIRouter()

# ========== 请求/响应模型 ==========

class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    resource_type: str
    resource_pattern: str
    action: str
    enable_intent_audit: bool = True
    intent_rules: Optional[list] = None
    risk_threshold: str = "medium"
    priority: int = 100

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_pattern: Optional[str] = None
    action: Optional[str] = None
    enable_intent_audit: Optional[bool] = None
    intent_rules: Optional[list] = None
    risk_threshold: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class NetworkRuleCreate(BaseModel):
    type: str  # allow, deny
    dst: str
    port: str
    protocol: str = "tcp"

class ProxyRequest(BaseModel):
    method: str
    url: str
    headers: Optional[dict] = {}
    body: Optional[str] = None
    original_task: Optional[str] = None

# ========== 沙箱管理API ==========

@router.post("/agents/{agent_id}/sandbox", response_model=dict)
async def create_agent_sandbox(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """为Agent创建沙箱环境"""
    # 检查权限
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # 检查是否已有沙箱
    existing = db.query(Sandbox).filter(Sandbox.agent_id == agent_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sandbox already exists for this agent"
        )
    
    # 创建沙箱
    sandbox = sandbox_manager.create_sandbox(agent_id, db)
    
    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sandbox"
        )
    
    return {
        "id": sandbox.id,
        "agent_id": sandbox.agent_id,
        "container_name": sandbox.container_name,
        "status": sandbox.status.value,
        "message": sandbox.status_message
    }

@router.get("/agents/{agent_id}/sandbox", response_model=dict)
async def get_agent_sandbox(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取Agent的沙箱状态"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    sandbox = db.query(Sandbox).filter(Sandbox.agent_id == agent_id).first()
    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sandbox not found"
        )
    
    status_info = sandbox_manager.get_sandbox_status(sandbox.id, db)
    return status_info

@router.post("/agents/{agent_id}/sandbox/rules")
async def add_sandbox_rule(
    agent_id: int,
    rule: NetworkRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """添加沙箱网络规则"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    sandbox = db.query(Sandbox).filter(Sandbox.agent_id == agent_id).first()
    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sandbox not found"
        )
    
    success = sandbox_manager.add_network_rule(
        sandbox.id,
        rule.dict(),
        db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add network rule"
        )
    
    return {"message": "Network rule added successfully"}

@router.delete("/agents/{agent_id}/sandbox")
async def delete_agent_sandbox(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除Agent的沙箱"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    sandbox = db.query(Sandbox).filter(Sandbox.agent_id == agent_id).first()
    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sandbox not found"
        )
    
    success = sandbox_manager.delete_sandbox(sandbox.id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sandbox"
        )
    
    return {"message": "Sandbox deleted successfully"}

# ========== 策略管理API ==========

@router.get("/policies", response_model=list)
async def list_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的所有策略"""
    policies = db.query(Policy).filter(Policy.user_id == current_user.id).all()
    return [{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "resource_type": p.resource_type,
        "resource_pattern": p.resource_pattern,
        "action": p.action.value,
        "enable_intent_audit": p.enable_intent_audit,
        "risk_threshold": p.risk_threshold.value if p.risk_threshold else None,
        "is_active": p.is_active,
        "priority": p.priority,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in policies]

@router.post("/policies")
async def create_policy(
    policy: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新策略"""
    # 验证action
    try:
        action = PolicyAction(policy.action)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {policy.action}"
        )
    
    # 验证risk_threshold
    try:
        risk_threshold = RiskLevel(policy.risk_threshold)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk_threshold: {policy.risk_threshold}"
        )
    
    new_policy = Policy(
        user_id=current_user.id,
        name=policy.name,
        description=policy.description,
        resource_type=policy.resource_type,
        resource_pattern=policy.resource_pattern,
        action=action,
        enable_intent_audit=policy.enable_intent_audit,
        intent_rules=policy.intent_rules or [],
        risk_threshold=risk_threshold,
        priority=policy.priority
    )
    
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    
    # 刷新策略缓存
    policy_engine.reload_policies(db)
    
    return {
        "id": new_policy.id,
        "name": new_policy.name,
        "message": "Policy created successfully"
    }

@router.put("/policies/{policy_id}")
async def update_policy(
    policy_id: int,
    policy_update: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新策略"""
    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.user_id == current_user.id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # 更新字段
    update_data = policy_update.dict(exclude_unset=True)
    
    if "action" in update_data:
        try:
            update_data["action"] = PolicyAction(update_data["action"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {update_data['action']}"
            )
    
    if "risk_threshold" in update_data:
        try:
            update_data["risk_threshold"] = RiskLevel(update_data["risk_threshold"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk_threshold: {update_data['risk_threshold']}"
            )
    
    for field, value in update_data.items():
        setattr(policy, field, value)
    
    db.commit()
    db.refresh(policy)
    
    # 刷新策略缓存
    policy_engine.reload_policies(db)
    
    return {"message": "Policy updated successfully"}

@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除策略"""
    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.user_id == current_user.id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    db.delete(policy)
    db.commit()
    
    # 刷新策略缓存
    policy_engine.reload_policies(db)
    
    return {"message": "Policy deleted successfully"}

@router.post("/policies/initialize-defaults")
async def initialize_default_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """初始化默认策略"""
    policy_engine.create_default_policies(current_user.id, db)
    return {"message": "Default policies created successfully"}

# ========== 代理请求API ==========

@router.post("/agents/{agent_id}/proxy")
async def proxy_agent_request(
    agent_id: int,
    request: ProxyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """代理Agent的网络请求（经过策略控制和审计）"""
    # 检查权限
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # 获取身份令牌
    identity_token = agent.identity_token
    
    # 处理请求
    allowed, response_data, message = await agent_gateway.process_request(
        agent_id=agent_id,
        method=request.method,
        url=request.url,
        headers=request.headers,
        body=request.body,
        db=db,
        original_task=request.original_task,
        identity_token=identity_token
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": message,
                "data": response_data
            }
        )
    
    return {
        "allowed": True,
        "message": message,
        "data": response_data
    }

# ========== 审计日志API ==========

@router.get("/audit-logs")
async def list_audit_logs(
    agent_id: Optional[int] = None,
    log_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取审计日志"""
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)
    
    if agent_id:
        query = query.filter(AuditLog.agent_id == agent_id)
    
    if log_type:
        query = query.filter(AuditLog.log_type == log_type)
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return [{
        "id": log.id,
        "agent_id": log.agent_id,
        "log_type": log.log_type,
        "event": log.event,
        "details": log.details,
        "description": log.description,
        "risk_level": log.risk_level.value if log.risk_level else None,
        "is_alert": log.is_alert,
        "created_at": log.created_at.isoformat() if log.created_at else None
    } for log in logs]

@router.get("/network-requests")
async def list_network_requests(
    agent_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取网络请求记录"""
    query = db.query(NetworkRequest).join(Agent).filter(Agent.user_id == current_user.id)
    
    if agent_id:
        query = query.filter(NetworkRequest.agent_id == agent_id)
    
    requests = query.order_by(NetworkRequest.request_time.desc()).limit(limit).all()
    
    return [{
        "id": req.id,
        "agent_id": req.agent_id,
        "method": req.method,
        "url": req.url,
        "intent_analysis": req.intent_analysis,
        "risk_level": req.risk_level.value if req.risk_level else None,
        "risk_score": req.risk_score,
        "policy_action": req.policy_action.value if req.policy_action else None,
        "blocked_reason": req.blocked_reason,
        "request_time": req.request_time.isoformat() if req.request_time else None
    } for req in requests]

# ========== 告警管理API ==========

@router.get("/alerts")
async def list_alerts(
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取告警列表"""
    # 获取用户的所有Agent的告警
    user_agent_ids = db.query(Agent.id).filter(Agent.user_id == current_user.id).subquery()
    
    query = db.query(Alert).filter(Alert.agent_id.in_(user_agent_ids))
    
    if agent_id:
        query = query.filter(Alert.agent_id == agent_id)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    return [{
        "id": alert.id,
        "agent_id": alert.agent_id,
        "title": alert.title,
        "description": alert.description,
        "alert_type": alert.alert_type,
        "severity": alert.severity.value if alert.severity else None,
        "status": alert.status,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "evidence": alert.evidence
    } for alert in alerts]

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """确认告警"""
    # 检查权限
    alert = db.query(Alert).join(Agent).filter(
        Alert.id == alert_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    success = alert_system.acknowledge_alert(alert_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )
    
    return {"message": "Alert acknowledged"}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """解决告警"""
    alert = db.query(Alert).join(Agent).filter(
        Alert.id == alert_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    success = alert_system.resolve_alert(alert_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert"
        )
    
    return {"message": "Alert resolved"}

@router.get("/alerts/statistics")
async def get_alert_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取告警统计"""
    return alert_system.get_alert_statistics(db)

# ========== 仪表盘API ==========

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取仪表盘统计数据"""
    # 获取用户的Agent数量
    agent_count = db.query(Agent).filter(Agent.user_id == current_user.id).count()
    
    # 获取运行中的沙箱数量
    sandbox_count = db.query(Sandbox).join(Agent).filter(
        Agent.user_id == current_user.id,
        Sandbox.status == "running"
    ).count()
    
    # 获取策略数量
    policy_count = db.query(Policy).filter(Policy.user_id == current_user.id).count()
    
    # 获取活动告警数量
    user_agent_ids = db.query(Agent.id).filter(Agent.user_id == current_user.id).subquery()
    alert_count = db.query(Alert).filter(
        Alert.agent_id.in_(user_agent_ids),
        Alert.status.in_(["open", "acknowledged"])
    ).count()
    
    # 获取网关统计
    gateway_stats = agent_gateway.get_statistics()
    
    return {
        "agents": {
            "total": agent_count,
            "with_sandbox": sandbox_count
        },
        "policies": policy_count,
        "active_alerts": alert_count,
        "gateway": gateway_stats
    }

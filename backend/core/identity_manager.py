"""
身份联动系统
结合JWT或OAuth2，为智能体的每一次网络调用赋予动态身份标签
"""
import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from backend.models import Agent, AuditLog, RiskLevel
from backend.database import get_db

logger = logging.getLogger(__name__)

class IdentityManager:
    """身份管理器"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expire_minutes = 30
        self.identity_refresh_interval = timedelta(minutes=15)
    
    def generate_identity_token(
        self,
        agent_id: int,
        user_id: int,
        session_context: Optional[Dict] = None
    ) -> str:
        """
        生成动态身份令牌
        """
        # 生成唯一会话ID
        session_id = str(uuid.uuid4())
        
        # 创建时间戳
        now = datetime.utcnow()
        
        # 生成动态身份标签
        identity_tags = self._generate_identity_tags(
            agent_id, 
            user_id, 
            session_context
        )
        
        # 构建令牌载荷
        payload = {
            "sub": str(agent_id),  # Agent ID
            "uid": str(user_id),   # User ID
            "sid": session_id,     # Session ID
            "tags": identity_tags, # 动态身份标签
            "ctx": session_context or {},  # 会话上下文
            "iat": now,            # 签发时间
            "exp": now + timedelta(minutes=self.token_expire_minutes),  # 过期时间
            "jti": str(uuid.uuid4())  # JWT ID (唯一标识)
        }
        
        # 生成令牌
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Generated identity token for agent {agent_id}, session {session_id}")
        
        return token
    
    def _generate_identity_tags(
        self,
        agent_id: int,
        user_id: int,
        session_context: Optional[Dict]
    ) -> List[Dict]:
        """
        生成动态身份标签
        """
        tags = []
        
        # 基础身份标签
        tags.append({
            "type": "agent",
            "key": "agent_id",
            "value": str(agent_id),
            "confidence": 1.0
        })
        
        tags.append({
            "type": "user",
            "key": "user_id",
            "value": str(user_id),
            "confidence": 1.0
        })
        
        # 时间上下文标签
        now = datetime.utcnow()
        tags.append({
            "type": "temporal",
            "key": "hour_of_day",
            "value": now.hour,
            "confidence": 1.0
        })
        
        tags.append({
            "type": "temporal",
            "key": "day_of_week",
            "value": now.weekday(),
            "confidence": 1.0
        })
        
        # 会话上下文标签
        if session_context:
            # 任务类型标签
            if "task_type" in session_context:
                tags.append({
                    "type": "context",
                    "key": "task_type",
                    "value": session_context["task_type"],
                    "confidence": 0.9
                })
            
            # 数据源标签
            if "data_source" in session_context:
                tags.append({
                    "type": "context",
                    "key": "data_source",
                    "value": session_context["data_source"],
                    "confidence": 0.85
                })
            
            # 安全级别标签
            if "security_level" in session_context:
                tags.append({
                    "type": "security",
                    "key": "security_level",
                    "value": session_context["security_level"],
                    "confidence": 1.0
                })
            
            # 访问范围标签
            if "access_scope" in session_context:
                tags.append({
                    "type": "security",
                    "key": "access_scope",
                    "value": session_context["access_scope"],
                    "confidence": 0.95
                })
        
        # 行为模式标签（基于历史行为分析）
        behavior_tags = self._analyze_behavior_pattern(agent_id)
        tags.extend(behavior_tags)
        
        # 风险评级标签
        risk_assessment = self._assess_risk_level(tags)
        tags.append({
            "type": "risk",
            "key": "risk_level",
            "value": risk_assessment["level"],
            "confidence": risk_assessment["confidence"],
            "score": risk_assessment["score"]
        })
        
        return tags
    
    def _analyze_behavior_pattern(self, agent_id: int) -> List[Dict]:
        """
        分析Agent的行为模式
        """
        # 这里可以集成更复杂的行为分析算法
        # 目前返回基础的行为标签
        return [
            {
                "type": "behavior",
                "key": "pattern_type",
                "value": "normal",  # normal, suspicious, anomalous
                "confidence": 0.8
            }
        ]
    
    def _assess_risk_level(self, tags: List[Dict]) -> Dict:
        """
        基于身份标签评估风险等级
        """
        score = 0
        
        # 检查安全级别
        security_tags = [t for t in tags if t["type"] == "security"]
        for tag in security_tags:
            if tag["key"] == "security_level":
                level = tag["value"]
                if level == "high":
                    score += 30
                elif level == "medium":
                    score += 15
                elif level == "low":
                    score += 5
            
            if tag["key"] == "access_scope":
                scope = tag["value"]
                if scope == "internal":
                    score += 20
                elif scope == "external":
                    score += 10
                elif scope == "public":
                    score += 0
        
        # 检查时间异常
        temporal_tags = [t for t in tags if t["type"] == "temporal"]
        for tag in temporal_tags:
            if tag["key"] == "hour_of_day":
                hour = tag["value"]
                # 非工作时间（晚上10点到早上6点）风险稍高
                if hour < 6 or hour > 22:
                    score += 10
        
        # 确定风险等级
        if score >= 60:
            level = "high"
        elif score >= 30:
            level = "medium"
        else:
            level = "low"
        
        return {
            "level": level,
            "score": min(score, 100),
            "confidence": 0.75
        }
    
    def verify_identity_token(self, token: str) -> Optional[Dict]:
        """
        验证身份令牌
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Invalid identity token: {e}")
            return None
    
    def refresh_identity_token(
        self,
        token: str,
        agent_id: int,
        user_id: int,
        db: Session
    ) -> Optional[str]:
        """
        刷新身份令牌
        """
        # 验证旧令牌
        payload = self.verify_identity_token(token)
        if not payload:
            return None
        
        # 获取会话上下文
        session_context = payload.get("ctx", {})
        
        # 生成新令牌
        new_token = self.generate_identity_token(
            agent_id,
            user_id,
            session_context
        )
        
        # 更新数据库
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            agent.identity_token = new_token
            agent.last_identity_refresh = datetime.utcnow()
            db.commit()
        
        logger.info(f"Refreshed identity token for agent {agent_id}")
        
        return new_token
    
    def should_refresh_token(self, agent: Agent) -> bool:
        """
        检查是否需要刷新令牌
        """
        if not agent.last_identity_refresh:
            return True
        
        elapsed = datetime.utcnow() - agent.last_identity_refresh
        return elapsed > self.identity_refresh_interval
    
    def validate_request_identity(
        self,
        token: str,
        request_context: Dict,
        db: Session
    ) -> Dict:
        """
        验证请求的身份合法性
        """
        result = {
            "valid": False,
            "agent_id": None,
            "user_id": None,
            "tags": [],
            "violations": [],
            "risk_level": "unknown"
        }
        
        # 验证令牌
        payload = self.verify_identity_token(token)
        if not payload:
            result["violations"].append("Invalid or expired identity token")
            return result
        
        agent_id = int(payload.get("sub"))
        user_id = int(payload.get("uid"))
        tags = payload.get("tags", [])
        
        result["valid"] = True
        result["agent_id"] = agent_id
        result["user_id"] = user_id
        result["tags"] = tags
        
        # 检查令牌是否需要刷新
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent and self.should_refresh_token(agent):
            result["should_refresh"] = True
        
        # 验证身份标签与请求上下文的一致性
        violations = self._check_identity_consistency(
            tags, 
            request_context
        )
        result["violations"].extend(violations)
        
        # 确定风险等级
        risk_tag = next((t for t in tags if t["key"] == "risk_level"), None)
        if risk_tag:
            result["risk_level"] = risk_tag["value"]
        
        # 如果有违规，标记为无效
        if violations:
            result["valid"] = False
            logger.warning(f"Identity validation failed for agent {agent_id}: {violations}")
        
        return result
    
    def _check_identity_consistency(
        self,
        tags: List[Dict],
        request_context: Dict
    ) -> List[str]:
        """
        检查身份标签与请求上下文的一致性
        """
        violations = []
        
        # 检查时间一致性
        temporal_tags = {t["key"]: t["value"] for t in tags if t["type"] == "temporal"}
        if "hour_of_day" in temporal_tags:
            token_hour = temporal_tags["hour_of_day"]
            current_hour = datetime.utcnow().hour
            
            # 允许1小时的误差（跨小时请求）
            if abs(current_hour - token_hour) > 1 and abs(current_hour - token_hour) < 23:
                violations.append("Time context mismatch")
        
        # 检查任务类型一致性
        if "task_type" in request_context:
            context_tags = {t["key"]: t["value"] for t in tags if t["type"] == "context"}
            if "task_type" in context_tags:
                token_task = context_tags["task_type"]
                request_task = request_context["task_type"]
                
                if token_task != request_task:
                    violations.append(f"Task type mismatch: {token_task} vs {request_task}")
        
        # 检查安全级别一致性
        if "security_level" in request_context:
            security_tags = {t["key"]: t["value"] for t in tags if t["type"] == "security"}
            if "security_level" in security_tags:
                token_level = security_tags["security_level"]
                request_level = request_context["security_level"]
                
                # 如果请求的安全级别高于令牌的安全级别，视为违规
                level_order = {"low": 1, "medium": 2, "high": 3}
                if level_order.get(request_level, 0) > level_order.get(token_level, 0):
                    violations.append(
                        f"Security level escalation: {token_level} -> {request_level}"
                    )
        
        return violations
    
    def log_identity_event(
        self,
        agent_id: int,
        user_id: int,
        event_type: str,
        details: Dict,
        db: Session
    ):
        """
        记录身份相关事件
        """
        log = AuditLog(
            user_id=user_id,
            agent_id=agent_id,
            log_type="identity",
            event=event_type,
            details=details,
            description=f"Identity event: {event_type}",
            risk_level=RiskLevel.MEDIUM if event_type == "violation" else RiskLevel.LOW,
            is_alert=(event_type == "violation")
        )
        
        db.add(log)
        db.commit()
    
    def revoke_identity_token(self, agent_id: int, db: Session) -> bool:
        """
        撤销Agent的身份令牌
        """
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False
        
        agent.identity_token = None
        agent.identity_tags = []
        agent.last_identity_refresh = None
        db.commit()
        
        logger.info(f"Revoked identity token for agent {agent_id}")
        
        return True

# 全局身份管理器实例（需要在应用启动时初始化）
identity_manager = None

def init_identity_manager(secret_key: str):
    """初始化身份管理器"""
    global identity_manager
    identity_manager = IdentityManager(secret_key)
    return identity_manager

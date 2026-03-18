"""
AI Agent Gateway - 影子网络系统核心网关
整合沙箱、策略控制、意图审计、身份联动和告警系统
"""
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import (
    NetworkRequest, PolicyAction, RiskLevel,
    Agent, AuditLog, Alert, Policy
)
from .sandbox import sandbox_manager
from .policy_engine import policy_engine
from .intent_analyzer import intent_analyzer, IntentAnalysisResult
from .identity_manager import identity_manager
from .alert_system import alert_system
from .privacy import privacy_manager

logger = logging.getLogger(__name__)

class AgentGateway:
    """Agent请求网关"""
    
    def __init__(self):
        self.request_count = 0
        self.blocked_count = 0
    
    async def process_request(
        self,
        agent_id: int,
        method: str,
        url: str,
        headers: Dict,
        body: Optional[str],
        db: Session,
        original_task: Optional[str] = None,
        identity_token: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        处理Agent的网络请求
        返回: (是否允许, 响应数据, 消息)
        """
        self.request_count += 1
        request_start_time = datetime.utcnow()
        
        try:
            # 1. 身份验证
            identity_result = self._verify_identity(
                agent_id, identity_token, headers, db
            )
            if not identity_result["valid"]:
                self.blocked_count += 1
                return False, None, f"Identity verification failed: {identity_result['violations']}"
            
            # 2. 策略评估
            policy_action, policy_id, policy_reason = policy_engine.evaluate_request(
                agent_id, method, url, headers, body, db
            )
            
            # 3. 意图分析
            intent_result = intent_analyzer.analyze_request(
                method, url, headers, body, original_task
            )
            
            # 4. 检查意图违规
            if policy_id:
                policy = db.query(Policy).filter(Policy.id == policy_id).first()
                if policy and policy.enable_intent_audit:
                    is_violation, violation_reason = policy_engine.check_intent_violation(
                        policy, intent_result.intent, original_task or ""
                    )
                    if is_violation:
                        policy_action = PolicyAction.DENY
                        policy_reason = f"Intent violation: {violation_reason}"
            
            # 5. 计算风险评分
            risk_score, risk_level = policy_engine.calculate_risk_score(
                method, url, headers, body, intent_result.intent
            )
            
            # 如果意图分析检测到恶意行为，提升风险等级
            if intent_result.is_malicious:
                risk_level = RiskLevel.CRITICAL
                risk_score = max(risk_score, 80)
                if policy_action == PolicyAction.ALLOW:
                    policy_action = PolicyAction.AUDIT
            
            # 6. 记录网络请求
            network_request = self._log_network_request(
                agent_id=agent_id,
                method=method,
                url=url,
                headers=headers,
                body=body,
                intent_analysis=intent_result.intent,
                risk_level=risk_level,
                risk_score=risk_score,
                policy_action=policy_action,
                policy_id=policy_id,
                blocked_reason=policy_reason if policy_action == PolicyAction.DENY else None,
                db=db
            )
            
            # 7. 审计日志
            self._create_audit_log(
                agent_id=agent_id,
                event="request_processed",
                details={
                    "method": method,
                    "url": url,
                    "policy_action": policy_action.value,
                    "risk_level": risk_level.value,
                    "intent": intent_result.intent,
                    "is_malicious": intent_result.is_malicious
                },
                risk_level=risk_level,
                is_alert=(policy_action == PolicyAction.DENY or intent_result.is_malicious),
                db=db
            )
            
            # 8. 检查告警
            if policy_action == PolicyAction.DENY or intent_result.is_malicious or risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert_system.check_and_create_alerts(agent_id, db)
            
            # 9. 执行策略动作
            if policy_action == PolicyAction.DENY:
                self.blocked_count += 1
                return False, {
                    "error": "Request blocked by policy",
                    "reason": policy_reason,
                    "risk_level": risk_level.value,
                    "request_id": network_request.id
                }, f"Request blocked: {policy_reason}"
            
            elif policy_action == PolicyAction.QUARANTINE:
                # 隔离请求 - 允许但限制功能
                return True, {
                    "warning": "Request quarantined",
                    "restrictions": ["no_external_calls", "read_only"],
                    "risk_level": risk_level.value,
                    "request_id": network_request.id
                }, "Request allowed with restrictions"
            
            elif policy_action == PolicyAction.AUDIT:
                # 审计模式 - 允许但记录详细日志
                logger.warning(f"Request under audit: {method} {url} (Agent {agent_id})")
            
            # 允许请求
            return True, {
                "request_id": network_request.id,
                "risk_level": risk_level.value,
                "policy_action": policy_action.value,
                "intent": intent_result.intent
            }, "Request allowed"
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            self.blocked_count += 1
            return False, None, f"Internal error: {str(e)}"
    
    def _verify_identity(
        self,
        agent_id: int,
        identity_token: Optional[str],
        headers: Dict,
        db: Session
    ) -> Dict:
        """验证身份"""
        if not identity_token:
            # 没有身份令牌，检查Agent是否存在
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                return {"valid": False, "violations": ["Agent not found"]}
            
            return {"valid": True, "agent_id": agent_id, "user_id": agent.user_id, "tags": []}
        
        # 验证身份令牌
        request_context = {
            "headers": headers,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return identity_manager.validate_request_identity(
            identity_token, request_context, db
        )
    
    def _log_network_request(
        self,
        agent_id: int,
        method: str,
        url: str,
        headers: Dict,
        body: Optional[str],
        intent_analysis: str,
        risk_level: RiskLevel,
        risk_score: int,
        policy_action: PolicyAction,
        policy_id: Optional[int],
        blocked_reason: Optional[str],
        db: Session
    ) -> NetworkRequest:
        """记录网络请求"""
        # 使用隐私管理器清理敏感信息
        safe_headers = privacy_manager.sanitize_data(headers, "high")
        safe_body = privacy_manager.sanitize_data(body, "high")
        
        # 评估数据敏感度
        sensitivity_score = privacy_manager.get_data_sensitivity_score(body)
        
        # 根据敏感度调整风险评分
        if sensitivity_score > 50:
            risk_score = min(risk_score + 20, 100)
            if risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                risk_level = RiskLevel.HIGH
        
        request = NetworkRequest(
            agent_id=agent_id,
            method=method,
            url=url[:2000],  # 限制长度
            headers=safe_headers,
            body=safe_body,
            intent_analysis=intent_analysis[:1000] if intent_analysis else None,
            risk_level=risk_level,
            risk_score=risk_score,
            policy_action=policy_action,
            policy_id=policy_id,
            blocked_reason=blocked_reason
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        
        return request
    
    def _sanitize_headers(self, headers: Dict) -> Dict:
        """清理请求头中的敏感信息"""
        sensitive_keys = ['authorization', 'cookie', 'x-api-key', 'token', 'password']
        safe_headers = {}
        
        for key, value in headers.items():
            if any(sk in key.lower() for sk in sensitive_keys):
                safe_headers[key] = "***REDACTED***"
            else:
                safe_headers[key] = value
        
        return safe_headers
    
    def _sanitize_body(self, body: Optional[str]) -> Optional[str]:
        """清理请求体中的敏感信息"""
        if not body:
            return None
        
        # 限制长度
        if len(body) > 10000:
            body = body[:10000] + "... [truncated]"
        
        # 尝试解析JSON并清理
        try:
            data = json.loads(body)
            self._sanitize_dict(data)
            return json.dumps(data)
        except json.JSONDecodeError:
            # 不是JSON，返回原始内容
            return body
    
    def _sanitize_dict(self, data: Dict):
        """递归清理字典中的敏感信息"""
        sensitive_keys = ['password', 'token', 'secret', 'key', 'credential', 'auth']
        
        for key in list(data.keys()):
            if any(sk in key.lower() for sk in sensitive_keys):
                data[key] = "***REDACTED***"
            elif isinstance(data[key], dict):
                self._sanitize_dict(data[key])
            elif isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        self._sanitize_dict(item)
    
    def _create_audit_log(
        self,
        agent_id: int,
        event: str,
        details: Dict,
        risk_level: RiskLevel,
        is_alert: bool,
        db: Session
    ):
        """创建审计日志"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return
        
        log = AuditLog(
            user_id=agent.user_id,
            agent_id=agent_id,
            log_type="network",
            event=event,
            details=details,
            description=f"Network request {event}",
            risk_level=risk_level,
            is_alert=is_alert
        )
        
        db.add(log)
        db.commit()
    
    def get_statistics(self) -> Dict:
        """获取网关统计信息"""
        return {
            "total_requests": self.request_count,
            "blocked_requests": self.blocked_count,
            "block_rate": self.blocked_count / self.request_count if self.request_count > 0 else 0
        }

# 全局网关实例
agent_gateway = AgentGateway()

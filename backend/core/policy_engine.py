"""
动态策略控制引擎
实现网络请求的拦截、策略匹配和执行
"""
import re
import json
import logging
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from ..models import Policy, PolicyAction, RiskLevel, NetworkRequest, Agent
from ..database import get_db

logger = logging.getLogger(__name__)

class PolicyEngine:
    """策略引擎"""
    
    def __init__(self):
        self.policy_cache = {}
        self.cache_version = 0
    
    def reload_policies(self, db: Session):
        """重新加载策略缓存"""
        policies = db.query(Policy).filter(Policy.is_active == True).order_by(Policy.priority).all()
        self.policy_cache = {}
        
        for policy in policies:
            if policy.user_id not in self.policy_cache:
                self.policy_cache[policy.user_id] = []
            self.policy_cache[policy.user_id].append(policy)
        
        self.cache_version += 1
        logger.info(f"Reloaded {len(policies)} policies for {len(self.policy_cache)} users")
    
    def evaluate_request(
        self,
        agent_id: int,
        method: str,
        url: str,
        headers: Dict,
        body: Optional[str],
        db: Session
    ) -> Tuple[PolicyAction, Optional[int], Optional[str]]:
        """
        评估请求是否符合策略
        返回: (动作, 策略ID, 原因)
        """
        # 获取Agent信息
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            logger.warning(f"Agent {agent_id} not found, denying request")
            return PolicyAction.DENY, None, "Agent not found"
        
        user_id = agent.user_id
        
        # 获取用户的策略
        policies = self.policy_cache.get(user_id, [])
        if not policies:
            # 如果没有配置策略，使用默认策略
            logger.debug(f"No policies found for user {user_id}, using default allow")
            return PolicyAction.ALLOW, None, None
        
        # 按优先级排序（数字越小优先级越高）
        sorted_policies = sorted(policies, key=lambda p: p.priority)
        
        # 匹配策略
        for policy in sorted_policies:
            if self._match_policy(policy, method, url, headers):
                logger.info(
                    f"Request matched policy {policy.id}: {policy.name}, "
                    f"action={policy.action.value}"
                )
                
                reason = f"Matched policy: {policy.name}"
                if policy.action == PolicyAction.DENY:
                    reason += f" - {policy.description or 'Access denied by policy'}"
                
                return policy.action, policy.id, reason
        
        # 没有匹配到任何策略，默认允许
        logger.debug(f"No policy matched for request to {url}")
        return PolicyAction.ALLOW, None, None
    
    def _match_policy(self, policy: Policy, method: str, url: str, headers: Dict) -> bool:
        """检查请求是否匹配策略"""
        try:
            # 匹配URL模式
            if policy.resource_pattern:
                pattern = policy.resource_pattern
                # 支持简单的通配符
                if '*' in pattern:
                    pattern = pattern.replace('*', '.*')
                
                if not re.search(pattern, url, re.IGNORECASE):
                    return False
            
            # 匹配资源类型
            if policy.resource_type == "api":
                # API请求通常有特定的Content-Type
                content_type = headers.get('content-type', '')
                if 'application/json' not in content_type:
                    # 如果不是JSON请求，检查URL是否包含/api/
                    if '/api/' not in url:
                        return False
            
            elif policy.resource_type == "database":
                # 数据库相关的URL模式
                db_patterns = ['database', 'db', 'sql', 'query', 'jdbc', 'mongodb', 'redis']
                if not any(p in url.lower() for p in db_patterns):
                    return False
            
            elif policy.resource_type == "file":
                # 文件操作相关的URL模式
                file_patterns = ['file', 'upload', 'download', 'storage', 's3', 'oss']
                if not any(p in url.lower() for p in file_patterns):
                    return False
            
            elif policy.resource_type == "network":
                # 网络相关的URL模式
                network_patterns = ['http', 'https', 'tcp', 'udp', 'socket', 'proxy']
                if not any(p in url.lower() for p in network_patterns):
                    return False
            
            return True
            
        except re.error as e:
            logger.error(f"Invalid regex pattern in policy {policy.id}: {e}")
            return False
    
    def check_intent_violation(
        self,
        policy: Policy,
        intent_analysis: str,
        original_task: str
    ) -> Tuple[bool, str]:
        """
        检查意图是否违反策略
        返回: (是否违规, 原因)
        """
        if not policy.enable_intent_audit or not policy.intent_rules:
            return False, ""
        
        intent_lower = intent_analysis.lower()
        task_lower = original_task.lower()
        
        for rule in policy.intent_rules:
            rule_type = rule.get('type')
            pattern = rule.get('pattern', '')
            
            if rule_type == 'forbidden':
                # 禁止的行为
                if re.search(pattern, intent_lower, re.IGNORECASE):
                    return True, f"Forbidden intent detected: {pattern}"
            
            elif rule_type == 'task_mismatch':
                # 任务不匹配
                # 检查意图是否与原始任务严重偏离
                task_keywords = task_lower.split()
                intent_keywords = intent_lower.split()
                
                # 简单的任务匹配检查
                match_count = sum(1 for kw in task_keywords if kw in intent_keywords)
                if len(task_keywords) > 0 and match_count / len(task_keywords) < 0.3:
                    return True, f"Intent deviates significantly from original task: {original_task}"
            
            elif rule_type == 'sensitive_operation':
                # 敏感操作
                sensitive_patterns = [
                    'delete', 'drop', 'truncate', 'remove',
                    'modify', 'update', 'alter', 'change',
                    'grant', 'privilege', 'permission',
                    'password', 'credential', 'secret', 'key'
                ]
                
                for sp in sensitive_patterns:
                    if sp in intent_lower and sp not in task_lower:
                        return True, f"Sensitive operation detected without authorization: {sp}"
        
        return False, ""
    
    def calculate_risk_score(
        self,
        method: str,
        url: str,
        headers: Dict,
        body: Optional[str],
        intent_analysis: Optional[str] = None
    ) -> Tuple[int, RiskLevel]:
        """
        计算风险评分
        返回: (分数0-100, 风险等级)
        """
        score = 0
        reasons = []
        
        # 基于HTTP方法的风险
        method_risk = {
            'GET': 5,
            'HEAD': 5,
            'OPTIONS': 5,
            'POST': 20,
            'PUT': 30,
            'PATCH': 30,
            'DELETE': 50
        }
        score += method_risk.get(method.upper(), 20)
        
        # 基于URL的风险
        url_lower = url.lower()
        
        # 敏感端点
        sensitive_endpoints = [
            ('admin', 30),
            ('config', 25),
            ('settings', 20),
            ('password', 35),
            ('credential', 35),
            ('secret', 40),
            ('token', 30),
            ('api-key', 35),
            ('database', 25),
            ('db', 25),
            ('sql', 30),
            ('exec', 40),
            ('eval', 40),
            ('system', 35),
            ('shell', 45),
            ('command', 40),
            ('file', 20),
            ('upload', 25),
            ('download', 20)
        ]
        
        for endpoint, risk in sensitive_endpoints:
            if endpoint in url_lower:
                score += risk
                reasons.append(f"Sensitive endpoint: {endpoint}")
                break  # 只加一次
        
        # 外部域名风险
        external_domains = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '169.254',  # 链路本地地址
            '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.',
            '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
            '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
            '192.168.'
        ]
        
        for domain in external_domains:
            if domain in url_lower:
                score += 30
                reasons.append(f"Internal network access: {domain}")
                break
        
        # 基于意图分析的风险
        if intent_analysis:
            intent_lower = intent_analysis.lower()
            
            # 恶意意图关键词
            malicious_keywords = [
                ('scan', 25),
                ('attack', 50),
                ('exploit', 50),
                ('inject', 45),
                ('bypass', 40),
                ('brute', 35),
                ('force', 30),
                ('steal', 45),
                ('leak', 40),
                ('dump', 35)
            ]
            
            for keyword, risk in malicious_keywords:
                if keyword in intent_lower:
                    score += risk
                    reasons.append(f"Malicious intent keyword: {keyword}")
        
        # 限制分数范围
        score = min(100, max(0, score))
        
        # 确定风险等级
        if score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif score >= 60:
            risk_level = RiskLevel.HIGH
        elif score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        logger.debug(f"Risk score for {method} {url}: {score} ({risk_level.value})")
        
        return score, risk_level
    
    def create_default_policies(self, user_id: int, db: Session):
        """为用户创建默认策略"""
        default_policies = [
            {
                "name": "禁止访问内部网络",
                "description": "禁止访问本地网络和私有IP地址",
                "resource_type": "network",
                "resource_pattern": "(localhost|127\\.0\\.0\\.1|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)",
                "action": PolicyAction.DENY,
                "priority": 1,
                "risk_threshold": RiskLevel.HIGH
            },
            {
                "name": "限制敏感操作",
                "description": "限制删除、修改等敏感操作",
                "resource_type": "api",
                "resource_pattern": "(delete|remove|drop|truncate)",
                "action": PolicyAction.AUDIT,
                "priority": 10,
                "enable_intent_audit": True,
                "intent_rules": [
                    {"type": "forbidden", "pattern": "delete.*database"},
                    {"type": "forbidden", "pattern": "drop.*table"}
                ],
                "risk_threshold": RiskLevel.HIGH
            },
            {
                "name": "审计文件上传",
                "description": "审计所有文件上传操作",
                "resource_type": "file",
                "resource_pattern": "(upload|file)",
                "action": PolicyAction.AUDIT,
                "priority": 20,
                "enable_intent_audit": True,
                "risk_threshold": RiskLevel.MEDIUM
            },
            {
                "name": "允许常规API访问",
                "description": "允许常规的API请求",
                "resource_type": "api",
                "resource_pattern": "*",
                "action": PolicyAction.ALLOW,
                "priority": 100,
                "risk_threshold": RiskLevel.LOW
            }
        ]
        
        for policy_data in default_policies:
            policy = Policy(
                user_id=user_id,
                **policy_data
            )
            db.add(policy)
        
        db.commit()
        logger.info(f"Created {len(default_policies)} default policies for user {user_id}")
        
        # 刷新缓存
        self.reload_policies(db)

# 全局策略引擎实例
policy_engine = PolicyEngine()

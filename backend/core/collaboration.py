"""
智能体协作管理模块
实现智能体之间的安全协作机制
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.models import (
    Agent, AgentTeam, TeamMember, NetworkRequest,
    PolicyAction, RiskLevel, AuditLog
)
from backend.core.policy_engine import policy_engine
from backend.core.identity_manager import identity_manager
from backend.core.alert_system import alert_system

logger = logging.getLogger(__name__)

class CollaborationManager:
    """智能体协作管理器"""
    
    def __init__(self):
        self.collaboration_count = 0
        self.security_violations = 0
    
    def create_team(self, user_id: int, name: str, description: str, db: Session) -> AgentTeam:
        """创建智能体团队"""
        team_id = f"team_{str(uuid.uuid4())[:8]}"
        
        team = AgentTeam(
            team_id=team_id,
            name=name,
            description=description,
            user_id=user_id,
            collaboration_policy={
                "allowed_operations": ["data_sharing", "task_assignment", "resource_access"],
                "security_protocols": ["end_to_end_encryption", "access_control", "audit_logging"],
                "communication_timeout": 30,
                "retry_attempts": 3
            }
        )
        
        db.add(team)
        db.commit()
        db.refresh(team)
        
        logger.info(f"Created team: {name} (ID: {team_id}) for user {user_id}")
        return team
    
    def add_agent_to_team(self, team_id: str, agent_id: int, role: str, permissions: Dict, db: Session) -> TeamMember:
        """添加智能体到团队"""
        # 检查团队是否存在
        team = db.query(AgentTeam).filter(AgentTeam.team_id == team_id).first()
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        # 检查智能体是否存在
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # 检查是否已经是团队成员
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.agent_id == agent_id
        ).first()
        
        if existing_member:
            raise ValueError(f"Agent {agent_id} is already a member of team {team_id}")
        
        # 创建团队成员
        team_member = TeamMember(
            team_id=team_id,
            agent_id=agent_id,
            role=role,
            permissions=permissions
        )
        
        # 更新智能体的团队信息
        agent.team_id = team_id
        agent.collaboration_mode = "collaborative"
        agent.role = role
        
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        
        logger.info(f"Added agent {agent_id} to team {team_id} with role {role}")
        return team_member
    
    def remove_agent_from_team(self, team_id: str, agent_id: int, db: Session) -> bool:
        """从团队中移除智能体"""
        team_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.agent_id == agent_id
        ).first()
        
        if not team_member:
            return False
        
        # 更新智能体信息
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            agent.team_id = None
            agent.collaboration_mode = "independent"
            agent.role = None
        
        db.delete(team_member)
        db.commit()
        
        logger.info(f"Removed agent {agent_id} from team {team_id}")
        return True
    
    async def process_collaboration_request(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        request_type: str,
        payload: Dict,
        db: Session,
        identity_token: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        处理智能体之间的协作请求
        返回: (是否允许, 响应数据, 消息)
        """
        self.collaboration_count += 1
        
        try:
            # 1. 验证发送方身份
            sender = db.query(Agent).filter(Agent.id == sender_agent_id).first()
            if not sender:
                return False, None, "Sender agent not found"
            
            # 2. 验证接收方身份
            receiver = db.query(Agent).filter(Agent.id == receiver_agent_id).first()
            if not receiver:
                return False, None, "Receiver agent not found"
            
            # 3. 检查协作权限
            has_permission, permission_reason = self._check_collaboration_permission(
                sender_agent_id, receiver_agent_id, request_type, db
            )
            
            if not has_permission:
                self.security_violations += 1
                # 记录安全违规
                self._create_audit_log(
                    agent_id=sender_agent_id,
                    event="collaboration_attempt",
                    details={
                        "receiver_agent_id": receiver_agent_id,
                        "request_type": request_type,
                        "violation_reason": permission_reason
                    },
                    risk_level=RiskLevel.HIGH,
                    is_alert=True,
                    db=db
                )
                return False, None, f"Permission denied: {permission_reason}"
            
            # 4. 评估安全风险
            risk_score, risk_level = self._assess_collaboration_risk(
                sender_agent_id, receiver_agent_id, request_type, payload
            )
            
            # 5. 记录协作请求
            collaboration_id = f"collab_{str(uuid.uuid4())[:12]}"
            
            # 6. 处理具体的协作请求
            if request_type == "data_sharing":
                return await self._handle_data_sharing(
                    sender_agent_id, receiver_agent_id, payload, db
                )
            elif request_type == "task_assignment":
                return await self._handle_task_assignment(
                    sender_agent_id, receiver_agent_id, payload, db
                )
            elif request_type == "resource_access":
                return await self._handle_resource_access(
                    sender_agent_id, receiver_agent_id, payload, db
                )
            else:
                return False, None, f"Unsupported request type: {request_type}"
                
        except Exception as e:
            logger.error(f"Error processing collaboration request: {e}", exc_info=True)
            return False, None, f"Internal error: {str(e)}"
    
    def _check_collaboration_permission(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        request_type: str,
        db: Session
    ) -> Tuple[bool, str]:
        """检查协作权限"""
        # 检查是否在同一团队
        sender = db.query(Agent).filter(Agent.id == sender_agent_id).first()
        receiver = db.query(Agent).filter(Agent.id == receiver_agent_id).first()
        
        if not sender or not receiver:
            return False, "Agent not found"
        
        # 检查团队成员身份
        if sender.team_id != receiver.team_id:
            return False, "Agents are not in the same team"
        
        # 检查团队成员权限
        sender_member = db.query(TeamMember).filter(
            TeamMember.team_id == sender.team_id,
            TeamMember.agent_id == sender_agent_id
        ).first()
        
        if not sender_member or not sender_member.is_active:
            return False, "Sender is not an active team member"
        
        # 检查请求类型权限
        team = db.query(AgentTeam).filter(AgentTeam.team_id == sender.team_id).first()
        if not team:
            return False, "Team not found"
        
        allowed_operations = team.collaboration_policy.get("allowed_operations", [])
        if request_type not in allowed_operations:
            return False, f"Request type {request_type} is not allowed"
        
        # 检查具体权限
        permissions = sender_member.permissions.get(request_type, {})
        if not permissions.get("allowed", False):
            return False, f"Sender does not have permission for {request_type}"
        
        return True, "Permission granted"
    
    def _assess_collaboration_risk(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        request_type: str,
        payload: Dict
    ) -> Tuple[int, RiskLevel]:
        """评估协作风险"""
        risk_score = 0
        
        # 基于请求类型的风险评估
        risk_factors = {
            "data_sharing": 20,
            "task_assignment": 15,
            "resource_access": 25
        }
        
        risk_score += risk_factors.get(request_type, 10)
        
        # 基于数据敏感性的风险评估
        if request_type == "data_sharing":
            data_type = payload.get("data_type", "")
            sensitive_data_types = ["personal", "financial", "health", "credentials"]
            if any(sensitive in data_type.lower() for sensitive in sensitive_data_types):
                risk_score += 30
        
        # 基于资源类型的风险评估
        elif request_type == "resource_access":
            resource_type = payload.get("resource_type", "")
            sensitive_resources = ["database", "api_key", "private_key", "configuration"]
            if any(sensitive in resource_type.lower() for sensitive in sensitive_resources):
                risk_score += 35
        
        # 确定风险等级
        if risk_score >= 70:
            return risk_score, RiskLevel.CRITICAL
        elif risk_score >= 50:
            return risk_score, RiskLevel.HIGH
        elif risk_score >= 30:
            return risk_score, RiskLevel.MEDIUM
        else:
            return risk_score, RiskLevel.LOW
    
    async def _handle_data_sharing(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        payload: Dict,
        db: Session
    ) -> Tuple[bool, Dict, str]:
        """处理数据共享请求"""
        # 提取数据
        data = payload.get("data", {})
        data_type = payload.get("data_type", "general")
        
        # 数据脱敏处理
        sanitized_data = self._sanitize_shared_data(data, data_type)
        
        # 记录数据共享
        self._create_audit_log(
            agent_id=sender_agent_id,
            event="data_shared",
            details={
                "receiver_agent_id": receiver_agent_id,
                "data_type": data_type,
                "data_size": len(str(data))
            },
            risk_level=RiskLevel.MEDIUM,
            is_alert=False,
            db=db
        )
        
        # 更新智能体的协作历史
        self._update_collaboration_history(
            sender_agent_id, receiver_agent_id, "data_sharing", db
        )
        
        return True, {
            "status": "success",
            "message": "Data shared successfully",
            "data": sanitized_data,
            "timestamp": datetime.utcnow().isoformat()
        }, "Data shared successfully"
    
    async def _handle_task_assignment(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        payload: Dict,
        db: Session
    ) -> Tuple[bool, Dict, str]:
        """处理任务分配请求"""
        # 提取任务信息
        task_id = payload.get("task_id", f"task_{uuid.uuid4().hex[:8]}")
        task_name = payload.get("task_name", "Unknown task")
        task_description = payload.get("task_description", "")
        deadline = payload.get("deadline")
        
        # 记录任务分配
        self._create_audit_log(
            agent_id=sender_agent_id,
            event="task_assigned",
            details={
                "receiver_agent_id": receiver_agent_id,
                "task_id": task_id,
                "task_name": task_name
            },
            risk_level=RiskLevel.LOW,
            is_alert=False,
            db=db
        )
        
        # 更新智能体的协作历史
        self._update_collaboration_history(
            sender_agent_id, receiver_agent_id, "task_assignment", db
        )
        
        return True, {
            "status": "success",
            "message": "Task assigned successfully",
            "task_id": task_id,
            "task_name": task_name,
            "timestamp": datetime.utcnow().isoformat()
        }, "Task assigned successfully"
    
    async def _handle_resource_access(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        payload: Dict,
        db: Session
    ) -> Tuple[bool, Dict, str]:
        """处理资源访问请求"""
        # 提取资源信息
        resource_id = payload.get("resource_id")
        resource_type = payload.get("resource_type")
        access_type = payload.get("access_type", "read")
        
        # 检查资源访问权限
        if access_type not in ["read", "write", "execute"]:
            return False, None, f"Invalid access type: {access_type}"
        
        # 记录资源访问
        self._create_audit_log(
            agent_id=sender_agent_id,
            event="resource_access",
            details={
                "receiver_agent_id": receiver_agent_id,
                "resource_id": resource_id,
                "resource_type": resource_type,
                "access_type": access_type
            },
            risk_level=RiskLevel.MEDIUM,
            is_alert=False,
            db=db
        )
        
        # 更新智能体的协作历史
        self._update_collaboration_history(
            sender_agent_id, receiver_agent_id, "resource_access", db
        )
        
        return True, {
            "status": "success",
            "message": "Resource access granted",
            "resource_id": resource_id,
            "access_type": access_type,
            "timestamp": datetime.utcnow().isoformat()
        }, "Resource access granted"
    
    def _sanitize_shared_data(self, data: Dict, data_type: str) -> Dict:
        """对共享数据进行脱敏处理"""
        if not isinstance(data, dict):
            return data
        
        sanitized_data = data.copy()
        
        # 定义敏感字段
        sensitive_fields = {
            "personal": ["name", "email", "phone", "address", "ssn"],
            "financial": ["credit_card", "bank_account", "password", "token"],
            "health": ["medical_record", "diagnosis", "treatment"],
            "credentials": ["username", "password", "api_key", "secret"]
        }
        
        # 对敏感字段进行脱敏
        fields_to_sanitize = sensitive_fields.get(data_type, [])
        for field in fields_to_sanitize:
            if field in sanitized_data:
                sanitized_data[field] = "***REDACTED***"
        
        return sanitized_data
    
    def _update_collaboration_history(
        self,
        sender_agent_id: int,
        receiver_agent_id: int,
        collaboration_type: str,
        db: Session
    ):
        """更新智能体的协作历史"""
        # 更新发送方的协作历史
        sender = db.query(Agent).filter(Agent.id == sender_agent_id).first()
        if sender:
            history = sender.collaboration_history or []
            history.append({
                "type": collaboration_type,
                "action": "sent",
                "target_agent_id": receiver_agent_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            # 限制历史记录长度
            if len(history) > 100:
                history = history[-100:]
            sender.collaboration_history = history
        
        # 更新接收方的协作历史
        receiver = db.query(Agent).filter(Agent.id == receiver_agent_id).first()
        if receiver:
            history = receiver.collaboration_history or []
            history.append({
                "type": collaboration_type,
                "action": "received",
                "source_agent_id": sender_agent_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            # 限制历史记录长度
            if len(history) > 100:
                history = history[-100:]
            receiver.collaboration_history = history
        
        db.commit()
    
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
            log_type="collaboration",
            event=event,
            details=details,
            description=f"Collaboration {event}",
            risk_level=risk_level,
            is_alert=is_alert
        )
        
        db.add(log)
        db.commit()
        
        # 如果是告警，创建告警记录
        if is_alert:
            alert_system.check_and_create_alerts(agent_id, db)
    
    def get_team_members(self, team_id: str, db: Session) -> List[Dict]:
        """获取团队成员"""
        members = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        ).all()
        
        return [{
            "agent_id": member.agent_id,
            "role": member.role,
            "permissions": member.permissions,
            "joined_at": member.joined_at.isoformat() if member.joined_at else None
        } for member in members]
    
    def get_agent_teams(self, agent_id: int, db: Session) -> List[Dict]:
        """获取智能体所属的团队"""
        memberships = db.query(TeamMember).filter(
            TeamMember.agent_id == agent_id,
            TeamMember.is_active == True
        ).all()
        
        teams = []
        for membership in memberships:
            team = db.query(AgentTeam).filter(
                AgentTeam.team_id == membership.team_id
            ).first()
            if team:
                teams.append({
                    "team_id": team.team_id,
                    "name": team.name,
                    "role": membership.role,
                    "permissions": membership.permissions
                })
        
        return teams
    
    def get_statistics(self) -> Dict:
        """获取协作统计信息"""
        return {
            "total_collaborations": self.collaboration_count,
            "security_violations": self.security_violations,
            "violation_rate": self.security_violations / self.collaboration_count if self.collaboration_count > 0 else 0
        }

# 全局协作管理器实例
collaboration_manager = CollaborationManager()

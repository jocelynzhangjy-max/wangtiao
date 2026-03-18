"""智能体信誉系统和行为评估模块"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import Agent, AuditLog, Alert, NetworkRequest, AgentTeam, TeamMember

logger = logging.getLogger(__name__)

class ReputationManager:
    """智能体信誉管理器"""
    
    def __init__(self):
        # 信誉评分权重配置
        self.reputation_weights = {
            "security_compliance": 0.3,       # 安全合规性
            "collaboration_success": 0.25,     # 协作成功率
            "resource_efficiency": 0.15,       # 资源使用效率
            "response_quality": 0.15,          # 响应质量
            "behavior_consistency": 0.15       # 行为一致性
        }
        
        # 行为评估指标
        self.behavior_metrics = {
            "security": {
                "unauthorized_access": -10,     # 未授权访问
                "data_exfiltration": -20,       # 数据泄露
                "malicious_activity": -25,      # 恶意活动
                "compliance_violation": -15     # 合规违规
            },
            "efficiency": {
                "task_completion": 5,           # 任务完成
                "resource_optimization": 3,     # 资源优化
                "response_time": 2              # 响应时间
            },
            "reliability": {
                "consistent_performance": 4,    # 一致性能
                "error_rate": -3,               # 错误率
                "availability": 3               # 可用性
            },
            "collaboration": {
                "teamwork": 5,                  # 团队合作
                "resource_sharing": 3,          # 资源共享
                "communication_quality": 4      # 沟通质量
            }
        }
    
    def calculate_reputation_score(self, agent_id: int, db: Session) -> Dict[str, Any]:
        """计算智能体的信誉评分"""
        try:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise ValueError(f"Agent with ID {agent_id} not found")
            
            # 获取最近30天的审计日志和网络请求
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # 安全合规性评估
            security_score = self._evaluate_security_compliance(agent_id, cutoff_date, db)
            
            # 协作成功率评估
            collaboration_score = self._evaluate_collaboration_success(agent_id, cutoff_date, db)
            
            # 资源使用效率评估
            resource_score = self._evaluate_resource_efficiency(agent_id, cutoff_date, db)
            
            # 响应质量评估
            response_score = self._evaluate_response_quality(agent_id, cutoff_date, db)
            
            # 行为一致性评估
            consistency_score = self._evaluate_behavior_consistency(agent_id, cutoff_date, db)
            
            # 计算加权总分
            total_score = (
                security_score * self.reputation_weights["security_compliance"] +
                collaboration_score * self.reputation_weights["collaboration_success"] +
                resource_score * self.reputation_weights["resource_efficiency"] +
                response_score * self.reputation_weights["response_quality"] +
                consistency_score * self.reputation_weights["behavior_consistency"]
            )
            
            # 确保分数在0-100之间
            total_score = max(0, min(100, total_score))
            
            # 更新智能体的信任等级
            agent.trust_level = int(total_score)
            db.commit()
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "total_score": total_score,
                "security_score": security_score,
                "collaboration_score": collaboration_score,
                "resource_score": resource_score,
                "response_score": response_score,
                "consistency_score": consistency_score,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating reputation score: {e}")
            raise
    
    def _evaluate_security_compliance(self, agent_id: int, cutoff_date: datetime, db: Session) -> float:
        """评估安全合规性"""
        # 获取安全相关的审计日志和告警
        security_alerts = db.query(Alert).filter(
            Alert.agent_id == agent_id,
            Alert.alert_type.in_(["security_violation", "unauthorized_access", "data_exfiltration"]),
            Alert.created_at >= cutoff_date
        ).count()
        
        # 获取总网络请求数
        total_requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id == agent_id,
            NetworkRequest.request_time >= cutoff_date
        ).count()
        
        if total_requests == 0:
            return 100.0
        
        # 计算安全合规性得分（无安全问题为100分）
        compliance_score = 100.0 - (security_alerts * 10)
        return max(0, compliance_score)
    
    def _evaluate_collaboration_success(self, agent_id: int, cutoff_date: datetime, db: Session) -> float:
        """评估协作成功率"""
        # 获取智能体参与的团队
        team_memberships = db.query(TeamMember).filter(TeamMember.agent_id == agent_id).all()
        team_ids = [tm.team_id for tm in team_memberships]
        
        if not team_ids:
            return 50.0  # 无协作历史，给予中等分数
        
        # 计算协作成功率（简化版）
        # 这里可以根据实际的协作任务完成情况进行更详细的评估
        return 75.0  # 暂时返回默认值，实际项目中需要根据具体协作数据计算
    
    def _evaluate_resource_efficiency(self, agent_id: int, cutoff_date: datetime, db: Session) -> float:
        """评估资源使用效率"""
        # 分析网络请求的资源使用情况
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id == agent_id,
            NetworkRequest.request_time >= cutoff_date
        ).all()
        
        if not requests:
            return 100.0
        
        # 计算平均响应时间
        total_response_time = sum(r.response_time or 0 for r in requests)
        avg_response_time = total_response_time / len(requests)
        
        # 响应时间越短，得分越高
        if avg_response_time < 1:
            return 100.0
        elif avg_response_time < 3:
            return 80.0
        elif avg_response_time < 5:
            return 60.0
        else:
            return 40.0
    
    def _evaluate_response_quality(self, agent_id: int, cutoff_date: datetime, db: Session) -> float:
        """评估响应质量"""
        # 这里可以根据实际的响应质量评估标准进行计算
        # 例如，基于用户反馈、任务完成质量等
        return 80.0  # 暂时返回默认值，实际项目中需要根据具体数据计算
    
    def _evaluate_behavior_consistency(self, agent_id: int, cutoff_date: datetime, db: Session) -> float:
        """评估行为一致性"""
        # 分析智能体行为模式的一致性
        # 例如，检查请求频率、操作类型的一致性等
        return 85.0  # 暂时返回默认值，实际项目中需要根据具体数据计算
    
    def generate_behavior_report(self, agent_id: int, db: Session) -> Dict[str, Any]:
        """生成智能体行为分析报告"""
        try:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise ValueError(f"Agent with ID {agent_id} not found")
            
            # 获取最近7天的数据
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            # 获取网络请求数据
            network_requests = db.query(NetworkRequest).filter(
                NetworkRequest.agent_id == agent_id,
                NetworkRequest.request_time >= cutoff_date
            ).all()
            
            # 获取审计日志
            audit_logs = db.query(AuditLog).filter(
                AuditLog.agent_id == agent_id,
                AuditLog.created_at >= cutoff_date
            ).all()
            
            # 获取告警
            alerts = db.query(Alert).filter(
                Alert.agent_id == agent_id,
                Alert.created_at >= cutoff_date
            ).all()
            
            # 分析行为模式
            behavior_patterns = self._analyze_behavior_patterns(network_requests, audit_logs)
            
            # 识别异常行为
            anomalies = self._identify_anomalies(network_requests, audit_logs, alerts)
            
            # 生成报告
            report = {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "report_period": f"{cutoff_date.isoformat()} to {datetime.utcnow().isoformat()}",
                "total_requests": len(network_requests),
                "total_logs": len(audit_logs),
                "total_alerts": len(alerts),
                "behavior_patterns": behavior_patterns,
                "anomalies": anomalies,
                "recommendations": self._generate_recommendations(anomalies)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating behavior report: {e}")
            raise
    
    def _analyze_behavior_patterns(self, network_requests: List[NetworkRequest], 
                                 audit_logs: List[AuditLog]) -> Dict[str, Any]:
        """分析智能体行为模式"""
        patterns = {
            "request_types": defaultdict(int),
            "request_frequency": defaultdict(int),
            "error_rates": defaultdict(int)
        }
        
        # 分析请求类型
        for req in network_requests:
            patterns["request_types"][req.request_type or "unknown"] += 1
            # 按小时统计请求频率
            hour = req.request_time.hour if req.request_time else 0
            patterns["request_frequency"][hour] += 1
            # 统计错误率
            if req.status_code and req.status_code >= 400:
                patterns["error_rates"][req.request_type or "unknown"] += 1
        
        return patterns
    
    def _identify_anomalies(self, network_requests: List[NetworkRequest], 
                          audit_logs: List[AuditLog], alerts: List[Alert]) -> List[Dict[str, Any]]:
        """识别异常行为"""
        anomalies = []
        
        # 基于告警识别异常
        for alert in alerts:
            anomalies.append({
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.created_at.isoformat()
            })
        
        # 基于网络请求异常识别
        # 例如：请求频率异常、错误率异常等
        # 这里可以添加更复杂的异常检测逻辑
        
        return anomalies
    
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if any(a["type"] == "security_violation" for a in anomalies):
            recommendations.append("加强安全策略，限制敏感操作的权限")
        
        if any(a["type"] == "unauthorized_access" for a in anomalies):
            recommendations.append("审查并更新访问控制策略")
        
        if any(a["severity"] == "high" for a in anomalies):
            recommendations.append("立即审查智能体配置，修复高风险问题")
        
        if not anomalies:
            recommendations.append("智能体行为正常，继续保持良好实践")
        
        return recommendations
    
    def get_reputation_summary(self, user_id: int, db: Session) -> Dict[str, Any]:
        """获取用户所有智能体的信誉摘要"""
        try:
            # 获取用户的所有智能体
            agents = db.query(Agent).filter(Agent.user_id == user_id).all()
            
            reputation_data = []
            total_score = 0
            
            for agent in agents:
                score_data = self.calculate_reputation_score(agent.id, db)
                reputation_data.append(score_data)
                total_score += score_data["total_score"]
            
            avg_score = total_score / len(agents) if agents else 0
            
            # 按信誉评分排序
            reputation_data.sort(key=lambda x: x["total_score"], reverse=True)
            
            return {
                "user_id": user_id,
                "total_agents": len(agents),
                "average_reputation_score": avg_score,
                "top_performers": reputation_data[:3],  # 前3名
                "low_performers": reputation_data[-3:] if len(reputation_data) >= 3 else reputation_data,  # 后3名
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting reputation summary: {e}")
            raise

# 初始化信誉管理器
reputation_manager = ReputationManager()

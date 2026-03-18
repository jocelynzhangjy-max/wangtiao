"""
异常行为检测和告警系统
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from backend.models import (
    Alert, NetworkRequest, AuditLog, Agent,
    RiskLevel, PolicyAction
)
from backend.database import get_db

logger = logging.getLogger(__name__)

class AlertSystem:
    """告警系统"""
    
    def __init__(self):
        self.alert_thresholds = {
            "request_rate": 100,  # 每分钟请求数阈值
            "error_rate": 0.1,    # 错误率阈值（10%）
            "risk_score": 70,     # 风险评分阈值
            "anomaly_score": 0.8  # 异常评分阈值
        }
    
    def check_and_create_alerts(self, agent_id: int, db: Session):
        """
        检查并创建告警
        """
        alerts_created = []
        
        # 1. 检查异常请求频率
        frequency_alert = self._check_request_frequency(agent_id, db)
        if frequency_alert:
            alerts_created.append(frequency_alert)
        
        # 2. 检查异常行为模式
        behavior_alert = self._check_behavior_anomaly(agent_id, db)
        if behavior_alert:
            alerts_created.append(behavior_alert)
        
        # 3. 检查策略违规
        policy_alert = self._check_policy_violations(agent_id, db)
        if policy_alert:
            alerts_created.append(policy_alert)
        
        # 4. 检查安全风险
        security_alert = self._check_security_risks(agent_id, db)
        if security_alert:
            alerts_created.append(security_alert)
        
        # 保存告警
        for alert_data in alerts_created:
            alert = Alert(**alert_data)
            db.add(alert)
        
        if alerts_created:
            db.commit()
            logger.info(f"Created {len(alerts_created)} alerts for agent {agent_id}")
        
        return alerts_created
    
    def _check_request_frequency(self, agent_id: int, db: Session) -> Optional[Dict]:
        """检查请求频率异常"""
        # 获取最近1分钟的请求数
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        request_count = db.query(NetworkRequest).filter(
            and_(
                NetworkRequest.agent_id == agent_id,
                NetworkRequest.request_time >= one_minute_ago
            )
        ).count()
        
        if request_count > self.alert_thresholds["request_rate"]:
            return {
                "agent_id": agent_id,
                "title": "异常请求频率",
                "description": f"Agent在1分钟内发送了{request_count}个请求，超过阈值{self.alert_thresholds['request_rate']}",
                "alert_type": "anomaly",
                "severity": RiskLevel.HIGH,
                "status": "open",
                "evidence": {
                    "request_count": request_count,
                    "threshold": self.alert_thresholds["request_rate"],
                    "time_window": "1 minute"
                }
            }
        
        return None
    
    def _check_behavior_anomaly(self, agent_id: int, db: Session) -> Optional[Dict]:
        """检查行为异常"""
        # 获取最近的行为模式
        recent_requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id == agent_id
        ).order_by(NetworkRequest.request_time.desc()).limit(50).all()
        
        if len(recent_requests) < 10:
            return None
        
        # 分析行为模式
        anomalies = []
        
        # 检查时间分布异常（正常工作时间外的大量请求）
        off_hours_requests = sum(
            1 for r in recent_requests
            if r.request_time and (r.request_time.hour < 6 or r.request_time.hour > 22)
        )
        if off_hours_requests / len(recent_requests) > 0.5:
            anomalies.append(f"工作时间外请求占比: {off_hours_requests / len(recent_requests):.1%}")
        
        # 检查URL多样性异常（访问大量不同的端点）
        unique_urls = len(set(r.url for r in recent_requests))
        if unique_urls > len(recent_requests) * 0.8:
            anomalies.append(f"高URL多样性: {unique_urls}个不同URL")
        
        # 检查被阻止请求比例
        blocked_requests = sum(
            1 for r in recent_requests
            if r.policy_action == PolicyAction.DENY
        )
        blocked_ratio = blocked_requests / len(recent_requests)
        if blocked_ratio > self.alert_thresholds["error_rate"]:
            anomalies.append(f"高阻止率: {blocked_ratio:.1%}")
        
        if anomalies:
            return {
                "agent_id": agent_id,
                "title": "行为模式异常",
                "description": "检测到Agent的异常行为模式: " + "; ".join(anomalies),
                "alert_type": "anomaly",
                "severity": RiskLevel.MEDIUM,
                "status": "open",
                "evidence": {
                    "anomalies": anomalies,
                    "request_count": len(recent_requests),
                    "unique_urls": unique_urls,
                    "blocked_ratio": blocked_ratio
                }
            }
        
        return None
    
    def _check_policy_violations(self, agent_id: int, db: Session) -> Optional[Dict]:
        """检查策略违规"""
        # 获取最近的策略违规记录
        recent_violations = db.query(NetworkRequest).filter(
            and_(
                NetworkRequest.agent_id == agent_id,
                NetworkRequest.policy_action == PolicyAction.DENY,
                NetworkRequest.request_time >= datetime.utcnow() - timedelta(hours=1)
            )
        ).all()
        
        if len(recent_violations) >= 5:  # 1小时内5次以上违规
            violation_types = {}
            for v in recent_violations:
                reason = v.blocked_reason or "Unknown"
                violation_types[reason] = violation_types.get(reason, 0) + 1
            
            return {
                "agent_id": agent_id,
                "title": "频繁策略违规",
                "description": f"Agent在1小时内触发{len(recent_violations)}次策略阻止",
                "alert_type": "policy_violation",
                "severity": RiskLevel.HIGH,
                "status": "open",
                "evidence": {
                    "violation_count": len(recent_violations),
                    "violation_types": violation_types,
                    "time_window": "1 hour"
                }
            }
        
        return None
    
    def _check_security_risks(self, agent_id: int, db: Session) -> Optional[Dict]:
        """检查安全风险"""
        # 获取高风险请求
        high_risk_requests = db.query(NetworkRequest).filter(
            and_(
                NetworkRequest.agent_id == agent_id,
                NetworkRequest.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
                NetworkRequest.request_time >= datetime.utcnow() - timedelta(hours=1)
            )
        ).all()
        
        if not high_risk_requests:
            return None
        
        # 统计风险类型
        risk_types = {}
        for req in high_risk_requests:
            if req.intent_analysis:
                # 提取风险关键词
                if "注入" in req.intent_analysis or "injection" in req.intent_analysis.lower():
                    risk_types["injection"] = risk_types.get("injection", 0) + 1
                if "扫描" in req.intent_analysis or "scan" in req.intent_analysis.lower():
                    risk_types["scanning"] = risk_types.get("scanning", 0) + 1
                if "窃取" in req.intent_analysis or "steal" in req.intent_analysis.lower():
                    risk_types["data_theft"] = risk_types.get("data_theft", 0) + 1
        
        if len(high_risk_requests) >= 3 or risk_types:
            severity = RiskLevel.CRITICAL if len(high_risk_requests) >= 5 else RiskLevel.HIGH
            
            return {
                "agent_id": agent_id,
                "title": "检测到安全风险",
                "description": f"发现{len(high_risk_requests)}个高风险请求" + 
                              (f"，包括: {', '.join(risk_types.keys())}" if risk_types else ""),
                "alert_type": "security",
                "severity": severity,
                "status": "open",
                "evidence": {
                    "high_risk_count": len(high_risk_requests),
                    "risk_types": risk_types,
                    "recent_requests": [
                        {
                            "url": r.url,
                            "risk_level": r.risk_level.value if r.risk_level else None,
                            "intent": r.intent_analysis[:100] if r.intent_analysis else None
                        }
                        for r in high_risk_requests[:5]
                    ]
                }
            }
        
        return None
    
    def acknowledge_alert(self, alert_id: int, db: Session) -> bool:
        """确认告警"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = "acknowledged"
        db.commit()
        
        logger.info(f"Alert {alert_id} acknowledged")
        return True
    
    def resolve_alert(self, alert_id: int, db: Session) -> bool:
        """解决告警"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Alert {alert_id} resolved")
        return True
    
    def get_active_alerts(self, agent_id: Optional[int] = None, db: Session = None) -> List[Dict]:
        """获取活动告警"""
        query = db.query(Alert).filter(Alert.status.in_(["open", "acknowledged"]))
        
        if agent_id:
            query = query.filter(Alert.agent_id == agent_id)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        
        return [{
            "id": a.id,
            "agent_id": a.agent_id,
            "title": a.title,
            "description": a.description,
            "alert_type": a.alert_type,
            "severity": a.severity.value if a.severity else None,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "evidence": a.evidence
        } for a in alerts]
    
    def get_alert_statistics(self, db: Session) -> Dict:
        """获取告警统计"""
        # 总告警数
        total_alerts = db.query(Alert).count()
        
        # 按状态统计
        status_counts = db.query(
            Alert.status,
            func.count(Alert.id)
        ).group_by(Alert.status).all()
        
        # 按严重程度统计
        severity_counts = db.query(
            Alert.severity,
            func.count(Alert.id)
        ).group_by(Alert.severity).all()
        
        # 按类型统计
        type_counts = db.query(
            Alert.alert_type,
            func.count(Alert.id)
        ).group_by(Alert.alert_type).all()
        
        # 最近24小时告警数
        recent_alerts = db.query(Alert).filter(
            Alert.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            "total_alerts": total_alerts,
            "status_distribution": {status: count for status, count in status_counts},
            "severity_distribution": {
                sev.value if sev else "unknown": count 
                for sev, count in severity_counts
            },
            "type_distribution": {alert_type: count for alert_type, count in type_counts},
            "recent_24h": recent_alerts
        }
    
    def auto_resolve_alerts(self, db: Session, max_age_hours: int = 24):
        """自动解决过期告警"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        old_alerts = db.query(Alert).filter(
            and_(
                Alert.status == "open",
                Alert.created_at < cutoff_time
            )
        ).all()
        
        for alert in old_alerts:
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
        
        db.commit()
        
        if old_alerts:
            logger.info(f"Auto-resolved {len(old_alerts)} old alerts")
        
        return len(old_alerts)

# 全局告警系统实例
alert_system = AlertSystem()

"""网络数据分析和可视化模块"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from sqlalchemy.orm import Session

from ..models import NetworkRequest, Agent, Alert, AuditLog

logger = logging.getLogger(__name__)

class NetworkAnalyticsManager:
    """网络数据分析管理器"""
    
    def __init__(self):
        # 分析配置
        self.analysis_config = {
            "time_windows": {
                "hour": 3600,
                "day": 86400,
                "week": 604800,
                "month": 2592000
            },
            "top_n": 10,  # 展示前N个数据
            "anomaly_threshold": 3.0  # 异常检测阈值
        }
    
    def collect_network_data(self, user_id: int, time_window: int, db: Session) -> List[NetworkRequest]:
        """收集网络请求数据"""
        try:
            # 获取用户的所有智能体
            agents = db.query(Agent).filter(Agent.user_id == user_id).all()
            agent_ids = [agent.id for agent in agents]
            
            # 获取时间窗口内的网络请求
            cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
            requests = db.query(NetworkRequest).filter(
                NetworkRequest.agent_id.in_(agent_ids),
                NetworkRequest.request_time >= cutoff_time
            ).all()
            
            return requests
            
        except Exception as e:
            logger.error(f"Error collecting network data: {e}")
            raise
    
    def analyze_network_traffic(self, requests: List[NetworkRequest]) -> Dict[str, Any]:
        """分析网络流量"""
        if not requests:
            return {
                "total_requests": 0,
                "request_types": {},
                "status_codes": {},
                "response_times": [],
                "top_urls": [],
                "time_distribution": {},
                "anomalies": []
            }
        
        # 分析请求类型
        request_types = Counter(req.request_type for req in requests if req.request_type)
        
        # 分析状态码
        status_codes = Counter(req.status_code for req in requests if req.status_code)
        
        # 分析响应时间
        response_times = [req.response_time for req in requests if req.response_time]
        
        # 分析URL
        url_counter = Counter(req.request_url for req in requests if req.request_url)
        top_urls = url_counter.most_common(self.analysis_config["top_n"])
        
        # 分析时间分布
        time_distribution = defaultdict(int)
        for req in requests:
            hour = req.request_time.hour if req.request_time else 0
            time_distribution[hour] += 1
        
        # 检测异常
        anomalies = self._detect_anomalies(requests, response_times)
        
        return {
            "total_requests": len(requests),
            "request_types": dict(request_types),
            "status_codes": dict(status_codes),
            "response_times": response_times,
            "top_urls": top_urls,
            "time_distribution": dict(time_distribution),
            "anomalies": anomalies
        }
    
    def _detect_anomalies(self, requests: List[NetworkRequest], response_times: List[float]) -> List[Dict[str, Any]]:
        """检测异常"""
        anomalies = []
        
        # 检测响应时间异常
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            std_response_time = (sum((t - avg_response_time) ** 2 for t in response_times) / len(response_times)) ** 0.5
            
            for req in requests:
                if req.response_time and req.response_time > avg_response_time + self.analysis_config["anomaly_threshold"] * std_response_time:
                    anomalies.append({
                        "type": "response_time_anomaly",
                        "severity": "medium",
                        "message": f"异常响应时间: {req.response_time:.2f}s",
                        "request_url": req.request_url,
                        "request_time": req.request_time.isoformat()
                    })
        
        # 检测错误率异常
        error_count = sum(1 for req in requests if req.status_code and req.status_code >= 400)
        error_rate = error_count / len(requests) if requests else 0
        
        if error_rate > 0.1:  # 错误率超过10%视为异常
            anomalies.append({
                "type": "error_rate_anomaly",
                "severity": "high",
                "message": f"异常错误率: {error_rate:.2f}",
                "error_count": error_count,
                "total_requests": len(requests)
            })
        
        return anomalies
    
    def analyze_agent_behavior(self, agent_id: int, time_window: int, db: Session) -> Dict[str, Any]:
        """分析智能体行为"""
        try:
            # 获取时间窗口内的网络请求
            cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
            requests = db.query(NetworkRequest).filter(
                NetworkRequest.agent_id == agent_id,
                NetworkRequest.request_time >= cutoff_time
            ).all()
            
            # 获取时间窗口内的审计日志
            audit_logs = db.query(AuditLog).filter(
                AuditLog.agent_id == agent_id,
                AuditLog.created_at >= cutoff_time
            ).all()
            
            # 获取时间窗口内的告警
            alerts = db.query(Alert).filter(
                Alert.agent_id == agent_id,
                Alert.created_at >= cutoff_time
            ).all()
            
            # 分析网络请求
            traffic_analysis = self.analyze_network_traffic(requests)
            
            # 分析审计日志
            log_analysis = {
                "total_logs": len(audit_logs),
                "log_types": Counter(log.log_type for log in audit_logs),
                "event_types": Counter(log.event for log in audit_logs)
            }
            
            # 分析告警
            alert_analysis = {
                "total_alerts": len(alerts),
                "alert_types": Counter(alert.alert_type for alert in alerts),
                "severities": Counter(alert.severity for alert in alerts)
            }
            
            return {
                "agent_id": agent_id,
                "time_window": time_window,
                "traffic_analysis": traffic_analysis,
                "log_analysis": log_analysis,
                "alert_analysis": alert_analysis,
                "summary": self._generate_behavior_summary(traffic_analysis, log_analysis, alert_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing agent behavior: {e}")
            raise
    
    def _generate_behavior_summary(self, traffic_analysis: Dict, log_analysis: Dict, alert_analysis: Dict) -> Dict[str, Any]:
        """生成行为摘要"""
        # 计算风险分数
        risk_score = 0
        
        # 基于错误率计算风险
        error_count = sum(count for code, count in traffic_analysis.get("status_codes", {}).items() if code >= 400)
        total_requests = traffic_analysis.get("total_requests", 0)
        error_rate = error_count / total_requests if total_requests > 0 else 0
        risk_score += error_rate * 30
        
        # 基于告警计算风险
        high_severity_alerts = alert_analysis.get("severities", {}).get("high", 0)
        risk_score += high_severity_alerts * 10
        
        # 基于异常计算风险
        anomalies_count = len(traffic_analysis.get("anomalies", []))
        risk_score += anomalies_count * 5
        
        # 确定风险等级
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "recommendations": self._generate_recommendations(risk_level, traffic_analysis, alert_analysis)
        }
    
    def _generate_recommendations(self, risk_level: str, traffic_analysis: Dict, alert_analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("立即审查智能体配置，修复高风险问题")
            recommendations.append("检查网络连接和API配置")
            recommendations.append("考虑限制智能体的网络访问权限")
        elif risk_level == "medium":
            recommendations.append("审查智能体的网络行为模式")
            recommendations.append("优化智能体的请求频率和响应处理")
        else:
            recommendations.append("智能体行为正常，继续保持良好实践")
        
        # 基于具体问题生成建议
        error_count = sum(count for code, count in traffic_analysis.get("status_codes", {}).items() if code >= 400)
        if error_count > 0:
            recommendations.append("检查并修复导致错误的API调用")
        
        anomalies_count = len(traffic_analysis.get("anomalies", []))
        if anomalies_count > 0:
            recommendations.append("调查并解决网络异常问题")
        
        high_severity_alerts = alert_analysis.get("severities", {}).get("high", 0)
        if high_severity_alerts > 0:
            recommendations.append("处理所有高严重性告警")
        
        return recommendations
    
    def generate_network_report(self, user_id: int, time_window: int, db: Session) -> Dict[str, Any]:
        """生成网络分析报告"""
        try:
            # 收集网络数据
            requests = self.collect_network_data(user_id, time_window, db)
            
            # 分析网络流量
            traffic_analysis = self.analyze_network_traffic(requests)
            
            # 获取用户的所有智能体
            agents = db.query(Agent).filter(Agent.user_id == user_id).all()
            
            # 分析每个智能体的行为
            agent_analyses = []
            for agent in agents:
                agent_analysis = self.analyze_agent_behavior(agent.id, time_window, db)
                agent_analyses.append({
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "analysis": agent_analysis
                })
            
            # 按风险分数排序
            agent_analyses.sort(key=lambda x: x["analysis"]["summary"]["risk_score"], reverse=True)
            
            return {
                "report_time": datetime.utcnow().isoformat(),
                "time_window": time_window,
                "total_requests": traffic_analysis["total_requests"],
                "overall_analysis": traffic_analysis,
                "agent_analyses": agent_analyses,
                "summary": self._generate_report_summary(traffic_analysis, agent_analyses)
            }
            
        except Exception as e:
            logger.error(f"Error generating network report: {e}")
            raise
    
    def _generate_report_summary(self, traffic_analysis: Dict, agent_analyses: List[Dict]) -> Dict[str, Any]:
        """生成报告摘要"""
        # 计算平均风险分数
        total_risk_score = sum(analysis["analysis"]["summary"]["risk_score"] for analysis in agent_analyses)
        avg_risk_score = total_risk_score / len(agent_analyses) if agent_analyses else 0
        
        # 统计风险等级分布
        risk_levels = Counter(analysis["analysis"]["summary"]["risk_level"] for analysis in agent_analyses)
        
        # 找出风险最高的智能体
        high_risk_agents = [analysis for analysis in agent_analyses if analysis["analysis"]["summary"]["risk_level"] == "high"]
        
        return {
            "average_risk_score": avg_risk_score,
            "risk_level_distribution": dict(risk_levels),
            "high_risk_agents_count": len(high_risk_agents),
            "recommendations": [
                "定期审查智能体的网络行为",
                "优化智能体的网络请求模式",
                "实施网络访问控制策略",
                "监控并处理异常网络行为"
            ]
        }

# 初始化网络分析管理器
network_analytics_manager = NetworkAnalyticsManager()

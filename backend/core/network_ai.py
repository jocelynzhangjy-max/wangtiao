"""
AI驱动的网络智能分析模块
使用轻量级AI模型分析网络流量和智能体行为
"""
import json
import logging
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from collections import defaultdict

from backend.models import (
    NetworkRequest, Agent, AuditLog, Alert,
    RiskLevel, PolicyAction
)
from backend.core.alert_system import alert_system

logger = logging.getLogger(__name__)

class NetworkAIAnalyzer:
    """网络智能分析器"""
    
    def __init__(self):
        self.model = self._initialize_model()
        self.anomaly_threshold = 0.7
        self.prediction_history = defaultdict(list)
        self.agent_profiles = {}
        self.network_patterns = {}
    
    def _initialize_model(self):
        """初始化轻量级AI模型"""
        # 这里使用简化的模型实现，实际应用中可以使用更复杂的模型
        # 例如：使用scikit-learn或TensorFlow Lite
        return {
            "anomaly_detector": self._detect_anomaly,
            "pattern_recognizer": self._recognize_pattern,
            "predictor": self._predict_agent_behavior
        }
    
    def analyze_network_traffic(self, network_requests: List[NetworkRequest]) -> Dict:
        """分析网络流量"""
        if not network_requests:
            return {"status": "no_data"}
        
        # 提取特征
        features = self._extract_features(network_requests)
        
        # 检测异常
        anomalies = self._detect_anomalies(features)
        
        # 识别模式
        patterns = self._identify_patterns(network_requests)
        
        # 生成分析报告
        report = {
            "total_requests": len(network_requests),
            "anomalies": anomalies,
            "patterns": patterns,
            "summary": self._generate_summary(network_requests, anomalies, patterns)
        }
        
        return report
    
    def analyze_agent_behavior(self, agent_id: int, db: Session, time_window: int = 3600) -> Dict:
        """分析智能体行为"""
        # 获取时间窗口内的网络请求
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id == agent_id,
            NetworkRequest.request_time >= cutoff_time
        ).all()
        
        if not requests:
            return {"status": "no_data"}
        
        # 分析行为
        behavior_analysis = {
            "request_count": len(requests),
            "request_types": self._analyze_request_types(requests),
            "targets": self._analyze_targets(requests),
            "risk_levels": self._analyze_risk_levels(requests),
            "anomalies": self._detect_agent_anomalies(requests, agent_id),
            "predictions": self._predict_agent_behavior(agent_id, requests)
        }
        
        # 更新智能体 profile
        self._update_agent_profile(agent_id, behavior_analysis)
        
        return behavior_analysis
    
    def detect_network_anomalies(self, db: Session, time_window: int = 3600) -> List[Dict]:
        """检测网络异常"""
        # 获取时间窗口内的所有网络请求
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.request_time >= cutoff_time
        ).all()
        
        if not requests:
            return []
        
        # 按智能体分组分析
        agent_requests = defaultdict(list)
        for req in requests:
            agent_requests[req.agent_id].append(req)
        
        anomalies = []
        for agent_id, agent_reqs in agent_requests.items():
            agent_anomalies = self._detect_agent_anomalies(agent_reqs, agent_id)
            anomalies.extend(agent_anomalies)
        
        return anomalies
    
    def predict_network_trends(self, db: Session, time_window: int = 3600, prediction_horizon: int = 3600) -> Dict:
        """预测网络趋势"""
        # 获取历史数据
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.request_time >= cutoff_time
        ).all()
        
        if not requests:
            return {"status": "no_data"}
        
        # 分析历史模式
        hourly_patterns = self._analyze_hourly_patterns(requests)
        
        # 预测未来趋势
        predictions = self._predict_future_trends(hourly_patterns, prediction_horizon)
        
        return {
            "historical_patterns": hourly_patterns,
            "predictions": predictions
        }
    
    def _extract_features(self, requests: List[NetworkRequest]) -> List[Dict]:
        """提取网络请求特征"""
        features = []
        for req in requests:
            feature = {
                "agent_id": req.agent_id,
                "method": req.method,
                "url_length": len(req.url),
                "body_length": len(req.body) if req.body else 0,
                "risk_score": req.risk_score or 0,
                "is_blocked": 1 if req.policy_action == PolicyAction.DENY else 0
            }
            features.append(feature)
        return features
    
    def _detect_anomalies(self, features: List[Dict]) -> List[Dict]:
        """检测异常"""
        anomalies = []
        for feature in features:
            anomaly_score = self._detect_anomaly(feature)
            if anomaly_score > self.anomaly_threshold:
                anomalies.append({
                    "agent_id": feature["agent_id"],
                    "anomaly_score": anomaly_score,
                    "timestamp": datetime.utcnow().isoformat()
                })
        return anomalies
    
    def _detect_anomaly(self, feature: Dict) -> float:
        """检测单个请求的异常"""
        # 简化的异常检测算法
        score = 0.0
        
        # 基于风险评分
        score += feature["risk_score"] / 100.0 * 0.4
        
        # 基于请求长度
        if feature["url_length"] > 1000:
            score += 0.2
        if feature["body_length"] > 5000:
            score += 0.2
        
        # 基于是否被阻止
        if feature["is_blocked"]:
            score += 0.2
        
        return min(score, 1.0)
    
    def _identify_patterns(self, requests: List[NetworkRequest]) -> List[Dict]:
        """识别网络模式"""
        patterns = []
        
        # 按目标URL分组
        url_patterns = defaultdict(list)
        for req in requests:
            url_patterns[req.url].append(req)
        
        for url, url_reqs in url_patterns.items():
            if len(url_reqs) > 5:
                patterns.append({
                    "pattern_type": "frequent_url",
                    "target": url,
                    "count": len(url_reqs),
                    "agents": list(set(req.agent_id for req in url_reqs))
                })
        
        # 按智能体分组
        agent_patterns = defaultdict(list)
        for req in requests:
            agent_patterns[req.agent_id].append(req)
        
        for agent_id, agent_reqs in agent_patterns.items():
            if len(agent_reqs) > 10:
                methods = defaultdict(int)
                for req in agent_reqs:
                    methods[req.method] += 1
                
                patterns.append({
                    "pattern_type": "agent_activity",
                    "agent_id": agent_id,
                    "request_count": len(agent_reqs),
                    "methods": dict(methods)
                })
        
        return patterns
    
    def _generate_summary(self, requests: List[NetworkRequest], anomalies: List[Dict], patterns: List[Dict]) -> Dict:
        """生成分析摘要"""
        total_requests = len(requests)
        blocked_requests = sum(1 for req in requests if req.policy_action == PolicyAction.DENY)
        high_risk_requests = sum(1 for req in requests if req.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
        
        return {
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "blocked_rate": blocked_requests / total_requests if total_requests > 0 else 0,
            "high_risk_requests": high_risk_requests,
            "high_risk_rate": high_risk_requests / total_requests if total_requests > 0 else 0,
            "anomaly_count": len(anomalies),
            "pattern_count": len(patterns)
        }
    
    def _analyze_request_types(self, requests: List[NetworkRequest]) -> Dict:
        """分析请求类型"""
        types = defaultdict(int)
        for req in requests:
            types[req.method] += 1
        return dict(types)
    
    def _analyze_targets(self, requests: List[NetworkRequest]) -> Dict:
        """分析目标"""
        targets = defaultdict(int)
        for req in requests:
            # 提取域名或主要路径
            target = req.url.split('//')[-1].split('/')[0]
            targets[target] += 1
        return dict(targets)
    
    def _analyze_risk_levels(self, requests: List[NetworkRequest]) -> Dict:
        """分析风险等级"""
        levels = defaultdict(int)
        for req in requests:
            if req.risk_level:
                levels[req.risk_level.value] += 1
        return dict(levels)
    
    def _detect_agent_anomalies(self, requests: List[NetworkRequest], agent_id: int) -> List[Dict]:
        """检测智能体异常"""
        anomalies = []
        
        # 检查请求频率
        if len(requests) > 50:  # 阈值可以根据实际情况调整
            anomalies.append({
                "type": "high_request_rate",
                "agent_id": agent_id,
                "severity": "medium",
                "description": f"Agent {agent_id} has high request rate: {len(requests)} requests"
            })
        
        # 检查高风险请求
        high_risk_count = sum(1 for req in requests if req.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
        if high_risk_count > 5:
            anomalies.append({
                "type": "high_risk_requests",
                "agent_id": agent_id,
                "severity": "high",
                "description": f"Agent {agent_id} has {high_risk_count} high-risk requests"
            })
        
        # 检查被阻止的请求
        blocked_count = sum(1 for req in requests if req.policy_action == PolicyAction.DENY)
        if blocked_count > 10:
            anomalies.append({
                "type": "high_blocked_rate",
                "agent_id": agent_id,
                "severity": "medium",
                "description": f"Agent {agent_id} has {blocked_count} blocked requests"
            })
        
        return anomalies
    
    def _predict_agent_behavior(self, agent_id: int, requests: List[NetworkRequest]) -> Dict:
        """预测智能体行为"""
        # 基于历史行为预测
        prediction = {
            "next_hour_requests": len(requests),
            "likely_targets": self._predict_likely_targets(requests),
            "risk_level": self._predict_risk_level(requests)
        }
        
        # 存储预测历史
        self.prediction_history[agent_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": prediction
        })
        
        # 限制历史记录长度
        if len(self.prediction_history[agent_id]) > 24:
            self.prediction_history[agent_id] = self.prediction_history[agent_id][-24:]
        
        return prediction
    
    def _predict_likely_targets(self, requests: List[NetworkRequest]) -> List[str]:
        """预测可能的目标"""
        targets = defaultdict(int)
        for req in requests:
            target = req.url.split('//')[-1].split('/')[0]
            targets[target] += 1
        
        # 返回最可能的目标
        sorted_targets = sorted(targets.items(), key=lambda x: x[1], reverse=True)
        return [target for target, _ in sorted_targets[:3]]
    
    def _predict_risk_level(self, requests: List[NetworkRequest]) -> str:
        """预测风险等级"""
        if not requests:
            return "low"
        
        risk_scores = [req.risk_score or 0 for req in requests]
        avg_score = sum(risk_scores) / len(risk_scores)
        
        if avg_score > 70:
            return "critical"
        elif avg_score > 50:
            return "high"
        elif avg_score > 30:
            return "medium"
        else:
            return "low"
    
    def _update_agent_profile(self, agent_id: int, behavior_analysis: Dict):
        """更新智能体配置文件"""
        self.agent_profiles[agent_id] = {
            "last_updated": datetime.utcnow().isoformat(),
            "behavior": behavior_analysis
        }
    
    def _analyze_hourly_patterns(self, requests: List[NetworkRequest]) -> Dict:
        """分析每小时模式"""
        hourly_patterns = defaultdict(int)
        for req in requests:
            hour = req.request_time.strftime("%Y-%m-%d %H:00")
            hourly_patterns[hour] += 1
        return dict(hourly_patterns)
    
    def _predict_future_trends(self, hourly_patterns: Dict, prediction_horizon: int) -> List[Dict]:
        """预测未来趋势"""
        predictions = []
        
        # 基于历史模式预测
        if hourly_patterns:
            avg_requests = sum(hourly_patterns.values()) / len(hourly_patterns)
            
            # 预测未来几个小时
            for i in range(1, prediction_horizon // 3600 + 1):
                future_time = datetime.utcnow() + timedelta(hours=i)
                predictions.append({
                    "timestamp": future_time.isoformat(),
                    "predicted_requests": int(avg_requests),
                    "confidence": 0.7  # 简化的置信度
                })
        
        return predictions
    
    def _recognize_pattern(self, requests: List[NetworkRequest]) -> List[Dict]:
        """识别网络模式"""
        # 简化的模式识别
        patterns = []
        
        # 检查是否有扫描行为
        urls = [req.url for req in requests]
        if len(set(urls)) / len(urls) < 0.3:
            patterns.append({
                "pattern": "scan_attempt",
                "confidence": 0.8
            })
        
        return patterns
    
    def get_agent_profile(self, agent_id: int) -> Optional[Dict]:
        """获取智能体配置文件"""
        return self.agent_profiles.get(agent_id)
    
    def get_network_statistics(self) -> Dict:
        """获取网络统计信息"""
        return {
            "total_agents": len(self.agent_profiles),
            "prediction_history_size": sum(len(hist) for hist in self.prediction_history.values())
        }

# 全局网络AI分析器实例
network_ai_analyzer = NetworkAIAnalyzer()

"""
意图审计模块
使用轻量级大模型分析Agent发出的网络请求意图
"""
import json
import logging
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IntentAnalysisResult:
    """意图分析结果"""
    intent: str
    confidence: float
    risk_level: str
    is_malicious: bool
    details: Dict

class IntentAnalyzer:
    """意图分析器"""
    
    def __init__(self):
        # 轻量级规则引擎（模拟LLM分析）
        self.intent_rules = self._load_intent_rules()
        self.malicious_patterns = self._load_malicious_patterns()
    
    def _load_intent_rules(self) -> Dict:
        """加载意图识别规则"""
        return {
            "data_query": {
                "patterns": [
                    r"查询|搜索|获取|查找|检索|fetch|query|search|get|retrieve",
                    r"数据|信息|记录|内容|data|info|record|content"
                ],
                "keywords": ["查询", "搜索", "获取", "fetch", "query", "search"],
                "risk": "low"
            },
            "data_modification": {
                "patterns": [
                    r"修改|更新|编辑|更改|update|modify|edit|change",
                    r"添加|创建|插入|新增|add|create|insert"
                ],
                "keywords": ["修改", "更新", "添加", "创建", "update", "modify", "add", "create"],
                "risk": "medium"
            },
            "data_deletion": {
                "patterns": [
                    r"删除|移除|清空|销毁|delete|remove|drop|truncate|clear",
                    r"全部|所有|整个|entire|all|whole"
                ],
                "keywords": ["删除", "移除", "delete", "remove", "drop"],
                "risk": "high"
            },
            "system_operation": {
                "patterns": [
                    r"执行|运行|调用|启动|execute|run|exec|call|invoke|start",
                    r"系统|命令|脚本|程序|system|command|script|program|shell"
                ],
                "keywords": ["执行", "运行", "调用", "execute", "run", "exec", "system", "command"],
                "risk": "high"
            },
            "file_operation": {
                "patterns": [
                    r"文件|文档|上传|下载|file|document|upload|download",
                    r"读取|写入|保存|加载|read|write|save|load"
                ],
                "keywords": ["文件", "上传", "下载", "file", "upload", "download", "read", "write"],
                "risk": "medium"
            },
            "network_scan": {
                "patterns": [
                    r"扫描|探测|发现|scan|probe|discover|detect",
                    r"端口|服务|主机|网络|port|service|host|network"
                ],
                "keywords": ["扫描", "探测", "scan", "probe", "port", "network"],
                "risk": "high"
            },
            "authentication": {
                "patterns": [
                    r"登录|认证|授权|身份|login|auth|authenticate|identity",
                    r"密码|令牌|密钥|凭证|password|token|key|credential"
                ],
                "keywords": ["登录", "认证", "密码", "令牌", "login", "auth", "password", "token"],
                "risk": "medium"
            },
            "configuration": {
                "patterns": [
                    r"配置|设置|参数|选项|config|setting|parameter|option",
                    r"修改|更改|更新|modify|change|update"
                ],
                "keywords": ["配置", "设置", "config", "setting", "modify"],
                "risk": "medium"
            }
        }
    
    def _load_malicious_patterns(self) -> list:
        """加载恶意行为模式"""
        return [
            {
                "name": "SQL注入",
                "patterns": [
                    r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(from|into|table|database)\b)",
                    r"(\b(or|and)\b\s*\d+\s*=\s*\d+)",
                    r"('|--|;|/\*|\*/)",
                    r"(\bexec\s*\(\s*@\w+)",
                    r"(union\s+select\s+null)"
                ],
                "severity": "critical",
                "description": "检测到可能的SQL注入攻击"
            },
            {
                "name": "命令注入",
                "patterns": [
                    r"(\b(sh|bash|cmd|powershell|python|ruby|perl)\b\s+-c\s+)",
                    r"([;&|]\s*\b(ls|cat|pwd|whoami|id|uname|ifconfig|ipconfig|netstat|ps|top)\b)",
                    r"(\b(curl|wget|nc|netcat)\b\s+-[a-zA-Z]*\s*)",
                    r"(`[^`]+`|\$\([^)]+\))"
                ],
                "severity": "critical",
                "description": "检测到可能的命令注入攻击"
            },
            {
                "name": "路径遍历",
                "patterns": [
                    r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/)",
                    r"(/etc/passwd|/etc/shadow|/proc/self|C:\\Windows\\System32)",
                    r"(file://|php://|data://|expect://)"
                ],
                "severity": "high",
                "description": "检测到可能的路径遍历攻击"
            },
            {
                "name": "XXE攻击",
                "patterns": [
                    r"(<!ENTITY\s+\w+\s+SYSTEM\s+)",
                    r"(<!DOCTYPE\s+\w+\s+\[)"
                ],
                "severity": "high",
                "description": "检测到可能的XXE攻击"
            },
            {
                "name": "SSRF攻击",
                "patterns": [
                    r"(http://(169\.254|127\.0\.0\.1|localhost|0\.0\.0\.0|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.))",
                    r"(file://|dict://|gopher://|ftp://|ldap://)"
                ],
                "severity": "high",
                "description": "检测到可能的SSRF攻击"
            },
            {
                "name": "暴力破解",
                "patterns": [
                    r"(\b(brute|force|guess|crack)\b)",
                    r"(password.*list|wordlist|dictionary)"
                ],
                "severity": "high",
                "description": "检测到可能的暴力破解尝试"
            },
            {
                "name": "数据窃取",
                "patterns": [
                    r"(\b(steal|exfiltrate|leak|dump|harvest)\b)",
                    r"(\b(sensitive|confidential|private|secret)\b.*\b(data|info|file)\b)"
                ],
                "severity": "critical",
                "description": "检测到可能的数据窃取行为"
            },
            {
                "name": "权限提升",
                "patterns": [
                    r"(\b(elevate|escalate|privilege|sudo|su\s+-)\b)",
                    r"(\b(chmod|chown)\b\s+\d{3,4})"
                ],
                "severity": "critical",
                "description": "检测到可能的权限提升尝试"
            }
        ]
    
    def analyze_request(
        self,
        method: str,
        url: str,
        headers: Dict,
        body: Optional[str],
        original_task: Optional[str] = None
    ) -> IntentAnalysisResult:
        """
        分析网络请求的意图
        """
        # 构建分析文本
        analysis_text = f"{method} {url}"
        if body:
            analysis_text += f" Body: {body[:500]}"  # 限制长度
        
        # 1. 识别意图类型
        intent_type, confidence = self._identify_intent(analysis_text)
        
        # 2. 检测恶意行为
        is_malicious, threats = self._detect_malicious_behavior(analysis_text)
        
        # 3. 检查任务偏离
        task_deviation = None
        if original_task:
            task_deviation = self._check_task_deviation(intent_type, original_task)
        
        # 4. 评估风险等级
        risk_level = self._assess_risk(
            intent_type, 
            is_malicious, 
            threats, 
            task_deviation,
            method,
            url
        )
        
        # 5. 生成详细分析
        details = {
            "intent_type": intent_type,
            "confidence": confidence,
            "threats": threats,
            "task_deviation": task_deviation,
            "analysis_text": analysis_text[:200],  # 截断保存
            "indicators": self._extract_indicators(analysis_text)
        }
        
        # 生成意图描述
        intent_description = self._generate_intent_description(
            intent_type, 
            is_malicious, 
            threats,
            task_deviation
        )
        
        return IntentAnalysisResult(
            intent=intent_description,
            confidence=confidence,
            risk_level=risk_level,
            is_malicious=is_malicious,
            details=details
        )
    
    def _identify_intent(self, text: str) -> Tuple[str, float]:
        """识别意图类型"""
        text_lower = text.lower()
        
        best_match = "unknown"
        best_score = 0.0
        
        for intent_type, rules in self.intent_rules.items():
            score = 0
            
            # 检查关键词匹配
            for keyword in rules["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
            
            # 检查正则匹配
            for pattern in rules["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2
            
            # 归一化分数
            max_possible = len(rules["keywords"]) + len(rules["patterns"]) * 2
            normalized_score = score / max_possible if max_possible > 0 else 0
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_match = intent_type
        
        return best_match, min(best_score, 1.0)
    
    def _detect_malicious_behavior(self, text: str) -> Tuple[bool, list]:
        """检测恶意行为"""
        threats = []
        
        for pattern_def in self.malicious_patterns:
            for pattern in pattern_def["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    threats.append({
                        "name": pattern_def["name"],
                        "severity": pattern_def["severity"],
                        "description": pattern_def["description"],
                        "matched_pattern": pattern
                    })
                    break  # 每种威胁类型只记录一次
        
        is_malicious = len(threats) > 0
        return is_malicious, threats
    
    def _check_task_deviation(self, intent_type: str, original_task: str) -> Optional[Dict]:
        """检查是否偏离原始任务"""
        task_lower = original_task.lower()
        
        # 定义任务-意图映射
        task_intent_map = {
            "查询": ["data_query"],
            "搜索": ["data_query"],
            "查资料": ["data_query"],
            "获取": ["data_query"],
            "修改": ["data_modification"],
            "更新": ["data_modification"],
            "编辑": ["data_modification"],
            "删除": ["data_deletion"],
            "上传": ["file_operation"],
            "下载": ["file_operation"],
            "配置": ["configuration"],
            "设置": ["configuration"]
        }
        
        # 检查意图是否与任务匹配
        expected_intents = []
        for task_keyword, intents in task_intent_map.items():
            if task_keyword in task_lower:
                expected_intents.extend(intents)
        
        if expected_intents and intent_type not in expected_intents:
            # 计算偏离程度
            deviation_score = 0.8  # 默认高度偏离
            
            # 某些意图组合是合理的
            reasonable_combinations = {
                "data_query": ["data_modification", "file_operation"],
                "data_modification": ["data_query", "file_operation"],
                "file_operation": ["data_query", "data_modification"]
            }
            
            if intent_type in reasonable_combinations:
                if any(ei in reasonable_combinations[intent_type] for ei in expected_intents):
                    deviation_score = 0.4  # 中度偏离
            
            return {
                "original_task": original_task,
                "expected_intents": expected_intents,
                "actual_intent": intent_type,
                "deviation_score": deviation_score,
                "is_deviated": deviation_score > 0.5
            }
        
        return None
    
    def _assess_risk(
        self,
        intent_type: str,
        is_malicious: bool,
        threats: list,
        task_deviation: Optional[Dict],
        method: str,
        url: str
    ) -> str:
        """评估风险等级"""
        # 基础风险
        base_risk = self.intent_rules.get(intent_type, {}).get("risk", "low")
        
        # 根据威胁调整风险
        if is_malicious:
            severities = [t["severity"] for t in threats]
            if "critical" in severities:
                return "critical"
            elif "high" in severities:
                return "high"
            else:
                return "medium"
        
        # 根据任务偏离调整
        if task_deviation and task_deviation.get("is_deviated"):
            if base_risk == "low":
                return "medium"
            elif base_risk == "medium":
                return "high"
        
        # 根据HTTP方法调整
        if method in ["DELETE", "PUT", "PATCH"]:
            if base_risk == "low":
                return "medium"
        
        # 检查敏感URL模式
        sensitive_patterns = ["admin", "config", "password", "secret", "token"]
        if any(p in url.lower() for p in sensitive_patterns):
            if base_risk == "low":
                return "medium"
        
        return base_risk
    
    def _extract_indicators(self, text: str) -> list:
        """提取威胁指标"""
        indicators = []
        
        # 提取IP地址
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, text)
        indicators.extend([{"type": "ip", "value": ip} for ip in ips])
        
        # 提取URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        indicators.extend([{"type": "url", "value": url} for url in urls])
        
        # 提取可能的敏感关键词
        sensitive_keywords = ["password", "token", "secret", "key", "credential", "auth"]
        for keyword in sensitive_keywords:
            if keyword in text.lower():
                indicators.append({"type": "keyword", "value": keyword})
        
        return indicators
    
    def _generate_intent_description(
        self,
        intent_type: str,
        is_malicious: bool,
        threats: list,
        task_deviation: Optional[Dict]
    ) -> str:
        """生成意图描述"""
        descriptions = {
            "data_query": "查询数据",
            "data_modification": "修改数据",
            "data_deletion": "删除数据",
            "system_operation": "执行系统操作",
            "file_operation": "文件操作",
            "network_scan": "网络扫描",
            "authentication": "身份认证",
            "configuration": "配置修改",
            "unknown": "未知操作"
        }
        
        base_desc = descriptions.get(intent_type, "未知操作")
        
        parts = [base_desc]
        
        if is_malicious:
            threat_names = [t["name"] for t in threats]
            parts.append(f"[检测到威胁: {', '.join(threat_names)}]")
        
        if task_deviation and task_deviation.get("is_deviated"):
            parts.append(f"[偏离任务: {task_deviation['original_task']}]")
        
        return " - ".join(parts)

# 全局意图分析器实例
intent_analyzer = IntentAnalyzer()

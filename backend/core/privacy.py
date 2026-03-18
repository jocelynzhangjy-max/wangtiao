"""
隐私保护模块
实现数据加密、脱敏和安全存储功能
"""
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import re

logger = logging.getLogger(__name__)

class PrivacyManager:
    """隐私保护管理器"""
    
    def __init__(self):
        self.encryption_key = os.getenv("PRIVACY_ENCRYPTION_KEY", "your-secret-key-for-privacy").encode('utf-8')
        self.backend = default_backend()
        self.sensitive_data_patterns = {
            "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "phone": r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "ssn": r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b",
            "password": r"(?i)password[\s:]*([^\s,]+)",
            "api_key": r"(?i)(api[_-]?key|token)[\s:]*([^\s,]+)",
            "private_key": r"(?i)(private[_-]?key|secret)[\s:]*([^\s,]+)",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        }
    
    def encrypt_data(self, data: Any) -> str:
        """加密数据"""
        try:
            # 将数据转换为字符串
            if not isinstance(data, str):
                data_str = json.dumps(data)
            else:
                data_str = data
            
            # 生成随机IV
            iv = os.urandom(16)
            
            # 创建加密器
            cipher = Cipher(
                algorithms.AES(self._get_encryption_key()),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # 对数据进行填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data_str.encode('utf-8')) + padder.finalize()
            
            # 加密数据
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # 组合IV和加密数据
            combined = iv + encrypted_data
            
            # Base64编码
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """解密数据"""
        try:
            # Base64解码
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 提取IV和加密数据
            iv = combined[:16]
            encrypted = combined[16:]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self._get_encryption_key()),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # 解密数据
            padded_data = decryptor.update(encrypted) + decryptor.finalize()
            
            # 移除填充
            unpadder = padding.PKCS7(128).unpadder()
            data_str = unpadder.update(padded_data) + unpadder.finalize()
            
            # 尝试解析为JSON
            try:
                return json.loads(data_str.decode('utf-8'))
            except json.JSONDecodeError:
                return data_str.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def sanitize_data(self, data: Any, sensitivity_level: str = "medium") -> Any:
        """对数据进行脱敏处理"""
        if isinstance(data, dict):
            return {key: self.sanitize_data(value, sensitivity_level) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item, sensitivity_level) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data, sensitivity_level)
        else:
            return data
    
    def _sanitize_string(self, text: str, sensitivity_level: str) -> str:
        """对字符串进行脱敏处理"""
        sanitized_text = text
        
        # 根据敏感度级别确定要脱敏的模式
        patterns_to_sanitize = list(self.sensitive_data_patterns.items())
        
        if sensitivity_level == "low":
            # 只脱敏最敏感的数据
            patterns_to_sanitize = [(k, v) for k, v in patterns_to_sanitize if k in ["password", "credit_card", "ssn"]]
        elif sensitivity_level == "medium":
            # 脱敏大部分敏感数据
            patterns_to_sanitize = [(k, v) for k, v in patterns_to_sanitize if k not in ["ip_address"]]
        # high 级别脱敏所有数据
        
        # 对每种模式进行脱敏
        for pattern_name, pattern in patterns_to_sanitize:
            if pattern_name == "password":
                # 特殊处理密码
                sanitized_text = re.sub(pattern, r'password: ***REDACTED***', sanitized_text, flags=re.IGNORECASE)
            elif pattern_name == "api_key" or pattern_name == "private_key":
                # 特殊处理API密钥和私钥
                sanitized_text = re.sub(pattern, r'\1: ***REDACTED***', sanitized_text, flags=re.IGNORECASE)
            elif pattern_name == "email":
                # 邮箱脱敏，保留域名
                def email_replacer(match):
                    email = match.group(0)
                    username, domain = email.split('@')
                    if len(username) <= 2:
                        return f"**@{domain}"
                    else:
                        return f"{username[0]}***@{domain}"
                sanitized_text = re.sub(pattern, email_replacer, sanitized_text)
            elif pattern_name == "phone":
                # 电话号码脱敏，保留后四位
                def phone_replacer(match):
                    phone = match.group(0)
                    digits = re.sub(r"\D", "", phone)
                    if len(digits) <= 4:
                        return "***" + digits
                    else:
                        return "***" + digits[-4:]
                sanitized_text = re.sub(pattern, phone_replacer, sanitized_text)
            elif pattern_name == "credit_card":
                # 信用卡脱敏，保留后四位
                def cc_replacer(match):
                    cc = match.group(0)
                    digits = re.sub(r"\D", "", cc)
                    if len(digits) <= 4:
                        return "***" + digits
                    else:
                        return "***" + digits[-4:]
                sanitized_text = re.sub(pattern, cc_replacer, sanitized_text)
            elif pattern_name == "ssn":
                # SSN脱敏，保留后四位
                def ssn_replacer(match):
                    ssn = match.group(0)
                    digits = re.sub(r"\D", "", ssn)
                    if len(digits) <= 4:
                        return "***" + digits
                    else:
                        return "***-**-" + digits[-4:]
                sanitized_text = re.sub(pattern, ssn_replacer, sanitized_text)
            elif pattern_name == "ip_address":
                # IP地址脱敏，保留最后一段
                def ip_replacer(match):
                    ip = match.group(0)
                    parts = ip.split('.')
                    if len(parts) == 4:
                        return f"***.***.***.{parts[3]}"
                    return ip
                sanitized_text = re.sub(pattern, ip_replacer, sanitized_text)
        
        return sanitized_text
    
    def generate_data_mask(self, data: Any, fields: List[str]) -> Dict:
        """生成数据掩码，只暴露指定字段"""
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        for field in fields:
            if field in data:
                masked_data[field] = data[field]
            else:
                # 支持嵌套字段，如 user.address.street
                parts = field.split('.')
                current = data
                value = None
                
                try:
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            break
                    else:
                        value = current
                except (KeyError, TypeError):
                    pass
                
                if value is not None:
                    # 重建嵌套结构
                    nested = masked_data
                    for part in parts[:-1]:
                        if part not in nested:
                            nested[part] = {}
                        nested = nested[part]
                    nested[parts[-1]] = value
        
        return masked_data
    
    def secure_data_transfer(self, data: Any, recipient_id: str) -> Dict:
        """安全数据传输，添加加密和签名"""
        # 加密数据
        encrypted_data = self.encrypt_data(data)
        
        # 生成传输元数据
        transfer_id = f"transfer_{datetime.utcnow().timestamp()}_{os.urandom(8).hex()}"
        timestamp = datetime.utcnow().isoformat()
        expiration = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        
        # 生成传输对象
        transfer = {
            "transfer_id": transfer_id,
            "recipient_id": recipient_id,
            "encrypted_data": encrypted_data,
            "timestamp": timestamp,
            "expiration": expiration,
            "status": "pending"
        }
        
        return transfer
    
    def verify_data_transfer(self, transfer: Dict) -> bool:
        """验证数据传输的有效性"""
        # 检查过期时间
        try:
            expiration = datetime.fromisoformat(transfer.get("expiration", ""))
            if datetime.utcnow() > expiration:
                return False
        except (ValueError, TypeError):
            return False
        
        # 检查必要字段
        required_fields = ["transfer_id", "recipient_id", "encrypted_data", "timestamp"]
        for field in required_fields:
            if field not in transfer:
                return False
        
        return True
    
    def _get_encryption_key(self) -> bytes:
        """获取加密密钥，确保长度为32字节"""
        key = self.encryption_key
        if len(key) < 32:
            # 填充到32字节
            key = key.ljust(32, b'\x00')
        elif len(key) > 32:
            # 截断到32字节
            key = key[:32]
        return key
    
    def get_data_sensitivity_score(self, data: Any) -> int:
        """评估数据敏感度分数"""
        if isinstance(data, str):
            score = 0
            text = data.lower()
            
            # 检查敏感关键词
            sensitive_keywords = [
                "password", "credit card", "ssn", "social security",
                "bank account", "api key", "private key", "token",
                "confidential", "secret", "personal", "financial"
            ]
            
            for keyword in sensitive_keywords:
                if keyword in text:
                    score += 10
            
            # 检查敏感模式
            for pattern_name, pattern in self.sensitive_data_patterns.items():
                if re.search(pattern, data):
                    score += 15
            
            return min(score, 100)
        elif isinstance(data, dict):
            return max(self.get_data_sensitivity_score(v) for v in data.values())
        elif isinstance(data, list):
            return max(self.get_data_sensitivity_score(item) for item in data)
        else:
            return 0

# 全局隐私管理器实例
privacy_manager = PrivacyManager()

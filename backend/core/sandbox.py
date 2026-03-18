"""
沙箱网络管理模块
为每个AI Agent构建虚拟的隔离沙箱网络环境
"""
import subprocess
import json
import uuid
import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from backend.models import Agent, Sandbox, SandboxStatus
from backend.database import get_db

logger = logging.getLogger(__name__)

class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self):
        self.network_name = "agent-sandbox-network"
        self.base_subnet = "172.20.0.0/16"
        
    def _run_command(self, cmd: List[str], check: bool = True) -> tuple:
        """运行shell命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            return e.returncode, e.stdout, e.stderr
    
    def initialize_network(self) -> bool:
        """初始化沙箱网络"""
        # 检查网络是否已存在
        returncode, stdout, _ = self._run_command(
            ["docker", "network", "ls", "--filter", f"name={self.network_name}", "--format", "{{.Name}}"],
            check=False
        )
        
        if self.network_name in stdout:
            logger.info(f"Network {self.network_name} already exists")
            return True
        
        # 创建隔离网络
        returncode, _, stderr = self._run_command([
            "docker", "network", "create",
            "--driver", "bridge",
            "--subnet", self.base_subnet,
            "--internal",  # 内部网络，禁止外部访问
            "--opt", "com.docker.network.bridge.name=agent-sandbox-br",
            "--opt", "com.docker.network.bridge.enable_icc=true",
            "--opt", "com.docker.network.bridge.enable_ip_masquerade=false",
            self.network_name
        ], check=False)
        
        if returncode == 0:
            logger.info(f"Created sandbox network: {self.network_name}")
            return True
        else:
            logger.error(f"Failed to create network: {stderr}")
            return False
    
    def create_sandbox(self, agent_id: int, db: Session) -> Optional[Sandbox]:
        """为Agent创建沙箱环境"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return None
        
        # 生成唯一标识
        sandbox_id = str(uuid.uuid4())[:8]
        container_name = f"agent-sandbox-{agent_id}-{sandbox_id}"
        
        # 创建沙箱记录
        sandbox = Sandbox(
            agent_id=agent_id,
            container_name=container_name,
            status=SandboxStatus.PENDING
        )
        db.add(sandbox)
        db.commit()
        db.refresh(sandbox)
        
        # 初始化网络
        if not self.initialize_network():
            sandbox.status = SandboxStatus.ERROR
            sandbox.status_message = "Failed to initialize network"
            db.commit()
            return sandbox
        
        # 创建Docker容器
        returncode, stdout, stderr = self._run_command([
            "docker", "run", "-d",
            "--name", container_name,
            "--network", self.network_name,
            "--network-alias", f"agent-{agent_id}",
            "--cap-drop", "ALL",  # 丢弃所有特权
            "--cap-add", "NET_BIND_SERVICE",
            "--security-opt", "no-new-privileges:true",
            "--read-only",  # 只读文件系统
            "--tmpfs", "/tmp:noexec,nosuid,size=100m",
            "--memory", "512m",
            "--memory-swap", "512m",
            "--cpus", "1.0",
            "--pids-limit", "100",
            "--restart", "unless-stopped",
            "-e", f"AGENT_ID={agent_id}",
            "-e", f"SANDBOX_ID={sandbox_id}",
            "python:3.11-slim",
            "sleep", "infinity"
        ], check=False)
        
        if returncode != 0:
            sandbox.status = SandboxStatus.ERROR
            sandbox.status_message = f"Failed to create container: {stderr}"
            db.commit()
            logger.error(f"Failed to create sandbox for agent {agent_id}: {stderr}")
            return sandbox
        
        container_id = stdout.strip()
        
        # 获取容器IP地址
        returncode, ip_output, _ = self._run_command([
            "docker", "inspect",
            "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
            container_id
        ], check=False)
        
        ip_address = ip_output.strip() if returncode == 0 else None
        
        # 配置网络规则（默认拒绝所有出站连接）
        network_rules = [
            {"type": "deny", "dst": "0.0.0.0/0", "port": "any", "protocol": "any"}
        ]
        
        # 更新沙箱信息
        sandbox.container_id = container_id
        sandbox.ip_address = ip_address
        sandbox.network_rules = network_rules
        sandbox.status = SandboxStatus.RUNNING
        sandbox.status_message = "Sandbox created successfully"
        db.commit()
        
        # 更新Agent信息
        agent.sandbox_id = sandbox_id
        agent.sandbox_status = SandboxStatus.RUNNING
        db.commit()
        
        logger.info(f"Created sandbox for agent {agent_id}: {container_name} ({ip_address})")
        return sandbox
    
    def add_network_rule(self, sandbox_id: int, rule: Dict, db: Session) -> bool:
        """添加网络规则"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox or not sandbox.container_id:
            return False
        
        # 使用iptables添加规则
        action = "ACCEPT" if rule.get("type") == "allow" else "DROP"
        dst = rule.get("dst", "0.0.0.0/0")
        port = rule.get("port", "any")
        protocol = rule.get("protocol", "tcp")
        
        if port == "any":
            port_arg = ""
        else:
            port_arg = f"--dport {port}"
        
        # 在容器内执行iptables命令
        cmd = [
            "docker", "exec", sandbox.container_id,
            "iptables", "-A", "OUTPUT",
            "-p", protocol,
            "-d", dst
        ]
        if port_arg:
            cmd.extend(port_arg.split())
        cmd.extend(["-j", action])
        
        returncode, _, stderr = self._run_command(cmd, check=False)
        
        if returncode == 0:
            # 更新数据库中的规则
            rules = sandbox.network_rules or []
            rules.append(rule)
            sandbox.network_rules = rules
            db.commit()
            logger.info(f"Added network rule to sandbox {sandbox_id}: {rule}")
            return True
        else:
            logger.error(f"Failed to add network rule: {stderr}")
            return False
    
    def remove_network_rule(self, sandbox_id: int, rule_index: int, db: Session) -> bool:
        """移除网络规则"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox or not sandbox.network_rules:
            return False
        
        rules = sandbox.network_rules
        if rule_index < 0 or rule_index >= len(rules):
            return False
        
        # 移除规则（简化处理：清除所有规则并重新应用）
        if sandbox.container_id:
            self._run_command([
                "docker", "exec", sandbox.container_id,
                "iptables", "-F", "OUTPUT"
            ], check=False)
        
        # 从列表中移除
        rules.pop(rule_index)
        sandbox.network_rules = rules
        db.commit()
        
        # 重新应用剩余规则
        for rule in rules:
            self.add_network_rule(sandbox_id, rule, db)
        
        return True
    
    def stop_sandbox(self, sandbox_id: int, db: Session) -> bool:
        """停止沙箱"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox or not sandbox.container_id:
            return False
        
        returncode, _, _ = self._run_command([
            "docker", "stop", sandbox.container_id
        ], check=False)
        
        if returncode == 0:
            sandbox.status = SandboxStatus.STOPPED
            db.commit()
            
            # 更新Agent状态
            agent = db.query(Agent).filter(Agent.id == sandbox.agent_id).first()
            if agent:
                agent.sandbox_status = SandboxStatus.STOPPED
                db.commit()
            
            logger.info(f"Stopped sandbox {sandbox_id}")
            return True
        return False
    
    def start_sandbox(self, sandbox_id: int, db: Session) -> bool:
        """启动沙箱"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox or not sandbox.container_id:
            return False
        
        returncode, _, _ = self._run_command([
            "docker", "start", sandbox.container_id
        ], check=False)
        
        if returncode == 0:
            sandbox.status = SandboxStatus.RUNNING
            db.commit()
            
            # 更新Agent状态
            agent = db.query(Agent).filter(Agent.id == sandbox.agent_id).first()
            if agent:
                agent.sandbox_status = SandboxStatus.RUNNING
                db.commit()
            
            logger.info(f"Started sandbox {sandbox_id}")
            return True
        return False
    
    def delete_sandbox(self, sandbox_id: int, db: Session) -> bool:
        """删除沙箱"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox:
            return False
        
        if sandbox.container_id:
            # 停止并删除容器
            self._run_command([
                "docker", "stop", sandbox.container_id
            ], check=False)
            
            self._run_command([
                "docker", "rm", "-f", sandbox.container_id
            ], check=False)
        
        # 更新Agent状态
        agent = db.query(Agent).filter(Agent.id == sandbox.agent_id).first()
        if agent:
            agent.sandbox_id = None
            agent.sandbox_status = SandboxStatus.PENDING
            db.commit()
        
        # 删除记录
        db.delete(sandbox)
        db.commit()
        
        logger.info(f"Deleted sandbox {sandbox_id}")
        return True
    
    def get_sandbox_status(self, sandbox_id: int, db: Session) -> Optional[Dict]:
        """获取沙箱状态"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox:
            return None
        
        status = {
            "id": sandbox.id,
            "agent_id": sandbox.agent_id,
            "container_id": sandbox.container_id,
            "container_name": sandbox.container_name,
            "ip_address": sandbox.ip_address,
            "status": sandbox.status.value,
            "network_rules": sandbox.network_rules,
            "created_at": sandbox.created_at.isoformat() if sandbox.created_at else None,
            "started_at": sandbox.started_at.isoformat() if sandbox.started_at else None
        }
        
        # 如果容器正在运行，获取实时状态
        if sandbox.container_id and sandbox.status == SandboxStatus.RUNNING:
            returncode, stdout, _ = self._run_command([
                "docker", "stats", "--no-stream", "--format",
                "{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.PIDs}}",
                sandbox.container_id
            ], check=False)
            
            if returncode == 0:
                stats = stdout.strip().split("|")
                if len(stats) >= 4:
                    status["stats"] = {
                        "cpu_percent": stats[0],
                        "memory_usage": stats[1],
                        "network_io": stats[2],
                        "pids": stats[3]
                    }
        
        return status
    
    def execute_in_sandbox(self, sandbox_id: int, command: List[str], db: Session) -> tuple:
        """在沙箱中执行命令"""
        sandbox = db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
        if not sandbox or not sandbox.container_id:
            return 1, "", "Sandbox not found"
        
        cmd = ["docker", "exec", sandbox.container_id] + command
        return self._run_command(cmd, check=False)
    
    def list_sandboxes(self, db: Session) -> List[Dict]:
        """列出所有沙箱"""
        sandboxes = db.query(Sandbox).all()
        return [{
            "id": s.id,
            "agent_id": s.agent_id,
            "container_name": s.container_name,
            "ip_address": s.ip_address,
            "status": s.status.value,
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in sandboxes]

# 全局沙箱管理器实例
sandbox_manager = SandboxManager()

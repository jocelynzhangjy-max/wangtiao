from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from ..database import get_db
from ..auth.auth import get_current_active_user
from ..models import User, Agent, NetworkRequest
from ..core.network_ai import network_ai_analyzer

router = APIRouter()

@router.get("/analysis/network", response_model=Dict)
async def analyze_network_traffic(
    time_window: int = 3600,  # 默认1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析网络流量"""
    try:
        # 获取用户的所有智能体
        agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
        agent_ids = [agent.id for agent in agents]
        
        # 获取时间窗口内的网络请求
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id.in_(agent_ids),
            NetworkRequest.request_time >= cutoff_time
        ).all()
        
        # 分析网络流量
        analysis = network_ai_analyzer.analyze_network_traffic(requests)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze network traffic: {str(e)}"
        )

@router.get("/analysis/agent/{agent_id}", response_model=Dict)
async def analyze_agent_behavior(
    agent_id: int,
    time_window: int = 3600,  # 默认1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析智能体行为"""
    # 验证智能体所有权
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    try:
        analysis = network_ai_analyzer.analyze_agent_behavior(agent_id, db, time_window)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze agent behavior: {str(e)}"
        )

@router.get("/anomalies", response_model=List[Dict])
async def detect_network_anomalies(
    time_window: int = 3600,  # 默认1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """检测网络异常"""
    try:
        # 获取用户的所有智能体
        agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
        agent_ids = [agent.id for agent in agents]
        
        # 获取时间窗口内的网络请求
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        requests = db.query(NetworkRequest).filter(
            NetworkRequest.agent_id.in_(agent_ids),
            NetworkRequest.request_time >= cutoff_time
        ).all()
        
        # 检测异常
        anomalies = network_ai_analyzer.detect_network_anomalies(db, time_window)
        
        # 过滤出用户的智能体异常
        user_anomalies = [a for a in anomalies if a.get('agent_id') in agent_ids]
        
        return user_anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect network anomalies: {str(e)}"
        )

@router.get("/trends", response_model=Dict)
async def predict_network_trends(
    time_window: int = 3600,  # 默认1小时历史数据
    prediction_horizon: int = 3600,  # 默认预测1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """预测网络趋势"""
    try:
        # 获取用户的所有智能体
        agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
        agent_ids = [agent.id for agent in agents]
        
        # 预测网络趋势
        trends = network_ai_analyzer.predict_network_trends(db, time_window, prediction_horizon)
        return trends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict network trends: {str(e)}"
        )

@router.get("/agent/{agent_id}/profile", response_model=Dict)
async def get_agent_profile(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取智能体配置文件"""
    # 验证智能体所有权
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    profile = network_ai_analyzer.get_agent_profile(agent_id)
    if not profile:
        # 如果没有配置文件，生成一个
        profile = network_ai_analyzer.analyze_agent_behavior(agent_id, db)
    
    return profile

@router.get("/statistics", response_model=Dict)
async def get_network_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """获取网络统计信息"""
    try:
        stats = network_ai_analyzer.get_network_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get network statistics: {str(e)}"
        )

"""网络数据分析和可视化API路由"""
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.network_analytics import network_analytics_manager
from ..dependencies import get_db, get_current_active_user
from ..models import User, Agent

router = APIRouter()

@router.get("/traffic-analysis", response_model=Dict)
def analyze_network_traffic(
    time_window: int = 3600,  # 默认1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析网络流量"""
    try:
        # 收集网络数据
        requests = network_analytics_manager.collect_network_data(current_user.id, time_window, db)
        
        # 分析网络流量
        analysis = network_analytics_manager.analyze_network_traffic(requests)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze network traffic: {str(e)}"
        )

@router.get("/agents/{agent_id}/behavior", response_model=Dict)
def analyze_agent_behavior(
    agent_id: int,
    time_window: int = 3600,  # 默认1小时
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析智能体行为"""
    try:
        # 验证智能体是否属于当前用户
        agent = db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not accessible"
            )
        
        # 分析智能体行为
        analysis = network_analytics_manager.analyze_agent_behavior(agent_id, time_window, db)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze agent behavior: {str(e)}"
        )

@router.get("/report", response_model=Dict)
def generate_network_report(
    time_window: int = 86400,  # 默认1天
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """生成网络分析报告"""
    try:
        # 生成网络报告
        report = network_analytics_manager.generate_network_report(current_user.id, time_window, db)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate network report: {str(e)}"
        )

@router.get("/dashboard", response_model=Dict)
def get_analytics_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分析仪表盘数据"""
    try:
        # 获取不同时间窗口的数据
        hour_data = network_analytics_manager.analyze_network_traffic(
            network_analytics_manager.collect_network_data(current_user.id, 3600, db)
        )
        
        day_data = network_analytics_manager.analyze_network_traffic(
            network_analytics_manager.collect_network_data(current_user.id, 86400, db)
        )
        
        week_data = network_analytics_manager.analyze_network_traffic(
            network_analytics_manager.collect_network_data(current_user.id, 604800, db)
        )
        
        # 获取用户的所有智能体
        agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
        
        # 分析每个智能体的行为
        agent_analyses = []
        for agent in agents:
            analysis = network_analytics_manager.analyze_agent_behavior(agent.id, 86400, db)
            agent_analyses.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "risk_score": analysis["summary"]["risk_score"],
                "risk_level": analysis["summary"]["risk_level"],
                "total_requests": analysis["traffic_analysis"]["total_requests"]
            })
        
        # 按风险分数排序
        agent_analyses.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "time_windows": {
                "hour": hour_data,
                "day": day_data,
                "week": week_data
            },
            "agent_analyses": agent_analyses,
            "summary": {
                "total_agents": len(agents),
                "total_requests": day_data["total_requests"],
                "high_risk_agents": len([a for a in agent_analyses if a["risk_level"] == "high"]),
                "average_risk_score": sum(a["risk_score"] for a in agent_analyses) / len(agent_analyses) if agent_analyses else 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics dashboard: {str(e)}"
        )

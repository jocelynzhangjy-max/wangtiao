"""智能体信誉系统API路由"""
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.reputation import reputation_manager
from ..dependencies import get_db, get_current_active_user
from ..models import User, Agent
from ..schemas import ReputationScore, BehaviorReport, ReputationSummary

router = APIRouter()

@router.get("/agents/{agent_id}/reputation", response_model=Dict)
def get_agent_reputation(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取智能体的信誉评分"""
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
        
        # 计算信誉评分
        reputation_score = reputation_manager.calculate_reputation_score(agent_id, db)
        return reputation_score
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent reputation: {str(e)}"
        )

@router.get("/agents/{agent_id}/behavior-report", response_model=Dict)
def get_agent_behavior_report(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取智能体的行为分析报告"""
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
        
        # 生成行为报告
        behavior_report = reputation_manager.generate_behavior_report(agent_id, db)
        return behavior_report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate behavior report: {str(e)}"
        )

@router.get("/summary", response_model=Dict)
def get_reputation_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户所有智能体的信誉摘要"""
    try:
        # 获取信誉摘要
        summary = reputation_manager.get_reputation_summary(current_user.id, db)
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reputation summary: {str(e)}"
        )

@router.post("/agents/{agent_id}/reputation/refresh", response_model=Dict)
def refresh_agent_reputation(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """刷新智能体的信誉评分"""
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
        
        # 重新计算信誉评分
        reputation_score = reputation_manager.calculate_reputation_score(agent_id, db)
        return {
            "message": "Reputation score refreshed successfully",
            "reputation": reputation_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh reputation score: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from ..database import get_db
from ..auth.auth import get_current_active_user
from ..models import User, AgentTeam, TeamMember, Agent
from ..core.collaboration import collaboration_manager

router = APIRouter()

@router.post("/teams", response_model=Dict)
async def create_team(
    name: str,
    description: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建智能体团队"""
    try:
        team = collaboration_manager.create_team(
            user_id=current_user.id,
            name=name,
            description=description,
            db=db
        )
        return {
            "team_id": team.team_id,
            "name": team.name,
            "description": team.description,
            "created_at": team.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create team: {str(e)}"
        )

@router.get("/teams", response_model=List[Dict])
async def get_teams(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有团队"""
    teams = db.query(AgentTeam).filter(
        AgentTeam.user_id == current_user.id,
        AgentTeam.is_active == True
    ).all()
    
    return [{
        "team_id": team.team_id,
        "name": team.name,
        "description": team.description,
        "security_level": team.security_level,
        "created_at": team.created_at.isoformat()
    } for team in teams]

@router.get("/teams/{team_id}", response_model=Dict)
async def get_team(
    team_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取团队详情"""
    team = db.query(AgentTeam).filter(
        AgentTeam.team_id == team_id,
        AgentTeam.user_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # 获取团队成员
    members = collaboration_manager.get_team_members(team_id, db)
    
    return {
        "team_id": team.team_id,
        "name": team.name,
        "description": team.description,
        "security_level": team.security_level,
        "collaboration_policy": team.collaboration_policy,
        "members": members,
        "created_at": team.created_at.isoformat()
    }

@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除团队"""
    team = db.query(AgentTeam).filter(
        AgentTeam.team_id == team_id,
        AgentTeam.user_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # 移除所有团队成员
    members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).all()
    
    for member in members:
        agent = db.query(Agent).filter(Agent.id == member.agent_id).first()
        if agent:
            agent.team_id = None
            agent.collaboration_mode = "independent"
            agent.role = None
        db.delete(member)
    
    # 删除团队
    team.is_active = False
    db.commit()
    
    return {"message": "Team deleted successfully"}

@router.post("/teams/{team_id}/members", response_model=Dict)
async def add_agent_to_team(
    team_id: str,
    agent_id: int,
    role: str,
    permissions: Dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加智能体到团队"""
    # 验证团队所有权
    team = db.query(AgentTeam).filter(
        AgentTeam.team_id == team_id,
        AgentTeam.user_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
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
        team_member = collaboration_manager.add_agent_to_team(
            team_id=team_id,
            agent_id=agent_id,
            role=role,
            permissions=permissions,
            db=db
        )
        return {
            "team_id": team_member.team_id,
            "agent_id": team_member.agent_id,
            "role": team_member.role,
            "permissions": team_member.permissions,
            "joined_at": team_member.joined_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add agent to team: {str(e)}"
        )

@router.delete("/teams/{team_id}/members/{agent_id}")
async def remove_agent_from_team(
    team_id: str,
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """从团队中移除智能体"""
    # 验证团队所有权
    team = db.query(AgentTeam).filter(
        AgentTeam.team_id == team_id,
        AgentTeam.user_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
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
    
    success = collaboration_manager.remove_agent_from_team(
        team_id=team_id,
        agent_id=agent_id,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent is not a member of the team"
        )
    
    return {"message": "Agent removed from team successfully"}

@router.post("/collaborate", response_model=Dict)
async def process_collaboration_request(
    sender_agent_id: int,
    receiver_agent_id: int,
    request_type: str,
    payload: Dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """处理智能体之间的协作请求"""
    # 验证智能体所有权
    sender = db.query(Agent).filter(
        Agent.id == sender_agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    receiver = db.query(Agent).filter(
        Agent.id == receiver_agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not sender or not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both agents not found"
        )
    
    try:
        allowed, response_data, message = await collaboration_manager.process_collaboration_request(
            sender_agent_id=sender_agent_id,
            receiver_agent_id=receiver_agent_id,
            request_type=request_type,
            payload=payload,
            db=db
        )
        
        return {
            "allowed": allowed,
            "message": message,
            "data": response_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process collaboration request: {str(e)}"
        )

@router.get("/agents/{agent_id}/teams", response_model=List[Dict])
async def get_agent_teams(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取智能体所属的团队"""
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
    
    teams = collaboration_manager.get_agent_teams(agent_id, db)
    return teams

@router.get("/statistics", response_model=Dict)
async def get_collaboration_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """获取协作统计信息"""
    stats = collaboration_manager.get_statistics()
    return stats

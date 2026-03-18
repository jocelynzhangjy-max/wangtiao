from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth.auth import get_current_active_user
from ..models import Agent, User
from ..schemas import Agent as AgentSchema, AgentCreate, AgentUpdate

router = APIRouter()

@router.post("/", response_model=AgentSchema)
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_agent = Agent(
        user_id=current_user.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        model_id=agent.model_id,
        config_json=agent.config_json
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/", response_model=List[AgentSchema])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agents = db.query(Agent).filter(Agent.user_id == current_user.id).offset(skip).limit(limit).all()
    return agents

@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent

@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # 更新Agent信息
    if agent_update.name is not None:
        agent.name = agent_update.name
    if agent_update.description is not None:
        agent.description = agent_update.description
    if agent_update.agent_type is not None:
        agent.agent_type = agent_update.agent_type
    if agent_update.model_id is not None:
        agent.model_id = agent_update.model_id
    if agent_update.config_json is not None:
        agent.config_json = agent_update.config_json
    
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.auth.auth import get_current_active_user
from backend.models import User, Tool, AgentTool
from backend.schemas import Tool as ToolSchema, ToolCreate, ToolUpdate, AgentTool as AgentToolSchema, AgentToolCreate

router = APIRouter()

@router.post("/", response_model=ToolSchema)
async def create_tool(
    tool: ToolCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 检查工具名称是否已存在
    existing_tool = db.query(Tool).filter(Tool.name == tool.name).first()
    if existing_tool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool name already exists"
        )
    
    db_tool = Tool(
        name=tool.name,
        description=tool.description,
        type=tool.type,
        config_json=tool.config_json
    )
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

@router.get("/", response_model=List[ToolSchema])
async def get_tools(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tools = db.query(Tool).offset(skip).limit(limit).all()
    return tools

@router.get("/{tool_id}", response_model=ToolSchema)
async def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool

@router.put("/{tool_id}", response_model=ToolSchema)
async def update_tool(
    tool_id: int,
    tool_update: ToolUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # 更新工具信息
    if tool_update.name is not None:
        # 检查工具名称是否已存在
        existing_tool = db.query(Tool).filter(
            Tool.name == tool_update.name,
            Tool.id != tool_id
        ).first()
        if existing_tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool name already exists"
            )
        tool.name = tool_update.name
    if tool_update.description is not None:
        tool.description = tool_update.description
    if tool_update.type is not None:
        tool.type = tool_update.type
    if tool_update.config_json is not None:
        tool.config_json = tool_update.config_json
    
    db.commit()
    db.refresh(tool)
    return tool

@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    db.delete(tool)
    db.commit()
    return {"message": "Tool deleted successfully"}

# AgentTool 相关路由
@router.post("/agent-tools", response_model=AgentToolSchema)
async def add_tool_to_agent(
    agent_tool: AgentToolCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 检查Agent是否存在且属于当前用户
    agent = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_tool.agent_id
    ).join(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # 检查工具是否存在
    tool = db.query(Tool).filter(Tool.id == agent_tool.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # 检查是否已经添加
    existing_agent_tool = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_tool.agent_id,
        AgentTool.tool_id == agent_tool.tool_id
    ).first()
    if existing_agent_tool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool already added to agent"
        )
    
    db_agent_tool = AgentTool(
        agent_id=agent_tool.agent_id,
        tool_id=agent_tool.tool_id,
        config_json=agent_tool.config_json
    )
    db.add(db_agent_tool)
    db.commit()
    db.refresh(db_agent_tool)
    return db_agent_tool

@router.delete("/agent-tools/{agent_id}/{tool_id}")
async def remove_tool_from_agent(
    agent_id: int,
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 检查Agent是否存在且属于当前用户
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent_tool = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    if not agent_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found in agent"
        )
    
    db.delete(agent_tool)
    db.commit()
    return {"message": "Tool removed from agent successfully"}

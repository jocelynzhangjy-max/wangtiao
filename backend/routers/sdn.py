"""软件定义网络(SDN) API路由"""
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.sdn import sdn_manager
from ..dependencies import get_db, get_current_active_user
from ..models import User, SDNTopology, SDNFlow, SDNLink

router = APIRouter()

@router.post("/topologies", response_model=Dict)
def create_topology(
    name: str,
    description: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建网络拓扑"""
    try:
        topology = sdn_manager.create_topology(
            user_id=current_user.id,
            name=name,
            description=description,
            db=db
        )
        return {
            "topology_id": topology.topology_id,
            "name": topology.name,
            "description": topology.description,
            "status": topology.status,
            "created_at": topology.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create topology: {str(e)}"
        )

@router.get("/topologies", response_model=List[Dict])
def get_topologies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有拓扑"""
    try:
        topologies = db.query(SDNTopology).filter(SDNTopology.user_id == current_user.id).all()
        return [{
            "topology_id": t.topology_id,
            "name": t.name,
            "description": t.description,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        } for t in topologies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get topologies: {str(e)}"
        )

@router.get("/topologies/{topology_id}", response_model=Dict)
def get_topology(
    topology_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取拓扑详情"""
    try:
        # 验证拓扑是否属于当前用户
        topology = db.query(SDNTopology).filter(
            SDNTopology.topology_id == topology_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not topology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topology not found or not accessible"
            )
        
        topology_info = sdn_manager.get_topology(topology_id, db)
        return topology_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get topology: {str(e)}"
        )

@router.post("/topologies/{topology_id}/switches", response_model=Dict)
def add_switch(
    topology_id: str,
    switch_id: str,
    name: str,
    ip: str,
    port: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加交换机到拓扑"""
    try:
        # 验证拓扑是否属于当前用户
        topology = db.query(SDNTopology).filter(
            SDNTopology.topology_id == topology_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not topology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topology not found or not accessible"
            )
        
        switch = sdn_manager.add_switch(topology_id, switch_id, name, ip, port, db)
        return switch
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add switch: {str(e)}"
        )

@router.post("/topologies/{topology_id}/links", response_model=Dict)
def add_link(
    topology_id: str,
    source_switch: str,
    destination_switch: str,
    bandwidth: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加链路到拓扑"""
    try:
        # 验证拓扑是否属于当前用户
        topology = db.query(SDNTopology).filter(
            SDNTopology.topology_id == topology_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not topology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topology not found or not accessible"
            )
        
        link = sdn_manager.add_link(topology_id, source_switch, destination_switch, bandwidth, db)
        return {
            "id": link.id,
            "source_switch": link.source_switch,
            "destination_switch": link.destination_switch,
            "bandwidth": link.bandwidth,
            "status": link.status,
            "latency": link.latency,
            "utilization": link.utilization
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add link: {str(e)}"
        )

@router.post("/topologies/{topology_id}/flows", response_model=Dict)
def create_flow(
    topology_id: str,
    switch_id: str,
    priority: int,
    match: Dict[str, Any],
    actions: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建流表项"""
    try:
        # 验证拓扑是否属于当前用户
        topology = db.query(SDNTopology).filter(
            SDNTopology.topology_id == topology_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not topology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topology not found or not accessible"
            )
        
        flow = sdn_manager.create_flow(topology_id, switch_id, priority, match, actions, db)
        return {
            "id": flow.id,
            "switch_id": flow.switch_id,
            "priority": flow.priority,
            "match": flow.match,
            "actions": flow.actions,
            "status": flow.status,
            "timeout": flow.timeout,
            "created_at": flow.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create flow: {str(e)}"
        )

@router.put("/flows/{flow_id}", response_model=Dict)
def update_flow(
    flow_id: int,
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新流表项状态"""
    try:
        # 验证流表项是否属于当前用户
        flow = db.query(SDNFlow).join(SDNTopology).filter(
            SDNFlow.id == flow_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found or not accessible"
            )
        
        updated_flow = sdn_manager.update_flow(flow_id, status, db)
        return {
            "id": updated_flow.id,
            "status": updated_flow.status,
            "updated_at": updated_flow.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update flow: {str(e)}"
        )

@router.delete("/flows/{flow_id}", response_model=Dict)
def delete_flow(
    flow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除流表项"""
    try:
        # 验证流表项是否属于当前用户
        flow = db.query(SDNFlow).join(SDNTopology).filter(
            SDNFlow.id == flow_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found or not accessible"
            )
        
        sdn_manager.delete_flow(flow_id, db)
        return {"message": "Flow deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete flow: {str(e)}"
        )

@router.get("/topologies/{topology_id}/traffic-analysis", response_model=Dict)
def analyze_network_traffic(
    topology_id: str,
    time_window: int = 3600,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析网络流量"""
    try:
        # 验证拓扑是否属于当前用户
        topology = db.query(SDNTopology).filter(
            SDNTopology.topology_id == topology_id,
            SDNTopology.user_id == current_user.id
        ).first()
        
        if not topology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topology not found or not accessible"
            )
        
        analysis = sdn_manager.analyze_network_traffic(topology_id, time_window, db)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze network traffic: {str(e)}"
        )

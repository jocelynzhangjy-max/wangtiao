from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, agents, shadow_network, collaboration, network_ai, reputation, sdn, network_analytics
from .auth import router as auth_router
from .core.policy_engine import policy_engine
from .core.identity_manager import init_identity_manager
import os
from dotenv import load_dotenv

load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Gateway API",
    description="A comprehensive API for managing AI agents with shadow network security",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化身份管理器
init_identity_manager(os.getenv("SECRET_KEY", "your-secret-key"))

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(shadow_network.router, prefix="/api/shadow", tags=["shadow-network"])
app.include_router(collaboration.router, prefix="/api/collaboration", tags=["collaboration"])
app.include_router(network_ai.router, prefix="/api/network-ai", tags=["network-ai"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["reputation"])
app.include_router(sdn.router, prefix="/api/sdn", tags=["sdn"])
app.include_router(network_analytics.router, prefix="/api/analytics", tags=["network-analytics"])

# 根路径
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Agent Gateway API",
        "version": "2.0.0",
        "features": [
            "agent-management",
            "sandbox-network",
            "policy-control",
            "intent-audit",
            "identity-management",
            "alert-system"
        ]
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "shadow_network": "enabled"}

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    from .database import SessionLocal
    
    # 加载策略缓存
    db = SessionLocal()
    try:
        policy_engine.reload_policies(db)
        print("✅ Policy engine initialized")
    finally:
        db.close()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import users, agents, tools, conversations
from backend.auth import router as auth_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Gateway API",
    description="A comprehensive API for managing AI agents and their tools",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to AI Agent Gateway API"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

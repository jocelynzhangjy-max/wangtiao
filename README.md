# AI Agent Gateway

AI Agent Gateway 是一个完整的系统，用于管理和部署 AI 代理（Agents），提供统一的 API 接口和用户友好的前端界面。

## 🚀 功能特点

### 核心功能
- **用户认证系统**：支持用户注册、登录、JWT 令牌验证
- **AI 代理管理**：创建、编辑、删除 AI 代理
- **工具集成**：为代理添加和管理各种工具
- **对话管理**：记录和管理与 AI 代理的对话
- **API 接口**：提供完整的 RESTful API

### 技术特点
- **现代化前端**：React + Tailwind CSS + Framer Motion
- **高性能后端**：FastAPI + SQLAlchemy
- **安全认证**：JWT 令牌 + 密码哈希
- **响应式设计**：支持桌面和移动设备
- **深色科技主题**：炫酷的深色界面，科技感十足

## 📦 安装说明

### 前置要求
- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 后端安装

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd agentgateway-master
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements-backend.txt
   ```

4. **配置环境变量**
   创建 `.env` 文件：
   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///./agentgateway.db
   ```

5. **启动后端服务**
   ```bash
   uvicorn backend.app:app --port 8001
   ```

### 前端安装

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动前端服务**
   ```bash
   npm run dev
   ```

## 🌐 访问地址

- **前端**：http://localhost:3000
- **后端 API**：http://localhost:8001
- **API 文档**：http://localhost:8001/docs

## 📁 项目结构

```
agentgateway-master/
├── backend/              # 后端代码
│   ├── auth/             # 认证相关
│   ├── database.py       # 数据库配置
│   ├── models/           # 数据库模型
│   ├── routers/          # API 路由
│   ├── schemas/          # 数据验证
│   └── app.py            # 应用入口
├── frontend/             # 前端代码
│   ├── src/              # 源代码
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── stores/       # 状态管理
│   │   └── App.jsx       # 应用入口
│   └── vite.config.js    # Vite 配置
├── .env                  # 环境变量
└── requirements-backend.txt  # 后端依赖
```

## 🎨 界面特点

### 深色科技主题
- **主背景**：深紫蓝渐变 (#120458 → #0a032e)
- **模块背景**：#1A1A2E（深蓝紫）
- **科技蓝**：#00BCD4（亮青色）
- **幻影紫**：#8854D9（中等紫色）
- **霓虹粉**：#FF6D99（亮粉色）

### 动态效果
- **缓慢流动渐变**：背景色循环过渡
- **粒子点缀**：半透明白色粒子，鼠标悬停时向鼠标位置聚拢
- **登录框动态**：入场动画、渐变呼吸、输入框反馈
- **文字动态**：标题逐字淡入，辅助文字滑入

## 🔧 API 接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 用户相关
- `GET /api/users/me` - 获取当前用户信息

### 代理相关
- `GET /api/agents` - 获取所有代理
- `POST /api/agents` - 创建代理
- `PUT /api/agents/{id}` - 更新代理
- `DELETE /api/agents/{id}` - 删除代理

### 工具相关
- `GET /api/tools` - 获取所有工具
- `POST /api/tools` - 创建工具

### 对话相关
- `GET /api/conversations` - 获取所有对话
- `POST /api/conversations` - 创建对话

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请联系项目维护者。

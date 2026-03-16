# 后端基础镜像
FROM python:3.9-slim AS backend

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-backend.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

# 前端基础镜像
FROM node:18-alpine AS frontend

# 设置工作目录
WORKDIR /app

# 复制前端代码
COPY frontend/package.json frontend/package-lock.json ./

# 安装依赖
RUN npm install

# 复制前端源代码
COPY frontend/ .

# 构建前端
RUN npm run build

# 生产环境镜像
FROM python:3.9-slim AS production

# 设置工作目录
WORKDIR /app

# 复制后端依赖和代码
COPY --from=backend /app/ .

# 复制前端构建文件
COPY --from=frontend /app/dist/ ./frontend/dist

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

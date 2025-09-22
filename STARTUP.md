# 快速启动指南

## 🎯 项目概述

本项目是一个基于FastAPI的接口自动化测试平台，支持用户权限管理、接口测试、测试用例管理等功能。

## ✅ 已完成功能

### 第一阶段：核心基础框架 ✅
- ✅ 项目目录结构和依赖配置
- ✅ 基于pydantic-settings的配置管理
- ✅ Tortoise ORM数据库连接配置
- ✅ Redis连接管理和缓存策略
- ✅ 基础中间件、异常处理和日志系统

### 第二阶段：用户认证系统 ✅
- ✅ 用户、角色、权限数据模型
- ✅ Redis Token认证机制
- ✅ 登录/登出API和用户管理API
- ✅ RBAC权限验证中间件

### 基础设施 ✅
- ✅ 数据库初始化SQL脚本
- ✅ Docker和Docker Compose配置
- ✅ 单元测试框架
- ✅ 项目文档

## 🚀 快速启动

### 方式一：Docker启动（推荐）

```bash
cd backend
docker-compose up -d
```

### 方式二：本地开发启动

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境**
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库连接
```

3. **启动MySQL和Redis**
```bash
# 使用Docker启动数据库服务
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=test_platform_dev mysql:8.0
docker run -d --name redis -p 6379:6379 redis:alpine
```

4. **初始化数据库**
```bash
mysql -h localhost -u root -ppassword < init_db.sql
```

5. **启动应用**
```bash
python start.py
```

## 🔍 验证功能

### 1. 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 健康检查
```bash
curl http://localhost:8000/health
```

### 3. 测试登录API
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 4. 获取用户列表（需要Token）
```bash
# 先登录获取Token，然后：
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🧪 运行测试

```bash
cd backend
pytest
```

## 📋 默认账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| tester | test123 | 测试工程师 |

## 🎯 下一步开发

### 待实现功能：

1. **接口测试核心**
   - 接口定义管理API
   - 测试用例CRUD功能
   - HTTP客户端封装和测试执行

2. **高级测试功能**
   - 变量管理系统
   - Celery异步任务
   - 批量测试执行
   - 测试报告生成

3. **前端界面**
   - Vue3 + TypeScript
   - Ant Design Vue
   - 测试用例编辑器
   - 测试报告可视化

## 🔧 技术架构

```
Frontend (Vue3)
      ↓
   FastAPI
      ↓
  ┌─────────┬─────────┐
  │  MySQL  │  Redis  │
  └─────────┴─────────┘
      ↓
   Celery Workers
```

## 📝 项目特色

1. **现代化技术栈** - FastAPI + Tortoise ORM + Redis
2. **完整权限系统** - RBAC角色权限管理
3. **异步架构** - 支持高并发请求处理
4. **容器化部署** - Docker一键部署
5. **完善测试** - 单元测试覆盖
6. **详细文档** - API自动文档生成

项目已成功创建核心架构和用户认证系统，可以开始进行下一阶段的接口测试功能开发！
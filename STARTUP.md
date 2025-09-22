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

**新版本特性**：现在使用 UV + Aerich 管理依赖和数据库，Docker 会自动：
- 使用 UV 安装依赖（极速）
- 初始化 Aerich 配置
- 创建数据库迁移
- 应用迁移到数据库
- 插入初始数据

### 方式二：本地开发启动

1. **安装 UV**
```bash
# 使用 pip 安装
pip install uv

# 或使用官方脚本（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **初始化项目**
```bash
cd backend

# 方式1：一键启动（推荐）
python start_modern.py

# 方式2：手动操作
uv venv                # 创建虚拟环境
uv pip install -e .    # 安装依赖
python migrate.py      # 初始化数据库
uv run python start.py # 启动应用
```

3. **配置数据库（如需要）**
```bash
# 使用Docker启动数据库服务
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=test_platform_dev mysql:8.0
docker run -d --name redis -p 6379:6379 redis:alpine
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
7. **数据库迁移** - 使用 Aerich 管理数据库版本
8. **现代化依赖管理** - 使用 UV 获得 10-100x 安装速度提升

## ⚡ UV 依赖管理 (新功能)

项目现在使用 **UV** 作为现代化的 Python 依赖管理工具，替代传统的 pip + requirements.txt 方式。

### UV 优势
- ⚡ **10-100x** 比 pip 更快的安装速度
- 🔒 确定性的依赖锁定（uv.lock）
- 🛠️ 内置虚拟环境管理
- 📝 原生支持 pyproject.toml
- 🌍 跨平台一致性

### 常用 UV 命令
```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e .[dev]

# 运行脚本
uv run python script.py
uv run pytest
uv run aerich migrate
```

### UV 相关命令
```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e .[dev]

# 运行脚本
uv run python script.py
uv run pytest
uv run aerich migrate
```

## 🔄 数据库迁移 (新功能)

项目现在使用 **Aerich** 作为数据库迁移工具，替代原来的 SQL 初始化方式。

### 迁移优势
- ✅ 版本化管理数据库变更
- ✅ 支持迁移回滚
- ✅ 团队协作友好
- ✅ 自动生成迁移文件
- ✅ 确保各环境数据库一致

### 常用迁移命令
```bash
# 生成迁移文件
aerich migrate --name "添加新字段"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade

# 查看迁移历史
aerich history
```

### 迁移工具
```bash
# 使用交互式迁移管理工具
python migrate.py
```

项目已成功创建核心架构和用户认证系统，现在使用：
- 🚀 **UV** 现代化依赖管理（极速安装）
- 🔄 **Aerich** 数据库迁移管理（版本化）
- 📝 **pyproject.toml** 现代化项目配置

**快速体验：**
```bash
cd backend
python start_modern.py  # 一键启动！
```

可以开始进行下一阶段的接口测试功能开发！
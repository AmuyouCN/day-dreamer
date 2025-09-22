## 前后端分离架构说明

### API接口规范

#### 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 错误响应格式
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null,
  "errors": [
    {
      "field": "username",
      "message": "用户名不能为空"
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 分页响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 前端需求API清单

#### 认证模块API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 登录 | POST | `/api/v1/auth/login` | 用户登录获取token |
| 登出 | POST | `/api/v1/auth/logout` | 用户登出清除token |
| 刷新token | POST | `/api/v1/auth/refresh` | 刷新访问token |
| 获取用户信息 | GET | `/api/v1/auth/me` | 获取当前用户信息 |

#### 用户管理API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 用户列表 | GET | `/api/v1/users` | 获取用户列表(支持分页、搜索) |
| 创建用户 | POST | `/api/v1/users` | 创建新用户 |
| 用户详情 | GET | `/api/v1/users/{id}` | 获取用户详细信息 |
| 更新用户 | PUT | `/api/v1/users/{id}` | 更新用户信息 |
| 删除用户 | DELETE | `/api/v1/users/{id}` | 删除用户 |
| 用户角色 | GET | `/api/v1/users/{id}/roles` | 获取用户角色列表 |
| 分配角色 | POST | `/api/v1/users/{id}/roles` | 为用户分配角色 |

#### 接口管理API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 接口列表 | GET | `/api/v1/apis` | 获取接口列表 |
| 创建接口 | POST | `/api/v1/apis` | 创建接口定义 |
| 接口详情 | GET | `/api/v1/apis/{id}` | 获取接口详情 |
| 更新接口 | PUT | `/api/v1/apis/{id}` | 更新接口定义 |
| 删除接口 | DELETE | `/api/v1/apis/{id}` | 删除接口 |
| 测试接口 | POST | `/api/v1/apis/{id}/test` | 执行接口测试 |
| 导入接口 | POST | `/api/v1/apis/import` | 批量导入接口 |

#### 测试用例API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 测试用例列表 | GET | `/api/v1/test-cases` | 获取测试用例列表 |
| 创建测试用例 | POST | `/api/v1/test-cases` | 创建测试用例 |
| 测试用例详情 | GET | `/api/v1/test-cases/{id}` | 获取测试用例详情 |
| 更新测试用例 | PUT | `/api/v1/test-cases/{id}` | 更新测试用例 |
| 删除测试用例 | DELETE | `/api/v1/test-cases/{id}` | 删除测试用例 |
| 运行测试用例 | POST | `/api/v1/test-cases/{id}/run` | 执行单个测试用例 |
| 复制测试用例 | POST | `/api/v1/test-cases/{id}/copy` | 复制测试用例 |

#### 变量管理API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 变量列表 | GET | `/api/v1/variables` | 获取变量列表(按作用域) |
| 创建变量 | POST | `/api/v1/variables` | 创建变量 |
| 变量详情 | GET | `/api/v1/variables/{id}` | 获取变量详情 |
| 更新变量 | PUT | `/api/v1/variables/{id}` | 更新变量 |
| 删除变量 | DELETE | `/api/v1/variables/{id}` | 删除变量 |
| 全局变量 | GET | `/api/v1/variables/global` | 获取全局变量 |
| 个人变量 | GET | `/api/v1/variables/personal` | 获取个人变量 |
| 环境变量 | GET | `/api/v1/variables/environment/{env_id}` | 获取环境变量 |

#### 测试执行API
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 执行历史 | GET | `/api/v1/executions` | 获取执行历史 |
| 执行详情 | GET | `/api/v1/executions/{id}` | 获取执行详情 |
| 执行结果 | GET | `/api/v1/executions/{id}/results` | 获取执行结果 |
| 执行报告 | GET | `/api/v1/executions/{id}/report` | 获取执行报告 |
| 停止执行 | POST | `/api/v1/executions/{id}/stop` | 停止执行 |
| 批量执行 | POST | `/api/v1/executions/batch` | 批量执行测试 |

### CORS配置说明
后端需要配置CORS允许前端跨域访问：
```python
# 开发环境
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]

# 生产环境
ALLOWED_HOSTS=["https://your-frontend-domain.com"]
```

### 前端Vue3项目建议

#### 推荐技术栈
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI组件库**: Ant Design Vue 或 Element Plus
- **HTTP客户端**: Axios
- **代码编辑器**: Monaco Editor (用于接口编辑)
- **图表库**: ECharts (用于测试报告)

#### 项目结构建议
```
frontend/
├── src/
│   ├── api/              # API请求封装
│   ├── components/        # 通用组件
│   ├── views/            # 页面组件
│   │   ├── auth/         # 认证页面
│   │   ├── user/         # 用户管理
│   │   ├── api/          # 接口管理
│   │   ├── test/         # 测试管理
│   │   └── variable/     # 变量管理
│   ├── stores/           # Pinia状态管理
│   ├── router/           # 路由配置
│   ├── utils/            # 工具函数
│   └── types/            # TypeScript类型定义
├── public/
└── package.json
```

#### 核心功能页面
1. **登录页面** - 用户认证
2. **仪表盘** - 数据概览和快捷操作
3. **用户管理** - 用户CRUD和角色分配
4. **接口管理** - 接口定义和测试
5. **测试用例管理** - 测试用例编辑和执行
6. **测试场景管理** - 复杂场景编排
7. **变量管理** - 四种作用域变量管理
8. **执行历史** - 测试结果查看和报告
9. **系统设置** - 环境配置等

## AI代码生成关键指引

### 🎯 实现优先级（必须严格按顺序）
1. **阶段一：核心基础框架**
   - 项目初始化和目录结构创建
   - 配置管理系统（pydantic-settings）
   - 数据库连接和模型定义
   - Redis连接管理
   - 基础中间件和异常处理

2. **阶段二：用户认证系统**
   - 用户模型和基础CRUD
   - Redis Token认证机制
   - 登录/登出API
   - 权限中间件

3. **阶段三：权限管理系统**
   - 角色和权限模型
   - RBAC权限验证
   - 用户角色分配API

4. **阶段四：接口测试核心**
   - 接口定义管理
   - 基础测试用例CRUD
   - HTTP客户端封装
   - 单个测试执行

5. **阶段五：高级测试功能**
   - 变量管理系统
   - Celery异步任务
   - 批量测试执行
   - 测试报告生成

### 🔧 关键技术要求

#### 必须使用的确切版本
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
tortoise-orm[asyncmy]==0.20.0
aiomysql==0.2.0
passlib[bcrypt]==1.7.4
aioredis==2.0.1
celery==5.3.4
httpx==0.25.2
loguru==0.7.2
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

#### 项目结构要求（严格按此结构）
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # pydantic-settings配置
│   │   ├── database.py     # Tortoise ORM配置
│   │   ├── redis.py        # Redis连接管理
│   │   ├── security.py     # 密码和Token工具
│   │   └── celery.py       # Celery配置
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py         # 依赖注入
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── roles.py
│   │       ├── permissions.py
│   │       ├── api_management.py
│   │       ├── test_cases.py
│   │       ├── variables.py
│   │       └── test_execution.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── api_definition.py
│   │   ├── test_case.py
│   │   ├── variable.py
│   │   ├── test_execution.py
│   │   └── test_result.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── api.py
│   │   ├── test_case.py
│   │   ├── variable.py
│   │   └── execution.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── api_service.py
│   │   ├── test_service.py
│   │   └── variable_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── api_repository.py
│   │   └── test_repository.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── test_tasks.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── exceptions.py
│       ├── http_client.py
│       └── variable_resolver.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_apis.py
├── alembic/                # 数据库迁移
├── logs/
├── .env.example
├── .env.dev
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

#### 必须实现的核心特性

1. **统一响应格式封装**
```python
# app/utils/response.py
from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: str = datetime.utcnow().isoformat()

class PagedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

def success_response(data: Any = None, message: str = "success") -> dict:
    return ApiResponse(data=data, message=message).dict()

def error_response(code: int, message: str, errors: Optional[List] = None) -> dict:
    response = ApiResponse(code=code, message=message, data=None).dict()
    if errors:
        response["errors"] = errors
    return response
```

2. **全局异常处理器**
```python
# app/utils/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
import traceback

class BusinessException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    logger.error(traceback.format_exc())
    
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=exc.code,
            content=error_response(exc.code, exc.message)
        )
    elif isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.status_code, exc.detail)
        )
    else:
        return JSONResponse(
            status_code=500,
            content=error_response(500, "Internal server error")
        )
```

3. **数据库事务装饰器**
```python
# app/utils/decorators.py
from functools import wraps
from tortoise.transactions import in_transaction
from loguru import logger

def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with in_transaction() as conn:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Transaction failed: {e}")
                raise
    return wrapper
```

4. **请求日志中间件**
```python
# app/middleware/logging.py
import time
import uuid
from fastapi import Request
from loguru import logger

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"[{request_id}] {request.method} {request.url} "
        f"- {response.status_code} - {process_time:.3f}s"
    )
    
    response.headers["X-Request-ID"] = request_id
    return response
```

#### 数据库初始化脚本要求
必须包含以下初始化数据：

```sql
-- 默认管理员用户
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES 
('admin', 'admin@example.com', '$2b$12$...' -- bcrypt加密后的'admin123', '系统管理员', true);

-- 默认测试用户
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES 
('tester', 'tester@example.com', '$2b$12$...' -- bcrypt加密后的'test123', '测试用户', true);

-- 管理员角色分配
INSERT INTO user_roles (user_id, role_id) VALUES 
(1, 1), -- admin -> 管理员
(2, 4); -- tester -> 测试工程师

-- 角色权限分配
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 1, id FROM permissions; -- 管理员拥有所有权限

INSERT INTO role_permissions (role_id, permission_id) VALUES 
(4, 4), (4, 5), (4, 6), (4, 7), (4, 8); -- 测试工程师基本权限
```

#### 环境配置文件模板
必须创建 .env.example 文件：
```env
# 应用配置
APP_NAME=接口自动化测试平台
DEBUG=true
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=mysql://root:password@localhost:3306/test_platform

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 日志配置
LOG_LEVEL=DEBUG
```
1. **第一阶段：核心基础** - 用户管理、认证授权、基础权限控制
2. **第二阶段：测试基础** - 接口管理、单个测试用例执行
3. **第三阶段：高级功能** - 测试场景、变量管理、批量执行
4. **第四阶段：平台完善** - 报告生成、统计分析、高级权限

### 📝 必须实现的文件清单

#### 启动脚本
创建以下启动脚本：

**start.py** (主启动脚本)
```python
#!/usr/bin/env python3
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
```

**start_celery.py** (Celery启动脚本)
```python
#!/usr/bin/env python3
import os
from celery import Celery
from app.core.config import settings

os.environ.setdefault('CELERY_CONFIG_MODULE', 'app.core.celery')

celery_app = Celery('test_platform')
celery_app.config_from_object(settings.celery_config)
celery_app.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    celery_app.start()
```

#### Docker配置

**Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

EXPOSE 8000

CMD ["python", "start.py"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://root:password@mysql:3306/test_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs

  celery:
    build: .
    command: python start_celery.py
    environment:
      - DATABASE_URL=mysql://root:password@mysql:3306/test_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: test_platform
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

#### README.md 模板
```markdown
# 接口自动化测试平台

## 快速开始

### 本地开发
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 复制配置文件：`cp .env.example .env`
4. 初始化数据库：执行SQL脚本
5. 启动应用：`python start.py`
6. 启动Celery: `python start_celery.py`

### Docker部署
```bash
docker-compose up -d
```

## API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账户
- 管理员: admin/admin123
- 测试用户: tester/test123
```

### 🚫 AI必须避免的错误

1. **不要使用过时的写法**
   - ✗ `from_orm()` → ✓ `from_attributes=True`
   - ✗ `Config` → ✓ `model_config`
   - ✗ `BaseSettings()` → ✓ `BaseSettings` + `SettingsConfigDict`

2. **不要混用数据库连接**
   - 只使用 Tortoise ORM，不要混用 SQLAlchemy
   - 使用 `await Model.create()` 而不是 `Model.objects.create()`

3. **不要忽略异常处理**
   - 所有数据库操作必须有 try-except
   - 所有API端点必须有错误处理

4. **不要忘记异步关键字**
   - 所有数据库操作必须使用 `await`
   - 所有HTTP请求必须使用 `async/await`

### 🎁 成功标准

AI生成的项目必须满足：

✓ **可以正常启动** - `python start.py` 无错误
✓ **数据库连接成功** - 可以连接MySQL和Redis
✓ **API文档可访问** - http://localhost:8000/docs 正常显示
✓ **登录功能正常** - 可以使用admin/admin123登录
✓ **权限验证正常** - 未登录访问受保护资源返回401
✓ **CRUD操作正常** - 用户、角色、权限等基本操作正常
✓ **日志输出正常** - 有清晰的请求日志
✓ **单元测试通过** - `pytest` 执行成功

### 🚀 最后检查清单

在提交给AI之前，请确认：

1. ☑️ 所有模型都有完整的字段定义
2. ☑️ 所有API都有明确的请求和响应Schema
3. ☑️ 所有配置都有默认值和环境变量支持
4. ☑️ 数据库初始化SQL有默认数据
5. ☑️ Docker配置完整可用
6. ☑️ 项目结构清晰明确
7. ☑️ 所有依赖包版本明确指定

🎆 **现在可以安心交给AI生成代码了！**
```
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库相关
tortoise-orm[asyncmy]==0.20.0
aiosqlite==0.19.0  # 开发环境
aiomysql==0.2.0    # 生产环境

# 认证和安全
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0

# Redis和缓存
redis==5.0.1
aioredis==2.0.1

# 异步任务
celery==5.3.4

# HTTP客户端
httpx==0.25.2

# 日志
loguru==0.7.2

# 数据验证
pydantic==2.5.0

# 配置管理
pydantic-settings==2.1.0
python-decouple==3.8

# 测试
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

## 概述

本项目是一个基于FastAPI的中小型用户权限管理系统，集成了接口自动化测试平台，采用现代化的Python技术栈，实现用户管理、基于角色的访问控制(RBAC)以及完整的API测试解决方案。系统设计遵循行业最佳实践，注重代码简洁性、可维护性和调试友好性。

### 核心价值
- 提供安全可靠的用户身份认证和授权机制
- 支持灵活的角色权限管理模型
- 集成完整的接口自动化测试平台
- 支持多环境、多场景的API测试管理
- 易于开发者理解、扩展和调试
- 高性能的API服务架构

### 核心配置管理 (app/core/config.py)
```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基本配置
    app_name: str = Field(default="接口自动化测试平台", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    allowed_hosts: List[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    
    # 数据库配置
    database_url: str = Field(..., alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    
    # Redis配置
    redis_url: str = Field(..., alias="REDIS_URL")
    redis_max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    
    # 安全配置
    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_hours: int = Field(default=2, alias="ACCESS_TOKEN_EXPIRE_HOURS")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Celery配置
    celery_broker_url: str = Field(..., alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., alias="CELERY_RESULT_BACKEND")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")
    log_rotation: str = Field(default="100 MB", alias="LOG_ROTATION")
    log_retention: str = Field(default="30 days", alias="LOG_RETENTION")
    
    # 测试配置
    max_concurrent_tests: int = Field(default=10, alias="MAX_CONCURRENT_TESTS")
    test_timeout: int = Field(default=300, alias="TEST_TIMEOUT")  # 秒
    
    # 文件上传配置
    upload_max_size: int = Field(default=10 * 1024 * 1024, alias="UPLOAD_MAX_SIZE")  # 10MB
    upload_allowed_types: List[str] = Field(
        default=[".json", ".yaml", ".yml", ".csv", ".xlsx"],
        alias="UPLOAD_ALLOWED_TYPES"
    )
    
    # 邮件配置(可选)
    smtp_server: Optional[str] = Field(default=None, alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    
    # 监控配置
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    
    @property
    def database_config(self) -> dict:
        """Tortoise ORM数据库配置"""
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self._parse_db_url()["host"],
                        "port": self._parse_db_url()["port"],
                        "user": self._parse_db_url()["username"],
                        "password": self._parse_db_url()["password"],
                        "database": self._parse_db_url()["database"],
                        "charset": "utf8mb4",
                        "echo": self.database_echo
                    }
                }
            },
            "apps": {
                "models": {
                    "models": ["app.models"],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "Asia/Shanghai"
        }
    
    def _parse_db_url(self) -> dict:
        """解析数据库URL"""
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(self.database_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "username": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/") if parsed.path else None
        }
    
    @property
    def redis_config(self) -> dict:
        """Redis连接配置"""
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(self.redis_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "max_connections": self.redis_max_connections,
            "decode_responses": True
        }
    
    @property
    def celery_config(self) -> dict:
        """Celery配置"""
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "Asia/Shanghai",
            "enable_utc": True,
            "worker_prefetch_multiplier": 1,
            "task_acks_late": True,
            "task_reject_on_worker_lost": True
        }

# 创建全局配置实例
settings = Settings()
```

### 环境配置文件示例

**开发环境配置 (.env.dev)**
```env
# 应用配置
APP_NAME=接口自动化测试平台
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000
ALLOWED_HOSTS=["localhost","127.0.0.1","0.0.0.0"]

# 数据库配置
DATABASE_URL=mysql://root:password@localhost:3306/test_platform_dev
DATABASE_ECHO=true

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# 安全配置
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_HOURS=24
REFRESH_TOKEN_EXPIRE_DAYS=30

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
LOG_ROTATION=50 MB
LOG_RETENTION=7 days

# 测试配置
MAX_CONCURRENT_TESTS=5
TEST_TIMEOUT=120

# 文件上传配置
UPLOAD_MAX_SIZE=52428800  # 50MB
UPLOAD_ALLOWED_TYPES=[".json",".yaml",".yml",".csv",".xlsx",".har"]

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
```

**生产环境配置 (.env.prod)**
```env
# 应用配置
APP_NAME=接口自动化测试平台
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
ALLOWED_HOSTS=["your-domain.com","api.your-domain.com"]

# 数据库配置
DATABASE_URL=mysql://username:strong_password@mysql-server:3306/test_platform
DATABASE_ECHO=false

# Redis配置
REDIS_URL=redis://redis-server:6379/0
REDIS_MAX_CONNECTIONS=50

# 安全配置
SECRET_KEY=your-very-strong-secret-key-here
ACCESS_TOKEN_EXPIRE_HOURS=2
REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery配置
CELERY_BROKER_URL=redis://redis-server:6379/1
CELERY_RESULT_BACKEND=redis://redis-server:6379/2

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_ROTATION=100 MB
LOG_RETENTION=30 days

# 测试配置
MAX_CONCURRENT_TESTS=20
TEST_TIMEOUT=300

# 文件上传配置
UPLOAD_MAX_SIZE=10485760  # 10MB
UPLOAD_ALLOWED_TYPES=[".json",".yaml",".yml",".csv",".xlsx"]

# 邮件配置(可选)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
```
### 数据库初始化配置 (app/core/database.py)
```python
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
from app.core.config import settings
from loguru import logger

async def init_database():
    """初始化数据库连接"""
    try:
        await Tortoise.init(config=settings.database_config)
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        raise

async def close_database():
    """关闭数据库连接"""
    try:
        await Tortoise.close_connections()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")

def setup_database(app: FastAPI):
    """设置数据库中间件"""
    register_tortoise(
        app,
        config=settings.database_config,
        generate_schemas=settings.debug,  # 仅在开发环境自动生成表
        add_exception_handlers=True,
    )
```

### Redis连接配置 (app/core/redis.py)
```python
import aioredis
from typing import Optional
from app.core.config import settings
from loguru import logger

class RedisManager:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._pool: Optional[aioredis.ConnectionPool] = None
    
    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self._pool = aioredis.ConnectionPool.from_url(
                settings.redis_url,
                **settings.redis_config
            )
            self._redis = aioredis.Redis(connection_pool=self._pool)
            
            # 测试连接
            await self._redis.ping()
            logger.info("“Redis连接初始化成功")
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise
    
    async def close_redis(self):
        """关闭Redis连接"""
        try:
            if self._redis:
                await self._redis.close()
            if self._pool:
                await self._pool.disconnect()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接失败: {e}")
    
    def get_redis(self) -> aioredis.Redis:
        """获取Redis实例"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        return self._redis

# 全局Redis管理器
redis_manager = RedisManager()

async def init_redis():
    """初始化Redis"""
    await redis_manager.init_redis()

async def close_redis():
    """关闭Redis"""
    await redis_manager.close_redis()

def get_redis() -> aioredis.Redis:
    """获取Redis实例"""
    return redis_manager.get_redis()
```

### Celery配置 (app/core/celery.py)
```python
from celery import Celery
from app.core.config import settings

# 创建Celery实例
celery_app = Celery(
    "test_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# 配置Celery
celery_app.conf.update(settings.celery_config)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])

@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```
- **Web框架**: FastAPI - 高性能异步Web框架
- **日志记录**: Loguru - 简化的Python日志库
- **数据库ORM**: Tortoise ORM - 异步ORM框架
- **缓存**: Redis - 用于Token存储和会话管理
- **数据库**: MySQL - 主要关系型数据库
- **数据验证**: Pydantic - 数据验证和序列化
- **密码加密**: Passlib + bcrypt - 密码安全处理
- **Token管理**: Redis - 纯Redis Token存储和管理
- **API文档**: FastAPI自动生成 - Swagger UI/ReDoc
- **HTTP客户端**: HTTPX - 异步HTTP请求客户端
- **任务调度**: Celery + Redis - 异步任务处理
- **数据序列化**: JSON/YAML - 测试数据存储格式

## 整体架构

### 分层架构设计

```mermaid
graph TB
    subgraph "API层"
        A1[用户API路由]
        A2[认证API路由]
        A3[权限API路由]
        A4[角色API路由]
        A5[接口测试API路由]
        A6[环境变量API路由]
        A7[测试执行API路由]
    end
    
    subgraph "业务逻辑层"
        B1[用户服务]
        B2[认证服务]
        B3[权限服务]
        B4[角色服务]
        B5[接口管理服务]
        B6[变量管理服务]
        B7[测试执行服务]
        B8[测试结果服务]
    end
    
    subgraph "数据访问层"
        C1[用户仓储]
        C2[角色仓储]
        C3[权限仓储]
        C4[接口仓储]
        C5[测试用例仓储]
        C6[变量仓储]
        C7[测试结果仓储]
    end
    
    subgraph "基础设施层"
        D1[(MySQL数据库)]
        D2[(Redis缓存&Token)]
        D3[日志系统]
        D4[配置管理]
        D5[Celery任务队列]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A5 --> B5
    A6 --> B6
    A7 --> B7
    
    B1 --> C1
    B2 --> C1
    B3 --> C3
    B4 --> C2
    B5 --> C4
    B6 --> C6
    B7 --> C5
    B8 --> C7
    
    C1 --> D1
    C2 --> D1
    C3 --> D1
    C4 --> D1
    C5 --> D1
    C6 --> D1
    C7 --> D1
    
    B2 --> D2
    B6 --> D2
    B7 --> D5
    B1 --> D3
    B2 --> D3
    B7 --> D3
```

### 目录结构设计

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── core/                   # 核心配置和工具
│   │   ├── config.py          # 配置管理
│   │   ├── security.py        # 安全相关工具
│   │   ├── database.py        # MySQL数据库连接配置
│   │   ├── redis.py           # Redis连接和Token管理配置
│   │   └── celery.py          # Celery异步任务配置
│   ├── api/                    # API路由层
│   │   ├── __init__.py
│   │   ├── deps.py            # 依赖注入
│   │   └── v1/                # API版本1
│   │       ├── __init__.py
│   │       ├── auth.py        # 认证相关API
│   │       ├── users.py       # 用户管理API
│   │       ├── roles.py       # 角色管理API
│   │       ├── permissions.py # 权限管理API
│   │       ├── api_management.py # 接口管理API
│   │       ├── test_cases.py  # 测试用例API
│   │       ├── test_scenarios.py # 测试场景API
│   │       ├── variables.py   # 变量管理API
│   │       ├── test_execution.py # 测试执行API
│   │       └── reports.py     # 测试报告API
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py    # 用户业务逻辑
│   │   ├── auth_service.py    # 认证业务逻辑
│   │   ├── role_service.py    # 角色业务逻辑
│   │   ├── permission_service.py # 权限业务逻辑
│   │   ├── api_service.py     # 接口管理业务逻辑
│   │   ├── variable_service.py # 变量管理业务逻辑
│   │   ├── test_execution_service.py # 测试执行业务逻辑
│   │   └── report_service.py  # 报告业务逻辑
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py            # 用户模型
│   │   ├── role.py            # 角色模型
│   │   ├── permission.py      # 权限模型
│   │   ├── api_definition.py  # 接口定义模型
│   │   ├── test_case.py       # 测试用例模型
│   │   ├── test_scenario.py   # 测试场景模型
│   │   ├── variable.py        # 变量模型
│   │   ├── test_execution.py  # 测试执行模型
│   │   └── test_result.py     # 测试结果模型
│   ├── schemas/                # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py            # 用户数据模式
│   │   ├── auth.py            # 认证数据模式
│   │   ├── role.py            # 角色数据模式
│   │   ├── permission.py      # 权限数据模式
│   │   ├── api.py             # API数据模式
│   │   ├── test_case.py       # 测试用例数据模式
│   │   ├── variable.py        # 变量数据模式
│   │   └── execution.py       # 执行数据模式
│   ├── repositories/           # 数据访问层
│   │   ├── __init__.py
│   │   ├── user_repository.py # 用户数据访问
│   │   ├── role_repository.py # 角色数据访问
│   │   ├── permission_repository.py # 权限数据访问
│   │   ├── api_repository.py  # 接口数据访问
│   │   ├── test_case_repository.py # 测试用例数据访问
│   │   ├── variable_repository.py # 变量数据访问
│   │   └── result_repository.py # 结果数据访问
│   ├── tasks/                  # Celery异步任务
│   │   ├── __init__.py
│   │   ├── test_execution_tasks.py # 测试执行任务
│   │   └── report_tasks.py    # 报告生成任务
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── logger.py          # 日志配置
│       ├── exceptions.py      # 自定义异常
│       ├── http_client.py     # HTTP请求客户端
│       ├── variable_resolver.py # 变量解析器
│       └── test_runner.py     # 测试执行器
├── tests/                      # 测试文件
├── requirements.txt            # 依赖包列表
└── README.md                  # 项目说明
```

## 数据库表结构设计

### 数据库初始化SQL脚本

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE test_platform;

-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- 角色表
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);

-- 权限表
CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_resource_action (resource, action)
);

-- 用户角色关联表
CREATE TABLE user_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_role (user_id, role_id)
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_permission (role_id, permission_id)
);

-- 接口定义表
CREATE TABLE api_definitions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL,
    url VARCHAR(500) NOT NULL,
    headers JSON,
    query_params JSON,
    body_schema JSON,
    response_schema JSON,
    creator_id INT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    INDEX idx_creator (creator_id),
    INDEX idx_method_url (method, url(100))
);

-- 测试用例表
CREATE TABLE test_cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    api_id INT NOT NULL,
    request_data JSON,
    expected_response JSON,
    assertions JSON,
    creator_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (api_id) REFERENCES api_definitions(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    INDEX idx_api (api_id),
    INDEX idx_creator (creator_id)
);

-- 环境表
CREATE TABLE environments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    config JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 变量表
CREATE TABLE variables (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    value TEXT,
    type VARCHAR(20) NOT NULL DEFAULT 'string',
    scope VARCHAR(20) NOT NULL,
    user_id INT NULL,
    environment_id INT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
    INDEX idx_scope (scope),
    INDEX idx_user_id (user_id),
    INDEX idx_environment_id (environment_id),
    UNIQUE KEY unique_global_var (name, scope) -- 全局变量名称唯一
);

-- 测试执行表
CREATE TABLE test_executions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    execution_type VARCHAR(20) NOT NULL,
    target_id INT NOT NULL,
    executor_id INT NOT NULL,
    environment_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    execution_config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (executor_id) REFERENCES users(id),
    FOREIGN KEY (environment_id) REFERENCES environments(id),
    INDEX idx_executor (executor_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 测试结果表
CREATE TABLE test_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    execution_id INT NOT NULL,
    test_case_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    request_data JSON,
    response_data JSON,
    assertion_results JSON,
    duration FLOAT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id),
    INDEX idx_execution (execution_id),
    INDEX idx_status (status)
);

-- 初始化数据
INSERT INTO environments (name, description, config) VALUES 
('development', '开发环境', '{"base_url": "http://localhost:8000"}'),
('testing', '测试环境', '{"base_url": "http://test.example.com"}'),
('production', '生产环境', '{"base_url": "https://api.example.com"}');

INSERT INTO roles (name, description) VALUES 
('管理员', '系统管理员，拥有所有权限'),
('测试负责人', '测试项目负责人'),
('高级测试工程师', '高级测试工程师'),
('测试工程师', '一般测试工程师'),
('实习生', '实习生，只读权限');

INSERT INTO permissions (name, resource, action, description) VALUES 
('user:read', 'user', 'read', '查看用户信息'),
('user:write', 'user', 'write', '编辑用户信息'),
('user:delete', 'user', 'delete', '删除用户'),
('api:read', 'api', 'read', '查看接口定义'),
('api:write', 'api', 'write', '编辑接口定义'),
('test:execute', 'test', 'execute', '执行测试'),
('test:manage', 'test', 'manage', '管理测试用例'),
('report:read', 'report', 'read', '查看测试报告'),
('variable:global', 'variable', 'global', '管理全局变量'),
('system:admin', 'system', 'admin', '系统管理权限');
```

## Tortoise ORM模型定义示例

### 用户模型 (app/models/user.py)
```python
from tortoise.models import Model
from tortoise import fields
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=100, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login = fields.DatetimeField(null=True)
    
    # 关联字段
    roles = fields.ManyToManyField('models.Role', related_name='users', through='user_roles')
    created_apis = fields.ReverseRelation['ApiDefinition']
    created_test_cases = fields.ReverseRelation['TestCase']
    personal_variables = fields.ReverseRelation['Variable']
    
    class Meta:
        table = "users"
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
    
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)
```

### 接口定义模型 (app/models/api_definition.py)
```python
from tortoise.models import Model
from tortoise import fields

class ApiDefinition(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    method = fields.CharField(max_length=10)  # GET, POST, PUT, DELETE
    url = fields.CharField(max_length=500)
    headers = fields.JSONField(default=dict)
    query_params = fields.JSONField(default=dict)
    body_schema = fields.JSONField(default=dict)
    response_schema = fields.JSONField(default=dict)
    is_public = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 关联字段
    creator = fields.ForeignKeyField('models.User', related_name='created_apis')
    test_cases = fields.ReverseRelation['TestCase']
    
    class Meta:
        table = "api_definitions"
```

### 测试用例模型 (app/models/test_case.py)
```python
from tortoise.models import Model
from tortoise import fields

class TestCase(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    request_data = fields.JSONField(default=dict)
    expected_response = fields.JSONField(default=dict)
    assertions = fields.JSONField(default=list)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 关联字段
    api = fields.ForeignKeyField('models.ApiDefinition', related_name='test_cases')
    creator = fields.ForeignKeyField('models.User', related_name='created_test_cases')
    test_results = fields.ReverseRelation['TestResult']
    
    class Meta:
        table = "test_cases"
```

### 变量模型 (app/models/variable.py)
```python
from tortoise.models import Model
from tortoise import fields
from enum import Enum

class VariableScope(str, Enum):
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    PERSONAL = "personal"
    TEMPORARY = "temporary"

class VariableType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"

class Variable(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    value = fields.TextField(null=True)
    type = fields.CharEnumField(VariableType, default=VariableType.STRING)
    scope = fields.CharEnumField(VariableScope)
    description = fields.CharField(max_length=200, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 关联字段
    user = fields.ForeignKeyField('models.User', related_name='personal_variables', null=True)
    environment = fields.ForeignKeyField('models.Environment', related_name='variables', null=True)
    
    class Meta:
        table = "variables"
```

## Pydantic Schema示例

### 用户相关Schema (app/schemas/user.py)
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
```

### API相关Schema (app/schemas/api.py)
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ApiDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    method: HttpMethod
    url: str = Field(..., min_length=1, max_length=500)
    headers: Optional[Dict[str, Any]] = {}
    query_params: Optional[Dict[str, Any]] = {}
    body_schema: Optional[Dict[str, Any]] = {}
    response_schema: Optional[Dict[str, Any]] = {}
    is_public: bool = False

class ApiDefinitionResponse(ApiDefinitionCreate):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TestApiRequest(BaseModel):
    request_data: Dict[str, Any] = {}
    environment_id: Optional[int] = None
    variables: Optional[Dict[str, str]] = {}
```

### 测试相关Schema (app/schemas/test_case.py)
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AssertionType(str, Enum):
    STATUS_CODE = "status_code"
    RESPONSE_TIME = "response_time"
    JSON_PATH = "json_path"
    REGEX = "regex"
    CONTAINS = "contains"

class AssertionRule(BaseModel):
    type: AssertionType
    field: Optional[str] = None
    operator: str  # eq, ne, gt, lt, contains, regex
    expected: Any
    description: Optional[str] = None

class TestCaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    api_id: int
    request_data: Optional[Dict[str, Any]] = {}
    expected_response: Optional[Dict[str, Any]] = {}
    assertions: List[AssertionRule] = []
    is_active: bool = True

class TestCaseResponse(TestCaseCreate):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RunTestCaseRequest(BaseModel):
    environment_id: int
    variables: Optional[Dict[str, str]] = {}
    save_result: bool = True
```

### 核心实体关系

```mermaid
erDiagram
    User ||--o{ UserRole : "拥有"
    Role ||--o{ UserRole : "分配给"
    Role ||--o{ RolePermission : "包含"
    Permission ||--o{ RolePermission : "授予"
    
    User ||--o{ ApiDefinition : "创建"
    User ||--o{ TestCase : "创建"
    User ||--o{ TestScenario : "创建"
    User ||--o{ Variable : "拥有"
    User ||--o{ TestExecution : "执行"
    
    ApiDefinition ||--o{ TestCase : "包含"
    TestCase ||--o{ TestScenarioStep : "作为步骤"
    TestScenario ||--o{ TestScenarioStep : "包含"
    TestExecution ||--o{ TestResult : "产生"
    TestCase ||--o{ TestResult : "测试结果"
    
    Environment ||--o{ Variable : "环境变量"
    TestExecution ||--o{ ExecutionVariable : "使用变量"
    
    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime last_login
    }
    
    Role {
        int id PK
        string name UK
        string description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Permission {
        int id PK
        string name UK
        string resource
        string action
        string description
        datetime created_at
    }
    
    ApiDefinition {
        int id PK
        string name
        string description
        string method
        string url
        json headers
        json query_params
        json body_schema
        json response_schema
        int creator_id FK
        boolean is_public
        datetime created_at
        datetime updated_at
    }
    
    TestCase {
        int id PK
        string name
        string description
        int api_id FK
        json request_data
        json expected_response
        json assertions
        int creator_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    TestScenario {
        int id PK
        string name
        string description
        int creator_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    TestScenarioStep {
        int id PK
        int scenario_id FK
        int test_case_id FK
        int step_order
        json step_config
        datetime created_at
    }
    
    Variable {
        int id PK
        string name
        string value
        string type
        string scope
        int user_id FK
        int environment_id FK
        string description
        datetime created_at
        datetime updated_at
    }
    
    Environment {
        int id PK
        string name
        string description
        json config
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    TestExecution {
        int id PK
        string execution_type
        int target_id
        int executor_id FK
        int environment_id FK
        string status
        datetime started_at
        datetime finished_at
        json execution_config
        datetime created_at
    }
    
    TestResult {
        int id PK
        int execution_id FK
        int test_case_id FK
        string status
        json request_data
        json response_data
        json assertion_results
        float duration
        string error_message
        datetime created_at
    }
    
    ExecutionVariable {
        int id PK
        int execution_id FK
        string name
        string value
        string type
        datetime created_at
    }
    
    UserRole {
        int id PK
        int user_id FK
        int role_id FK
        datetime assigned_at
    }
    
    RolePermission {
        int id PK
        int role_id FK
        int permission_id FK
        datetime assigned_at
    }
```

## FastAPI路由示例

### 更新后的主应用入口 (app/main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.redis import init_redis, close_redis
from app.api.v1 import auth, users, api_management, test_cases, variables
from app.utils.logger import setup_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("应用启动中...")
    
    # 初始化日志
    setup_logger()
    
    # 初始化数据库
    await init_database()
    
    # 初始化Redis
    await init_redis()
    
    logger.info(f"应用启动完成 - {settings.app_name} v{settings.app_version}")
    
    yield
    
    # 关闭时清理
    logger.info("应用关闭中...")
    await close_redis()
    await close_database()
    logger.info("应用已关闭")

app = FastAPI(
    title=settings.app_name,
    description="基于FastAPI的用户权限管理和接口测试平台",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(api_management.router, prefix="/api/v1/apis", tags=["接口管理"])
app.include_router(test_cases.router, prefix="/api/v1/test-cases", tags=["测试用例"])
app.include_router(variables.router, prefix="/api/v1/variables", tags=["变量管理"])

@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "debug": settings.debug
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }

@app.get("/info")
async def app_info():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "environment": "development" if settings.debug else "production"
    }
```
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import settings
from app.core.redis import init_redis
from app.api.v1 import auth, users, api_management, test_cases, variables
from app.utils.logger import setup_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await init_redis()
    setup_logger()
    yield
    # 关闭时清理
    pass

app = FastAPI(
    title="接口自动化测试平台",
    description="基于FastAPI的用户权限管理和接口测试平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册数据库
register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(api_management.router, prefix="/api/v1/apis", tags=["接口管理"])
app.include_router(test_cases.router, prefix="/api/v1/test-cases", tags=["测试用例"])
app.include_router(variables.router, prefix="/api/v1/variables", tags=["变量管理"])

@app.get("/")
async def root():
    return {"message": "接口自动化测试平台 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 认证路由 (app/api/v1/auth.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.schemas.auth import TokenResponse, LoginRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """用户登录"""
    auth_service = AuthService()
    token_data = await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """用户登出"""
    auth_service = AuthService()
    await auth_service.logout_user(current_user.id)
    return {"message": "登出成功"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """获取当前用户信息"""
    return current_user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """刷新Token"""
    auth_service = AuthService()
    return await auth_service.refresh_user_token(current_user.id)
```

### 接口管理路由 (app/api/v1/api_management.py)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional, List

from app.schemas.api import (
    ApiDefinitionCreate, 
    ApiDefinitionResponse, 
    ApiDefinitionUpdate,
    TestApiRequest,
    TestApiResponse
)
from app.services.api_service import ApiService
from app.api.deps import get_current_user, require_permission
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ApiDefinitionResponse])
async def list_apis(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    method: Optional[str] = None,
    is_public: Optional[bool] = None
):
    """获取接口列表"""
    api_service = ApiService()
    return await api_service.list_apis(
        user_id=current_user.id,
        page=page,
        size=size,
        search=search,
        method=method,
        is_public=is_public
    )

@router.post("/", response_model=ApiDefinitionResponse)
async def create_api(
    api_data: ApiDefinitionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[None, Depends(require_permission("api:write"))]
):
    """创建接口定义"""
    api_service = ApiService()
    return await api_service.create_api(api_data, current_user.id)

@router.get("/{api_id}", response_model=ApiDefinitionResponse)
async def get_api(
    api_id: int,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """获取接口详情"""
    api_service = ApiService()
    api = await api_service.get_api_by_id(api_id, current_user.id)
    if not api:
        raise HTTPException(status_code=404, detail="接口不存在")
    return api

@router.post("/{api_id}/test", response_model=TestApiResponse)
async def test_api(
    api_id: int,
    test_data: TestApiRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[None, Depends(require_permission("test:execute"))]
):
    """测试接口"""
    api_service = ApiService()
    return await api_service.test_api(api_id, test_data, current_user.id)
```

```mermaid
graph TD
    A[用户登录] --> B[验证凭证]
    B --> C{凭证正确?}
    C -->|是| D[生成随机Token]
    C -->|否| E[返回错误]
    
    D --> F[Token信息]
    F --> G[user_id]
    F --> H[login_time]
    F --> I[expire_time]
    F --> J[permissions]
    
    F --> K[存储到Redis]
    K --> L[token:access:{token_value}]
    K --> M[user:tokens:{user_id}]
    
    N[API请求] --> O[提取Token]
    O --> P[从 Redis获取Token信息]
    P --> Q{存在且未过期?}
    Q -->|是| R[获取用户信息]
    Q -->|否| S[返回401未授权]
```

### Token数据结构

| 字段 | 类型 | 说明 |
|------|------|------|
| token | String | 随机生成的32位字符串 |
| user_id | Integer | 用户ID |
| username | String | 用户名 |
| login_time | Timestamp | 登录时间 |
| expire_time | Timestamp | 过期时间 |
| permissions | List | 用户权限列表 |
| ip_address | String | 登录IP地址 |
| user_agent | String | 客户端信息 |

### 自动化测试模块数据模型扩展

| 模型 | 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|------|
| ApiDefinition | id | Integer | PK, 自增 | 接口定义唯一标识 |
|  | name | VARCHAR(100) | 非空 | 接口名称 |
|  | description | TEXT | 可空 | 接口描述 |
|  | method | VARCHAR(10) | 非空 | HTTP方法 |
|  | url | VARCHAR(500) | 非空 | 接口URL |
|  | headers | JSON | 可空 | 请求头 |
|  | query_params | JSON | 可空 | 查询参数 |
|  | body_schema | JSON | 可空 | 请求体模式 |
|  | response_schema | JSON | 可空 | 响应模式 |
|  | creator_id | Integer | FK | 创建者ID |
|  | is_public | BOOLEAN | 默认FALSE | 是否公开 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| TestCase | id | Integer | PK, 自增 | 测试用例唯一标识 |
|  | name | VARCHAR(100) | 非空 | 测试用例名称 |
|  | description | TEXT | 可空 | 测试用例描述 |
|  | api_id | Integer | FK | 关联接口ID |
|  | request_data | JSON | 可空 | 请求数据 |
|  | expected_response | JSON | 可空 | 期望响应 |
|  | assertions | JSON | 可空 | 断言规则 |
|  | creator_id | Integer | FK | 创建者ID |
|  | is_active | BOOLEAN | 默认TRUE | 是否激活 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| TestScenario | id | Integer | PK, 自增 | 测试场景唯一标识 |
|  | name | VARCHAR(100) | 非空 | 测试场景名称 |
|  | description | TEXT | 可空 | 测试场景描述 |
|  | creator_id | Integer | FK | 创建者ID |
|  | is_active | BOOLEAN | 默认TRUE | 是否激活 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| Variable | id | Integer | PK, 自增 | 变量唯一标识 |
|  | name | VARCHAR(100) | 非空 | 变量名称 |
|  | value | TEXT | 可空 | 变量值 |
|  | type | VARCHAR(20) | 非空 | 变量类型(string/number/boolean/json) |
|  | scope | VARCHAR(20) | 非空 | 作用域(global/environment/personal/temporary) |
|  | user_id | Integer | FK | 用户ID(个人变量) |
|  | environment_id | Integer | FK | 环境ID(环境变量) |
|  | description | VARCHAR(200) | 可空 | 变量描述 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| Environment | id | Integer | PK, 自增 | 环境唯一标识 |
|  | name | VARCHAR(50) | 唯一, 非空 | 环境名称 |
|  | description | VARCHAR(200) | 可空 | 环境描述 |
|  | config | JSON | 可空 | 环境配置 |
|  | is_active | BOOLEAN | 默认TRUE | 是否激活 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| TestExecution | id | Integer | PK, 自增 | 测试执行唯一标识 |
|  | execution_type | VARCHAR(20) | 非空 | 执行类型(single/scenario/batch) |
|  | target_id | Integer | 非空 | 目标ID(测试用例或场景ID) |
|  | executor_id | Integer | FK | 执行者ID |
|  | environment_id | Integer | FK | 环境ID |
|  | status | VARCHAR(20) | 非空 | 执行状态 |
|  | started_at | DATETIME | 可空 | 开始时间 |
|  | finished_at | DATETIME | 可空 | 结束时间 |
|  | execution_config | JSON | 可空 | 执行配置 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
| TestResult | id | Integer | PK, 自增 | 测试结果唯一标识 |
|  | execution_id | Integer | FK | 执行ID |
|  | test_case_id | Integer | FK | 测试用例ID |
|  | status | VARCHAR(20) | 非空 | 测试状态(pass/fail/error/skip) |
|  | request_data | JSON | 可空 | 实际请求数据 |
|  | response_data | JSON | 可空 | 实际响应数据 |
|  | assertion_results | JSON | 可空 | 断言结果 |
|  | duration | FLOAT | 可空 | 执行时间(毫秒) |
|  | error_message | TEXT | 可空 | 错误信息 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |

| 模型 | 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|------|
| User | id | Integer | PK, 自增 | 用户唯一标识 |
|  | username | VARCHAR(50) | 唯一, 非空 | 用户名 |
|  | email | VARCHAR(100) | 唯一, 非空 | 邮箱地址 |
|  | password_hash | VARCHAR(255) | 非空 | 密码哈希值 |
|  | full_name | VARCHAR(100) | 可空 | 用户全名 |
|  | is_active | BOOLEAN | 默认TRUE | 用户状态 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
|  | last_login | DATETIME | 可空 | 最后登录时间 |
| Role | id | Integer | PK, 自增 | 角色唯一标识 |
|  | name | VARCHAR(50) | 唯一, 非空 | 角色名称 |
|  | description | VARCHAR(200) | 可空 | 角色描述 |
|  | is_active | BOOLEAN | 默认TRUE | 角色状态 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |
|  | updated_at | DATETIME | 自动更新 | 更新时间 |
| Permission | id | Integer | PK, 自增 | 权限唯一标识 |
|  | name | VARCHAR(100) | 唯一, 非空 | 权限名称 |
|  | resource | VARCHAR(50) | 非空 | 资源类型 |
|  | action | VARCHAR(50) | 非空 | 操作类型 |
|  | description | VARCHAR(200) | 可空 | 权限描述 |
|  | created_at | DATETIME | 自动填充 | 创建时间 |

## API接口设计

### 认证相关API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/auth/login` | POST | 用户登录 | LoginRequest | TokenResponse |
| `/api/v1/auth/logout` | POST | 用户登出 | - | MessageResponse |
| `/api/v1/auth/refresh` | POST | 刷新Token | RefreshRequest | TokenResponse |
| `/api/v1/auth/me` | GET | 获取当前用户信息 | - | UserResponse |

### 用户管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/users` | GET | 获取用户列表 | Query参数 | UserListResponse |
| `/api/v1/users` | POST | 创建用户 | CreateUserRequest | UserResponse |
| `/api/v1/users/{id}` | GET | 获取用户详情 | - | UserResponse |
| `/api/v1/users/{id}` | PUT | 更新用户信息 | UpdateUserRequest | UserResponse |
| `/api/v1/users/{id}` | DELETE | 删除用户 | - | MessageResponse |
| `/api/v1/users/{id}/roles` | GET | 获取用户角色 | - | RoleListResponse |
| `/api/v1/users/{id}/roles` | POST | 分配角色 | AssignRoleRequest | MessageResponse |
| `/api/v1/users/{id}/roles/{role_id}` | DELETE | 移除角色 | - | MessageResponse |

### 角色管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/roles` | GET | 获取角色列表 | Query参数 | RoleListResponse |
| `/api/v1/roles` | POST | 创建角色 | CreateRoleRequest | RoleResponse |
| `/api/v1/roles/{id}` | GET | 获取角色详情 | - | RoleResponse |
| `/api/v1/roles/{id}` | PUT | 更新角色信息 | UpdateRoleRequest | RoleResponse |
| `/api/v1/roles/{id}` | DELETE | 删除角色 | - | MessageResponse |
| `/api/v1/roles/{id}/permissions` | GET | 获取角色权限 | - | PermissionListResponse |
| `/api/v1/roles/{id}/permissions` | POST | 分配权限 | AssignPermissionRequest | MessageResponse |

### 接口管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/apis` | GET | 获取接口列表 | Query参数 | ApiListResponse |
| `/api/v1/apis` | POST | 创建接口 | CreateApiRequest | ApiResponse |
| `/api/v1/apis/{id}` | GET | 获取接口详情 | - | ApiResponse |
| `/api/v1/apis/{id}` | PUT | 更新接口 | UpdateApiRequest | ApiResponse |
| `/api/v1/apis/{id}` | DELETE | 删除接口 | - | MessageResponse |
| `/api/v1/apis/{id}/test` | POST | 测试接口 | TestApiRequest | TestResponse |
| `/api/v1/apis/import` | POST | 导入接口 | ImportApiRequest | MessageResponse |

### 测试用例管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/test-cases` | GET | 获取测试用例列表 | Query参数 | TestCaseListResponse |
| `/api/v1/test-cases` | POST | 创建测试用例 | CreateTestCaseRequest | TestCaseResponse |
| `/api/v1/test-cases/{id}` | GET | 获取测试用例详情 | - | TestCaseResponse |
| `/api/v1/test-cases/{id}` | PUT | 更新测试用例 | UpdateTestCaseRequest | TestCaseResponse |
| `/api/v1/test-cases/{id}` | DELETE | 删除测试用例 | - | MessageResponse |
| `/api/v1/test-cases/{id}/run` | POST | 执行单个测试用例 | RunTestCaseRequest | ExecutionResponse |
| `/api/v1/test-cases/{id}/copy` | POST | 复制测试用例 | - | TestCaseResponse |

### 测试场景管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/test-scenarios` | GET | 获取测试场景列表 | Query参数 | TestScenarioListResponse |
| `/api/v1/test-scenarios` | POST | 创建测试场景 | CreateTestScenarioRequest | TestScenarioResponse |
| `/api/v1/test-scenarios/{id}` | GET | 获取测试场景详情 | - | TestScenarioResponse |
| `/api/v1/test-scenarios/{id}` | PUT | 更新测试场景 | UpdateTestScenarioRequest | TestScenarioResponse |
| `/api/v1/test-scenarios/{id}` | DELETE | 删除测试场景 | - | MessageResponse |
| `/api/v1/test-scenarios/{id}/steps` | GET | 获取场景步骤 | - | StepListResponse |
| `/api/v1/test-scenarios/{id}/steps` | POST | 添加场景步骤 | AddStepRequest | StepResponse |
| `/api/v1/test-scenarios/{id}/run` | POST | 执行测试场景 | RunScenarioRequest | ExecutionResponse |

### 变量管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/variables` | GET | 获取变量列表 | Query参数(scope) | VariableListResponse |
| `/api/v1/variables` | POST | 创建变量 | CreateVariableRequest | VariableResponse |
| `/api/v1/variables/{id}` | GET | 获取变量详情 | - | VariableResponse |
| `/api/v1/variables/{id}` | PUT | 更新变量 | UpdateVariableRequest | VariableResponse |
| `/api/v1/variables/{id}` | DELETE | 删除变量 | - | MessageResponse |
| `/api/v1/variables/global` | GET | 获取全局变量 | - | VariableListResponse |
| `/api/v1/variables/personal` | GET | 获取个人变量 | - | VariableListResponse |
| `/api/v1/variables/environment/{env_id}` | GET | 获取环境变量 | - | VariableListResponse |

### 环境管理API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/environments` | GET | 获取环境列表 | - | EnvironmentListResponse |
| `/api/v1/environments` | POST | 创建环境 | CreateEnvironmentRequest | EnvironmentResponse |
| `/api/v1/environments/{id}` | GET | 获取环境详情 | - | EnvironmentResponse |
| `/api/v1/environments/{id}` | PUT | 更新环境 | UpdateEnvironmentRequest | EnvironmentResponse |
| `/api/v1/environments/{id}` | DELETE | 删除环境 | - | MessageResponse |

### 测试执行和报告API

| 端点 | 方法 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/v1/executions` | GET | 获取执行历史 | Query参数 | ExecutionListResponse |
| `/api/v1/executions/{id}` | GET | 获取执行详情 | - | ExecutionResponse |
| `/api/v1/executions/{id}/results` | GET | 获取执行结果 | - | ResultListResponse |
| `/api/v1/executions/{id}/report` | GET | 获取执行报告 | - | ReportResponse |
| `/api/v1/executions/{id}/stop` | POST | 停止执行 | - | MessageResponse |
| `/api/v1/executions/batch` | POST | 批量执行测试 | BatchExecutionRequest | ExecutionResponse |
| `/api/v1/reports/summary` | GET | 获取统计报告 | Query参数 | SummaryReportResponse |

## 业务逻辑层设计

### 接口测试业务架构

```mermaid
graph TD
    A[接口测试服务] --> B[接口管理]
    A --> C[测试用例管理]
    A --> D[测试场景管理]
    A --> E[变量管理]
    A --> F[测试执行]
    
    B --> G[接口创建]
    B --> H[接口编辑]
    B --> I[接口分类]
    B --> J[接口导入]
    
    C --> K[用例创建]
    C --> L[用例编辑]
    C --> M[用例复制]
    C --> N[断言管理]
    
    D --> O[场景创建]
    D --> P[步骤管理]
    D --> Q[数据传递]
    
    E --> R[全局变量]
    E --> S[环境变量]
    E --> T[个人变量]
    E --> U[临时变量]
    
    F --> V[单个测试]
    F --> W[场景测试]
    F --> X[批量测试]
    F --> Y[结果收集]
```

### 测试执行流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant API as API网关
    participant TestService as 测试服务
    participant VariableService as 变量服务
    participant Celery as 异步任务
    participant HttpClient as HTTP客户端
    participant MySQL as MySQL数据库
    participant Redis as Redis缓存
    
    User->>API: 提交测试执行请求
    API->>TestService: 创建执行任务
    TestService->>MySQL: 保存执行记录
    TestService->>Celery: 提交异步任务
    TestService-->>API: 返回执行ID
    API-->>User: 执行已开始
    
    Note over Celery: 异步执行测试
    Celery->>VariableService: 获取变量配置
    VariableService->>MySQL: 查询各类变量
    VariableService->>Redis: 获取临时变量
    VariableService-->>Celery: 返回变量数据
    
    loop 执行测试用例
        Celery->>Celery: 解析变量和参数
        Celery->>HttpClient: 发送HTTP请求
        HttpClient-->>Celery: 返回响应结果
        Celery->>Celery: 执行断言验证
        Celery->>MySQL: 保存测试结果
        Celery->>Redis: 更新临时变量
    end
    
    Celery->>MySQL: 更新执行状态
    Celery->>Redis: 发布执行完成事件
    
    User->>API: 查询执行结果
    API->>TestService: 获取执行结果
    TestService->>MySQL: 查询结果数据
    TestService-->>API: 返回结果数据
    API-->>User: 测试结果报告

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as API网关
    participant AuthService as 认证服务
    participant UserService as 用户服务
    participant Redis as Redis缓存
    participant MySQL as MySQL数据库
    
    Client->>API: 登录请求(username, password)
    API->>AuthService: 验证用户凭证
    AuthService->>UserService: 获取用户信息
    UserService->>MySQL: 查询用户数据
    MySQL-->>UserService: 返回用户信息
    UserService-->>AuthService: 用户验证结果
    
    alt 验证成功
        AuthService->>AuthService: 生成随机Token(使用uuid/secrets)
        AuthService->>UserService: 获取用户权限
        UserService->>MySQL: 查询用户角色和权限
        MySQL-->>UserService: 返回权限数据
        UserService-->>AuthService: 用户权限列表
        AuthService->>Redis: 存储Token信息
        Note over Redis: token:access:{token}<br/>{“user_id”: 1, “username”: “john”,<br/>“permissions”: [...], “expire_time”: timestamp}
        Redis-->>AuthService: 存储确认
        AuthService->>Redis: 更新用户Token列表
        Note over Redis: user:tokens:{user_id}<br/>[“token1”, “token2”, ...]
        AuthService-->>API: 返回Token
        API-->>Client: 登录成功响应
    else 验证失败
        AuthService-->>API: 返回错误信息
        API-->>Client: 登录失败响应
    end
```

### 变量管理机制

```mermaid
graph TD
    A[变量管理系统] --> B[全局变量]
    A --> C[环境变量]
    A --> D[个人变量]
    A --> E[临时变量]
    
    B --> F[所有用户可访问]
    B --> G[管理员可编辑]
    B --> H[存储在MySQL]
    
    C --> I[环境相关配置]
    C --> J[所有用户可访问]
    C --> K[管理员可编辑]
    C --> L[存储在MySQL]
    
    D --> M[用户私有变量]
    D --> N[仅创建者可访问]
    D --> O[存储在MySQL]
    
    E --> P[测试执行期间使用]
    E --> Q[数据传递变量]
    E --> R[存储在Redis]
    E --> S[执行结束后清理]
    
    T[变量解析] --> U[语法: {{variable_name}}]
    T --> V[支持嵌套解析]
    T --> W[支持函数调用]
    T --> X[优先级: 临时 > 个人 > 环境 > 全局]

### 权限验证机制

```mermaid
graph TD
    A[请求到达] --> B[提取Token]
    B --> C{从 Redis获取Token信息}
    C -->|不存在| D[返回401未授权]
    C -->|存在| E[检查Token过期时间]
    E -->|已过期| F[删除过期Token]
    F --> D
    E -->|未过期| G[解析用户信息]
    G --> H[从 Token信息获取用户权限]
    H --> I{权限检查}
    I -->|通过| J[执行业务逻辑]
    I -->|拒绝| K[返回403禁止访问]
    J --> L[返回结果]
```

### 测试平台专用功能设计

### 接口管理功能

#### 接口定义管理
- 支持RESTful API、GraphQL、WebSocket等多种接口类型
- 接口分组管理，支持按模块、版本、环境分类
- 动态参数解析，支持Path、Query、Header、Body参数
- 请求/响应模式定义，支持JSON Schema验证
- 接口文档自动生成和维护

#### 接口导入功能
- 支持Swagger/OpenAPI文档导入
- 支持Postman Collection导入
- 支持cURL命令导入
- 支持HAR文件导入

### 测试用例管理

#### 单元测试设计
- 基于单个接口的测试用例创建
- 多种断言类型：响应状态码、响应时间、JSON路径、正则表达式
- 数据驱动测试，支持CSV/Excel数据文件
- 参数化测试，支持变量替换和动态生成
- 前置和后置脚本，支持JavaScript执行

#### 测试用例组织
- 按功能模块分类管理
- 测试用例标签系统
- 支持用例复制、导入导出
- 版本控制和历史记录

### 测试场景管理

#### 场景流程设计
- 支持复杂业务流程的测试场景搭建
- 测试步骤之间的数据传递
- 条件判断和分支执行
- 循环执行和并发执行
- 异常处理和重试机制

#### 场景编排功能
- 可视化流程编辑器
- 拖拽式步骤组合
- 步骤顺序调整和依赖管理
- 场景模板和快速复制

### 变量管理系统

#### 全局变量
- 系统级配置变量
- 所有用户共享访问
- 管理员权限控制
- 支持加密存储敏感信息

#### 环境变量
- 按环境维度管理(开发、测试、预发布、生产)
- 环境间变量继承和覆盖
- 环境切换时变量自动适配
- 支持动态环境配置

#### 个人变量仓库
- 用户私有变量空间
- 支持变量分组管理
- 变量共享和协作功能
- 变量使用统计和分析

#### 临时变量
- 测试执行过程中的动态变量
- 步骤间数据传递和共享
- 自动清理机制
- 支持复杂数据类型存储

### 测试执行引擎

#### 执行模式
- 单个测试用例执行
- 测试场景批量执行
- 定时任务和自动化测试
- 并发执行和负载测试

#### 执行管理
- 实时执行状态监控
- 执行过程日志记录
- 支持执行中断和继续
- 执行队列管理和优先级控制

### 结果分析和报告

#### 测试结果展示
- 实时测试结果反馈
- 详细的请求/响应数据展示
- 断言失败原因分析
- 性能指标统计(响应时间、吞吐量等)

#### 报告生成
- 多种报告格式(HTML、PDF、Excel)
- 自定义报告模板
- 趋势分析和历史对比
- 自动报告发送和通知

## 中间件和拦截器设计

### 测试平台专用中间件

| 中间件名称 | 功能 | 应用范围 |
|------------|------|----------|
| RedisTokenMiddleware | Redis Token验证 | 需要认证的API端点 |
| PermissionMiddleware | 权限验证 | 需要授权的API端点 |
| LoggingMiddleware | 请求日志记录 | 所有API端点 |
| CORSMiddleware | 跨域资源共享 | 所有API端点 |
| RateLimitMiddleware | 请求频率限制 | 公开API端点 |
| TestExecutionMiddleware | 测试执行监控 | 测试执行相关API |
| VariableResolverMiddleware | 变量解析 | 测试数据处理API |
| ExecutionTimeMiddleware | 执行时间统计 | 所有测试相关API |

### 中间件执行顺序

```mermaid
graph LR
    A[请求] --> B[CORS中间件]
    B --> C[日志中间件]
    C --> D[限流中间件]
    D --> E[Redis Token认证中间件]
    E --> F[权限验证中间件]
    F --> G[业务处理]
    G --> H[响应]
```

### 异步任务设计

| 任务类型 | 任务名称 | 执行频率 | 说明 |
|----------|----------|----------|------|
| 测试执行 | execute_single_test | 即时执行 | 单个测试用例执行 |
| 测试执行 | execute_scenario_test | 即时执行 | 测试场景执行 |
| 测试执行 | execute_batch_test | 即时执行 | 批量测试执行 |
| 报告生成 | generate_test_report | 延迟执行 | 测试报告生成 |
| 数据清理 | cleanup_temp_data | 定时执行 | 清理临时数据和过期缓存 |
| 统计分析 | calculate_statistics | 定时执行 | 计算测试统计数据 |
| 通知推送 | send_notification | 即时执行 | 测试结果通知推送 |

## 缓存策略设计

### Redis使用场景
| 场景 | Key格式 | 过期时间 | 说明 |
|------|---------|----------|------|
| Access Token | `token:access:{token_value}` | 2小时 | 访问令牌信息 |
| Refresh Token | `token:refresh:{token_value}` | 7天 | 刷新令牌信息 |
| 用户Token列表 | `user:tokens:{user_id}` | 7天 | 用户所有有效Token |
| 用户权限缓存 | `user:permissions:{user_id}` | 30分钟 | 用户权限列表 |
| 用户会话 | `user:session:{user_id}` | 24小时 | 用户会话信息 |
| 登录失败次数 | `login:attempts:{ip}` | 1小时 | 防暴力破解 |
| 登录验证码 | `login:captcha:{session_id}` | 5分钟 | 登录验证码 |
| 测试执行状态 | `test:execution:{execution_id}` | 24小时 | 测试执行实时状态 |
| 临时变量 | `temp:vars:{execution_id}` | 2小时 | 测试执行中的临时变量 |
| 测试结果缓存 | `test:results:{execution_id}` | 1小时 | 测试结果快照 |
| API响应缓存 | `api:response:{api_id}:{hash}` | 10分钟 | API响应缓存(可选) |

### 缓存更新策略

```mermaid
graph TD
    A[数据变更] --> B{影响权限?}
    B -->|是| C[清除权限缓存]
    B -->|否| D[保持缓存]
    C --> E[下次请求重新加载]
    
    F[用户登出] --> G[清除所有Token]
    G --> H[清除会话信息]
    G --> I[从用户Token列表删除]
    
    J[权限变更] --> K[清除所有相关用户权限缓存]
    
    L[Token刷新] --> M[删除旧Token]
    M --> N[生成新Token]
    N --> O[更新用户Token列表]
```

## 安全机制设计

### 密码安全策略

| 策略项 | 配置 | 说明 |
|--------|------|------|
| 密码复杂度 | 最少8位，包含大小写字母、数字 | 基础安全要求 |
| 密码加密 | bcrypt + salt | 防彩虹表攻击 |
| 密码历史 | 记录最近5次密码 | 防重复使用 |
| 登录失败锁定 | 5次失败锁定30分钟 | 防暴力破解 |

### Token安全机制

```mermaid
graph TD
    A[Token生成] --> B[使用安全随机数生成器]
    A --> C[设置过期时间]
    A --> D[存储用户信息和权限]
    A --> E[记录登录IP和设备信息]
    
    F[Token验证] --> G[从 Redis获取Token数据]
    G --> H[检查过期时间]
    H --> I[验证IP地址(可选)]
    I --> J[检查黑名单]
    J --> K[验证用户状态]
    
    L[Token刷新] --> M[验证Refresh Token]
    M --> N[生成新的Access Token]
    N --> O[延长Refresh Token有效期]
    
    P[安全策略] --> Q[单设备登录限制]
    P --> R[异地登录检测]
    P --> S[频繁请求限制]
```

## 日志记录策略

### 日志级别定义

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| DEBUG | 调试信息 | 函数参数、中间变量 |
| INFO | 一般信息 | 用户登录、业务操作 |
| WARNING | 警告信息 | 权限不足、参数异常 |
| ERROR | 错误信息 | 数据库连接失败、业务异常 |
| CRITICAL | 严重错误 | 系统崩溃、安全威胁 |

### 安全审计日志

```mermaid
graph TD
    A[用户操作] --> B[记录操作日志]
    B --> C[用户ID]
    B --> D[操作类型]
    B --> E[操作时间]
    B --> F[操作结果]
    B --> G[IP地址]
    B --> H[用户代理]
    
    I[安全事件] --> J[记录安全日志]
    J --> K[登录失败]
    J --> L[权限违规]
    J --> M[异常访问]
```

## 异常处理机制

### 异常层次结构

| 异常类型 | 父类 | HTTP状态码 | 说明 |
|----------|------|------------|------|
| ValidationError | HTTPException | 422 | 数据验证错误 |
| AuthenticationError | HTTPException | 401 | 认证失败 |
| AuthorizationError | HTTPException | 403 | 权限不足 |
| NotFoundError | HTTPException | 404 | 资源不存在 |
| ConflictError | HTTPException | 409 | 数据冲突 |
| DatabaseError | HTTPException | 500 | 数据库错误 |

### 异常处理流程

```mermaid
graph TD
    A[异常发生] --> B[异常捕获]
    B --> C[记录错误日志]
    C --> D[判断异常类型]
    D --> E[格式化错误响应]
    E --> F[返回客户端]
    
    G[敏感信息] --> H[脱敏处理]
    H --> E
```

### 单元测试覆盖

| 测试层级 | 覆盖范围 | 工具 | 目标覆盖率 |
|----------|----------|------|------------|
| 接口服务测试 | API接口功能验证 | pytest + httpx | 95%+ |
| 业务逻辑测试 | 业务逻辑验证 | pytest + unittest.mock | 90%+ |
| 数据访问测试 | 数据库操作验证 | pytest + pytest-asyncio | 85%+ |
| 工具类测试 | 工具函数验证 | pytest | 95%+ |
| 集成测试 | 系统集成验证 | pytest + testcontainers | 80%+ |
| 测试平台功能测试 | 测试执行引擎验证 | pytest + celery-test | 90%+ |

### 测试数据管理

```mermaid
graph TD
    A[测试开始] --> B[创建测试数据库]
    B --> C[运行数据迁移]
    C --> D[加载测试夹具]
    D --> E[执行测试用例]
    E --> F[清理测试数据]
    F --> G[删除测试数据库]
```

### 安全测试要点

| 测试类型 | 测试内容 | 验证点 |
|----------|----------|--------|
| 认证测试 | 登录功能 | 有效/无效凭证处理 |
| 授权测试 | 权限控制 | 角色权限边界验证 |
| 输入验证 | 数据安全 | SQL注入、XSS防护 |
| 会话管理 | Token安全 | Token生成、验证、过期 |
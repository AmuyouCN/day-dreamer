# 接口自动化测试平台 - 启动指南

## 项目概述

基于FastAPI的接口自动化测试平台，提供完整的用户权限管理、接口测试、变量管理、异步任务处理和测试报告生成功能。

## 技术栈

- **Web框架**: FastAPI (异步)
- **数据库**: MySQL + Tortoise ORM
- **缓存**: Redis
- **任务队列**: Celery
- **认证**: JWT Token + Redis
- **配置管理**: Pydantic Settings
- **日志**: Loguru
- **容器化**: Docker

## 项目结构

```
backend/
├── app/
│   ├── api/v1/          # API路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据模型
│   ├── services/        # 业务服务
│   ├── tasks/           # 异步任务
│   └── utils/           # 工具类
├── tests/               # 测试文件
├── logs/                # 日志文件
├── reports/             # 测试报告
├── docker-compose.yml   # Docker配置
├── requirements.txt     # 依赖包
└── worker.py           # Celery Worker启动
```

## 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 环境配置

创建 `.env` 文件：

```env
# 应用配置
APP_NAME=接口自动化测试平台
APP_VERSION=1.0.0
DEBUG=true

# 数据库配置
DATABASE_URL=mysql://username:password@localhost:3306/test_platform
DATABASE_ECHO=false

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 其他配置
ALLOWED_HOSTS=["*"]
```

## 数据库初始化

```bash
# 执行数据库初始化脚本
mysql -u username -p database_name < init_db.sql
```

## 启动服务

### 1. 启动主应用

```bash
# 开发模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 启动Celery Worker

```bash
# 方式一：使用启动脚本
python worker.py

# 方式二：直接使用celery命令
celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

### 3. 启动Celery Beat（可选，用于定时任务）

```bash
celery -A app.core.celery_app beat --loglevel=info
```

## Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

## API文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主要功能模块

### 1. 用户认证系统
- 用户注册、登录、登出
- 基于Redis的Token管理
- RBAC权限控制
- 密码加密和验证

### 2. 接口管理
- 接口定义和分组管理
- 支持多种HTTP方法
- 请求头、参数、Body配置
- 接口文档生成

### 3. 测试用例管理
- 测试用例CRUD操作
- 断言规则配置
- 数据提取和关联
- 用例分组和排序

### 4. 环境管理
- 多环境配置支持
- 环境变量管理
- 动态环境切换

### 5. 变量管理
- 全局变量、环境变量、个人变量、临时变量
- 变量解析和替换
- 敏感数据脱敏
- 变量导入导出

### 6. 测试执行
- 单个用例执行
- 批量用例执行（串行/并行）
- 测试套件执行
- 异步任务处理

### 7. 测试报告
- 多格式报告生成（HTML、JSON、PDF、Excel）
- 测试结果统计分析
- 趋势报告
- 报告下载和分享

### 8. 系统维护
- 数据清理和备份
- 系统健康检查
- 日志管理
- 监控统计

## 默认账户

系统初始化后的默认管理员账户：

- **用户名**: admin
- **密码**: admin123

## 开发说明

### 添加新的API端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `app/main.py` 中注册路由
3. 添加相应的权限检查

### 添加新的异步任务

1. 在 `app/tasks/` 下创建任务文件
2. 在 `app/core/celery_app.py` 中配置任务路由
3. 在API中调用任务

### 数据库模型修改

1. 修改 `app/models/` 下的模型文件
2. 生成数据库迁移脚本
3. 更新 `init_db.sql` 脚本

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接字符串配置
   - 确认数据库用户权限

2. **Redis连接失败**
   - 检查Redis服务状态
   - 验证Redis配置
   - 检查网络连接

3. **Celery任务不执行**
   - 确认Celery Worker已启动
   - 检查任务队列配置
   - 查看Worker日志

4. **权限验证失败**
   - 检查Token是否有效
   - 验证用户权限配置
   - 确认中间件正常工作

### 日志查看

```bash
# 应用日志
tail -f logs/app.log

# Celery日志
tail -f logs/celery.log

# Docker日志
docker-compose logs -f
```

## 性能优化

1. **数据库优化**
   - 添加必要的数据库索引
   - 使用连接池
   - 定期清理过期数据

2. **缓存优化**
   - 使用Redis缓存热点数据
   - 设置合理的过期时间
   - 监控缓存命中率

3. **异步任务优化**
   - 合理设置Worker数量
   - 使用不同队列处理不同类型任务
   - 监控任务执行状态

## 监控和维护

1. **健康检查端点**
   - `/health` - 基础健康检查
   - `/api/v1/tasks/stats` - 任务统计
   - `/api/v1/reports/statistics/summary` - 报告统计

2. **定期维护任务**
   - 清理过期临时变量
   - 清理过期测试报告
   - 系统数据备份

3. **监控指标**
   - API响应时间
   - 任务队列长度
   - 数据库连接数
   - 内存和CPU使用率

## 扩展开发

项目采用模块化设计，支持功能扩展：

1. **插件系统**: 支持自定义断言器和数据提取器
2. **通知系统**: 支持邮件、钉钉、企业微信等通知方式
3. **CI/CD集成**: 支持Jenkins、GitLab CI等持续集成
4. **数据源扩展**: 支持更多数据库和数据格式

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
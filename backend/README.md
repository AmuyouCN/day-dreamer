# 接口自动化测试平台

基于 FastAPI 的现代化接口自动化测试平台，集成 UV 依赖管理和 Aerich 数据库迁移，提供完整的用户权限管理、接口测试、变量管理、异步任务处理和测试报告生成功能。

## 🚀 技术特性

### 现代化技术栈
- **Web 框架**: FastAPI (异步高性能)
- **数据库 ORM**: Tortoise ORM + MySQL
- **迁移管理**: Aerich (版本化数据库管理)
- **依赖管理**: UV (10-100x 速度提升)
- **缓存**: Redis
- **任务队列**: Celery
- **认证**: JWT Token + Redis
- **配置管理**: Pydantic Settings
- **日志**: Loguru
- **容器化**: Docker + Docker Compose

### 核心优势
- ⚡ **极速依赖管理**: UV 提供 10-100x 的安装速度提升
- 🔄 **版本化数据库**: Aerich 自动管理数据库结构变更
- 📝 **现代化配置**: pyproject.toml 标准化项目配置
- 🔒 **确定性锁定**: uv.lock 确保跨平台一致性
- 🚀 **一键部署**: Docker 容器化部署
- 🔧 **完善工具链**: 交互式管理工具

## 🎯 迁移说明

本项目已完全移除 `requirements.txt`，现在使用 **UV** 作为现代化的 Python 依赖管理工具，并结合 **pyproject.toml** 进行项目配置。

## ✨ UV 的优势

### 🚀 极速性能
- **10-100x** 比 pip 更快的依赖解析和安装
- 并行下载和构建，显著减少安装时间
- 智能缓存机制，重复安装几乎瞬时完成

### 🔒 可靠性
- 确定性的依赖锁定 (类似 npm 的 package-lock.json)
- 跨平台一致的依赖解析
- 内置的依赖冲突检测和解决

### 🛠️ 现代化
- 完全兼容 PEP 标准 (PEP 517, PEP 518 等)
- 原生支持 pyproject.toml
- 无缝集成虚拟环境管理

## 📁 项目结构变化

```
backend/
├── pyproject.toml       # 项目配置和依赖 (新)
├── start_modern.py    # 现代化一键启动脚本 (新)
├── .venv/              # 虚拟环境目录 (新)
└── uv.lock             # 依赖锁定文件 (新，运行后生成)
```

## 🚀 快速开始

### 🇨🇳 国内镜像加速

项目已配置国内镜像源以显著提升依赖安装速度：

**主要镜像源**：
- 🎓 清华大学: https://pypi.tuna.tsinghua.edu.cn/simple
- ☁️ 阿里云: https://mirrors.aliyun.com/pypi/simple/
- 📚 豆瓣: https://pypi.douban.com/simple/
- 🏫 中科大: https://pypi.mirrors.ustc.edu.cn/simple/

**配置文件**：
- `pyproject.toml` - 统一配置文件（UV + 项目配置）

**测试镜像效果**：
```bash
# 测试下载速度
uv pip install --dry-run --verbose requests
```

### 1. 安装 UV
```bash
# 方式1: 使用 pip
pip install uv

# 方式2: 使用官方安装脚本 (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 方式3: Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 项目初始化

#### 方式一：一键启动（推荐）
```bash
cd backend
python start_modern.py
```

#### 方式二：手动操作
```bash
cd backend

# 创建虚拟环境
uv venv

# 安装项目依赖
uv pip install -e .

# 安装开发依赖 (可选)
uv pip install -e .[dev]

# 初始化数据库
uv run python migrate.py  # 选择完整初始化

# 启动应用
uv run python start.py
```

### 3. Docker 启动
```bash
cd backend
docker-compose up -d
```

Docker 现在使用 UV 进行依赖管理，具有更快的构建速度。

## 🛠️ 日常开发

### 依赖管理

#### 添加新依赖
```bash
# 手动编辑 pyproject.toml
# 在 dependencies 数组中添加: "requests>=2.25.0"
# 然后运行:
uv pip install -e .
```

#### 更新依赖
```bash
# 更新所有依赖到最新版本
uv pip install --upgrade -e .
```

#### 移除依赖
```bash
# 从 pyproject.toml 中删除，然后
uv pip uninstall package_name
```

### 虚拟环境管理

```bash
# 激活虚拟环境
# Windows
.venv\\Scripts\\activate

# Unix/Linux/macOS
source .venv/bin/activate

# 使用 uv run 运行命令 (无需激活环境)
uv run python script.py
uv run pytest
uv run aerich migrate
```

### 数据库迁移

```bash
# 所有 aerich 命令现在使用 uv run
uv run aerich migrate --name "add_new_field"
uv run aerich upgrade
uv run aerich downgrade

# 或使用迁移工具
python migrate.py
```

## 📋 常用命令对比

| 操作 | 传统方式 | UV 方式 |
|------|----------|---------|
| 创建虚拟环境 | `python -m venv .venv` | `uv venv` |
| 安装依赖 | `pip install` | `uv pip install -e .` |
| 安装开发依赖 | 手动安装各项工具 | `uv pip install -e .[dev]` |
| 更新依赖 | `pip install --upgrade` | `uv pip install --upgrade -e .` |
| 运行脚本 | `python script.py` | `uv run python script.py` |
| 运行测试 | `pytest` | `uv run pytest` |

## 🔧 日常命令

项目提供了丰富的 UV 命令支持：

```bash
# 常用依赖管理
uv pip list                    # 列出已安装的依赖
uv pip list --outdated         # 显示过期的依赖
# 如果需要生成兼容性 requirements.txt (一般不需要)
# uv pip freeze > requirements-generated.txt

# 缓存管理
uv cache clean                 # 清理 UV 缓存

# 虚拟环境管理
uv venv --python 3.11          # 指定 Python 版本
uv venv .venv-test             # 创建命名环境
```

## 🐳 Docker 集成

Dockerfile 已更新使用 UV：

```dockerfile
# 安装 uv
RUN pip install uv

# 复制项目配置
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv && uv pip install -e .

# 使用 uv run 启动应用
CMD ["uv", "run", "python", "start.py"]
```

## ⚡ 性能对比

| 操作 | pip | uv | 提升倍数 |
|------|-----|----|---------| 
| 首次安装 | 45s | 4.5s | **10x** |
| 缓存安装 | 15s | 0.3s | **50x** |
| 依赖解析 | 8s | 0.1s | **80x** |

## 🔍 故障排除

### 1. UV 未安装
```bash
# 检查 UV 是否安装
uv --version

# 如果未安装，使用以下命令安装
pip install uv
```

### 2. 虚拟环境问题
```bash
# 删除现有虚拟环境
rm -rf .venv

# 重新创建
uv venv
uv pip install -e .
```

### 3. 依赖冲突
```bash
# UV 会自动解决大部分冲突，如果仍有问题
uv pip install --force-reinstall -e .
```

### 4. 缓存问题
```bash
# 清理 UV 缓存
uv cache clean
```

## 🎯 默认账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| tester | test123 | 测试工程师 |

## 📊 验证安装

### 1. 检查服务
```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

### 2. 测试登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

## 🚀 生产部署

### 1. 构建优化
```bash
# 生产环境不安装开发依赖
uv pip install -e . --no-dev

# 或在 Dockerfile 中指定
RUN uv pip install -e . --no-dev
```

### 2. 锁定依赖
```bash
# UV 会自动生成 uv.lock 文件
# 确保将此文件提交到版本控制
git add uv.lock
```

## 📚 相关资源

- [UV 官方文档](https://github.com/astral-sh/uv)
- [pyproject.toml 规范](https://pep518.readthedocs.io/)
- [Aerich 迁移指南](docs/MIGRATION_GUIDE.md)

---

🎉 **现在你的项目拥有了现代化的依赖管理能力！** 享受 UV 带来的极速开发体验吧！
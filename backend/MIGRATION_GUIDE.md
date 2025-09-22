# Aerich 迁移指南

## 📋 迁移改造完成清单

✅ **核心配置**
- [x] 添加 aerich 依赖到 requirements.txt
- [x] 创建 pyproject.toml 配置文件
- [x] 创建 app/core/database_config.py 专用配置
- [x] 修改 database.py 禁用自动生成表结构

✅ **初始化脚本**
- [x] 创建 init_data.py 初始数据插入脚本
- [x] 创建 migrate.py 交互式迁移管理工具
- [x] 创建 start_modern.py 现代化一键启动脚本

✅ **Docker 配置**
- [x] 修改 docker-compose.yml 支持 aerich
- [x] 添加 db-migrate 初始化服务
- [x] 移除 init_db.sql 挂载

✅ **文档更新**
- [x] 创建统一的主 README.md 文档
- [x] 更新 STARTUP.md 启动流程
- [x] 添加迁移相关说明

## 🚀 立即开始使用

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 选择启动方式

#### 方式一：一键启动（推荐新手）
```bash
python start_modern.py
```

#### 方式二：交互式管理
```bash
python migrate.py
# 选择 "8. 完整初始化"
```

#### 方式三：Docker 启动
```bash
docker-compose up -d
```

#### 方式四：手动操作
```bash
# 1. 初始化 aerich
aerich init -t app.core.database_config.TORTOISE_CONFIG

# 2. 创建初始迁移
aerich init-db

# 3. 插入初始数据
python init_data.py

# 4. 启动应用
python start.py
```

## 🔍 验证迁移成功

### 1. 检查迁移目录
```bash
ls migrations/
# 应该看到 models/ 目录和配置文件
```

### 2. 验证数据库表
连接到 MySQL 检查表是否正确创建：
```sql
USE test_platform_dev;
SHOW TABLES;
-- 应该看到所有的表，包括 aerich 表
```

### 3. 验证初始数据
```sql
SELECT * FROM users;
SELECT * FROM roles;
SELECT * FROM permissions;
-- 应该看到默认用户和权限数据
```

### 4. 测试 API
```bash
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

## 🛠️ 日常开发流程

### 1. 修改数据模型
编辑 `app/models/` 下的文件，例如：
```python
# app/models/user.py
class User(Model):
    # ... 现有字段 ...
    avatar = fields.CharField(max_length=255, null=True)  # 新增字段
```

### 2. 生成迁移
```bash
aerich migrate --name "add_user_avatar"
```

### 3. 应用迁移
```bash
aerich upgrade
```

### 4. 提交代码
```bash
git add migrations/
git commit -m "Add user avatar field"
```

## 🚨 注意事项

### 1. 团队协作
- 新成员加入时，只需运行 `aerich upgrade`
- 迁移文件必须提交到版本控制
- 避免多人同时生成迁移文件

### 2. 生产部署
```bash
# 生产环境部署时
aerich upgrade  # 先应用迁移
python start.py  # 再启动应用
```

### 3. 数据备份
```bash
# 重要变更前备份数据库
mysqldump -h localhost -u root -p test_platform_dev > backup.sql
```

### 4. 错误处理
如果迁移失败：
```bash
# 查看当前状态
aerich heads

# 查看历史
aerich history

# 回滚到上一个版本
aerich downgrade
```

## 🎯 默认账户信息

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| tester | test123 | 测试工程师 |

## 📞 问题排查

### 1. Aerich 命令失败
```bash
# 检查配置
cat pyproject.toml

# 检查数据库连接
python -c "from app.core.database_config import TORTOISE_CONFIG; print(TORTOISE_CONFIG)"
```

### 2. 数据库连接问题
```bash
# 检查 MySQL 是否运行
docker ps | grep mysql

# 检查连接
mysql -h localhost -u root -p
```

### 3. 迁移冲突
```bash
# 删除迁移目录重新初始化（开发阶段）
rm -rf migrations/
aerich init -t app.core.database_config.TORTOISE_CONFIG
aerich init-db
```

## 📚 参考资源

- [Aerich 官方文档](https://github.com/tortoise/aerich)
- [Tortoise ORM 文档](https://tortoise-orm.readthedocs.io/)
- [项目主文档](README.md)

---

🎉 **恭喜！** 你已经成功将项目迁移到 Aerich 管理方式。现在可以享受版本化数据库管理的便利了！
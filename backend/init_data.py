#!/usr/bin/env python
"""
数据库初始化脚本

使用 aerich 初始化数据库并插入初始数据
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from tortoise import Tortoise
from passlib.context import CryptContext
from app.models.user import User
from app.models.role import Role  
from app.models.permission import Permission
from app.models.environment import Environment
from app.models.variable import Variable
from app.core.database_config import TORTOISE_CONFIG
from loguru import logger

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_database():
    """初始化数据库连接"""
    try:
        await Tortoise.init(config=TORTOISE_CONFIG)
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        raise

async def insert_initial_data():
    """插入初始数据"""
    logger.info("开始插入初始数据...")
    
    try:
        # 插入默认环境
        environments_data = [
            {"name": "development", "description": "开发环境", "config": {"base_url": "http://localhost:8000"}},
            {"name": "testing", "description": "测试环境", "config": {"base_url": "http://test.example.com"}},
            {"name": "production", "description": "生产环境", "config": {"base_url": "https://api.example.com"}}
        ]
        
        for env_data in environments_data:
            env, created = await Environment.get_or_create(
                name=env_data["name"],
                defaults={
                    "description": env_data["description"], 
                    "config": env_data["config"]
                }
            )
            if created:
                logger.info(f"创建环境: {env.name}")

        # 插入默认角色
        roles_data = [
            {"name": "管理员", "description": "系统管理员，拥有所有权限"},
            {"name": "测试负责人", "description": "测试项目负责人"},
            {"name": "高级测试工程师", "description": "高级测试工程师"},
            {"name": "测试工程师", "description": "一般测试工程师"},
            {"name": "实习生", "description": "实习生，只读权限"}
        ]
        
        created_roles = {}
        for role_data in roles_data:
            role, created = await Role.get_or_create(
                name=role_data["name"],
                defaults={"description": role_data["description"]}
            )
            created_roles[role.name] = role
            if created:
                logger.info(f"创建角色: {role.name}")

        # 插入权限
        permissions_data = [
            {"name": "user:read", "resource": "user", "action": "read", "description": "查看用户信息"},
            {"name": "user:write", "resource": "user", "action": "write", "description": "编辑用户信息"},
            {"name": "user:delete", "resource": "user", "action": "delete", "description": "删除用户"},
            {"name": "user:self", "resource": "user", "action": "self", "description": "管理自己的信息"},
            {"name": "role:read", "resource": "role", "action": "read", "description": "查看角色信息"},
            {"name": "role:write", "resource": "role", "action": "write", "description": "编辑角色信息"},
            {"name": "permission:read", "resource": "permission", "action": "read", "description": "查看权限信息"},
            {"name": "api:read", "resource": "api", "action": "read", "description": "查看接口定义"},
            {"name": "api:write", "resource": "api", "action": "write", "description": "编辑接口定义"},
            {"name": "api:delete", "resource": "api", "action": "delete", "description": "删除接口定义"},
            {"name": "test:execute", "resource": "test", "action": "execute", "description": "执行测试"},
            {"name": "test:manage", "resource": "test", "action": "manage", "description": "管理测试用例"},
            {"name": "test:read", "resource": "test", "action": "read", "description": "查看测试信息"},
            {"name": "report:read", "resource": "report", "action": "read", "description": "查看测试报告"},
            {"name": "variable:global", "resource": "variable", "action": "global", "description": "管理全局变量"},
            {"name": "variable:personal", "resource": "variable", "action": "personal", "description": "管理个人变量"},
            {"name": "system:admin", "resource": "system", "action": "admin", "description": "系统管理权限"}
        ]
        
        created_permissions = {}
        for perm_data in permissions_data:
            permission, created = await Permission.get_or_create(
                name=perm_data["name"],
                defaults={
                    "resource": perm_data["resource"],
                    "action": perm_data["action"],
                    "description": perm_data["description"]
                }
            )
            created_permissions[permission.name] = permission
            if created:
                logger.info(f"创建权限: {permission.name}")

        # 创建默认用户
        # 管理员用户 (密码: admin123)
        admin_password_hash = pwd_context.hash("admin123")
        admin_user, created = await User.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "password_hash": admin_password_hash,
                "full_name": "系统管理员",
                "is_active": True
            }
        )
        if created:
            logger.info("创建管理员用户: admin")

        # 测试用户 (密码: test123)
        test_password_hash = pwd_context.hash("test123")
        test_user, created = await User.get_or_create(
            username="tester",
            defaults={
                "email": "tester@example.com",
                "password_hash": test_password_hash,
                "full_name": "测试用户",
                "is_active": True
            }
        )
        if created:
            logger.info("创建测试用户: tester")

        # 分配角色权限
        admin_role = created_roles["管理员"]
        tester_role = created_roles["测试工程师"]
        leader_role = created_roles["测试负责人"]
        senior_role = created_roles["高级测试工程师"]
        intern_role = created_roles["实习生"]

        # 管理员拥有所有权限
        await admin_role.permissions.clear()
        for permission in created_permissions.values():
            await admin_role.permissions.add(permission)
        logger.info("为管理员角色分配所有权限")

        # 测试工程师基本权限
        tester_permissions = [
            "user:self", "api:read", "api:write", "test:execute",
            "test:manage", "test:read", "report:read", "variable:personal"
        ]
        await tester_role.permissions.clear()
        for perm_name in tester_permissions:
            if perm_name in created_permissions:
                await tester_role.permissions.add(created_permissions[perm_name])
        logger.info("为测试工程师角色分配权限")

        # 测试负责人权限
        leader_permissions = [
            "user:read", "user:self", "role:read", "api:read", "api:write", "api:delete",
            "test:execute", "test:manage", "test:read", "report:read", 
            "variable:global", "variable:personal"
        ]
        await leader_role.permissions.clear()
        for perm_name in leader_permissions:
            if perm_name in created_permissions:
                await leader_role.permissions.add(created_permissions[perm_name])
        logger.info("为测试负责人角色分配权限")

        # 高级测试工程师权限
        senior_permissions = [
            "user:self", "api:read", "api:write", "test:execute",
            "test:manage", "test:read", "report:read", "variable:personal"
        ]
        await senior_role.permissions.clear()
        for perm_name in senior_permissions:
            if perm_name in created_permissions:
                await senior_role.permissions.add(created_permissions[perm_name])
        logger.info("为高级测试工程师角色分配权限")

        # 实习生权限（只读）
        intern_permissions = ["user:self", "api:read", "test:read", "report:read"]
        await intern_role.permissions.clear()
        for perm_name in intern_permissions:
            if perm_name in created_permissions:
                await intern_role.permissions.add(created_permissions[perm_name])
        logger.info("为实习生角色分配权限")

        # 分配用户角色
        await admin_user.roles.clear()
        await admin_user.roles.add(admin_role)
        
        await test_user.roles.clear()
        await test_user.roles.add(tester_role)
        logger.info("为用户分配角色")

        # 插入全局变量
        variables_data = [
            {"name": "base_timeout", "value": "30", "type": "number", "scope": "global", "description": "默认超时时间（秒）"},
            {"name": "default_headers", "value": '{"Content-Type": "application/json", "Accept": "application/json"}', "type": "json", "scope": "global", "description": "默认请求头"},
            {"name": "api_version", "value": "v1", "type": "string", "scope": "global", "description": "API版本号"}
        ]
        
        for var_data in variables_data:
            variable, created = await Variable.get_or_create(
                name=var_data["name"],
                scope=var_data["scope"],
                defaults={
                    "value": var_data["value"],
                    "type": var_data["type"],
                    "description": var_data["description"]
                }
            )
            if created:
                logger.info(f"创建全局变量: {variable.name}")

        logger.info("初始数据插入完成！")
        
    except Exception as e:
        logger.error(f"插入初始数据失败: {e}")
        raise

async def main():
    """主函数"""
    logger.info("开始数据库初始化...")
    
    try:
        await init_database()
        await insert_initial_data()
        logger.info("数据库初始化完成！")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
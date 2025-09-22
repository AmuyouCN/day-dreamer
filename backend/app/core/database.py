"""
数据库连接和初始化模块

配置 Tortoise ORM 数据库连接和管理
"""

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
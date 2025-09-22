"""
Redis连接管理模块

管理Redis连接池和基础操作
"""

import aioredis
from typing import Optional
from app.core.config import settings
from loguru import logger


class RedisManager:
    """Redis连接管理器"""
    
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
            logger.info("Redis连接初始化成功")
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
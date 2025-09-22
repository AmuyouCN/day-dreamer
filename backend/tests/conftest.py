"""
Pytest配置文件

定义测试环境和夹具
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from tortoise.contrib.test import initializer, finalizer
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    """初始化测试环境"""
    # 使用内存数据库进行测试
    initializer(["app.models"], db_url="sqlite://:memory:")
    yield
    finalizer()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP客户端夹具"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers() -> dict:
    """认证头夹具"""
    # 这里简化处理，实际测试中需要先登录获取Token
    return {"Authorization": "Bearer test-token"}
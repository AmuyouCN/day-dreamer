"""
用户管理API测试

测试用户CRUD操作功能
"""

import pytest
from httpx import AsyncClient
from app.models.user import User


class TestUsers:
    """用户管理接口测试类"""
    
    async def test_get_users_without_auth(self, client: AsyncClient):
        """测试未认证获取用户列表"""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401
    
    async def test_create_user_without_auth(self, client: AsyncClient):
        """测试未认证创建用户"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 401
    
    async def test_get_user_without_auth(self, client: AsyncClient):
        """测试未认证获取用户详情"""
        response = await client.get("/api/v1/users/1")
        assert response.status_code == 401
    
    async def test_update_user_without_auth(self, client: AsyncClient):
        """测试未认证更新用户"""
        user_data = {
            "full_name": "Updated Name"
        }
        
        response = await client.put("/api/v1/users/1", json=user_data)
        assert response.status_code == 401
    
    async def test_delete_user_without_auth(self, client: AsyncClient):
        """测试未认证删除用户"""
        response = await client.delete("/api/v1/users/1")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_user_model_creation(self):
        """测试用户模型创建"""
        user = await User.create(
            username="modeltest",
            email="model@example.com",
            full_name="Model Test User",
            is_active=True
        )
        
        # 测试密码设置和验证
        user.set_password("testpassword")
        await user.save()
        
        assert user.verify_password("testpassword")
        assert not user.verify_password("wrongpassword")
        
        # 测试获取权限（空列表）
        permissions = await user.get_permissions()
        assert isinstance(permissions, list)
        assert len(permissions) == 0
"""
认证服务模块

基于Redis的Token认证和用户会话管理
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from loguru import logger

from app.core.redis import get_redis
from app.core.security import create_access_token, create_refresh_token, is_token_expired
from app.core.config import settings
from app.models.user import User
from app.utils.exceptions import AuthenticationError, AuthorizationError


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.redis = get_redis()
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """用户认证"""
        
        # 检查登录失败次数
        await self._check_login_attempts(ip_address or "unknown")
        
        try:
            # 查找用户
            user = await User.get_or_none(username=username, is_active=True)
            if not user or not user.verify_password(password):
                await self._record_login_failure(ip_address or "unknown")
                raise AuthenticationError("用户名或密码错误")
            
            # 获取用户权限
            permissions = await user.get_permissions()
            
            # 创建Token数据
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "permissions": permissions,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            # 生成访问Token
            token_info = create_access_token(user_data)
            access_token = token_info["access_token"]
            token_data = token_info["token_data"]
            
            # 生成刷新Token
            refresh_token = create_refresh_token(user.id)
            
            # 存储Token到Redis
            await self._store_access_token(access_token, token_data)
            await self._store_refresh_token(refresh_token, user.id)
            await self._add_user_token(user.id, access_token)
            
            # 更新用户最后登录时间
            user.last_login = datetime.utcnow()
            await user.save(update_fields=["last_login"])
            
            # 清除登录失败记录
            await self._clear_login_failures(ip_address or "unknown")
            
            logger.info(f"用户登录成功: {username} (ID: {user.id})")
            
            return {
                \"access_token\": access_token,
                \"refresh_token\": refresh_token,
                \"token_type\": \"bearer\",
                \"expires_in\": settings.access_token_expire_hours * 3600,
                \"user_info\": {
                    \"id\": user.id,
                    \"username\": user.username,
                    \"full_name\": user.full_name,
                    \"email\": user.email
                }
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f\"认证过程发生错误: {e}\")
            raise AuthenticationError(\"认证失败\")
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        \"\"\"验证Token\"\"\"
        try:
            # 从Redis获取Token数据
            token_key = f\"token:access:{token}\"
            token_data_str = await self.redis.get(token_key)
            
            if not token_data_str:
                return None
            
            token_data = json.loads(token_data_str)
            
            # 检查Token是否过期
            if is_token_expired(token_data.get(\"expire_time\")):
                await self._remove_token(token)
                return None
            
            return token_data
            
        except Exception as e:
            logger.error(f\"Token验证错误: {e}\")
            return None
    
    async def logout_user(self, user_id: int, token: str = None) -> bool:
        \"\"\"用户登出\"\"\"
        try:
            if token:
                # 删除指定Token
                await self._remove_token(token)
                await self._remove_user_token(user_id, token)
            else:
                # 删除用户所有Token
                await self._remove_all_user_tokens(user_id)
            
            logger.info(f\"用户登出成功: ID={user_id}\")
            return True
            
        except Exception as e:
            logger.error(f\"登出过程发生错误: {e}\")
            return False
    
    async def refresh_user_token(self, refresh_token: str) -> Dict[str, Any]:
        \"\"\"刷新用户Token\"\"\"
        try:
            # 验证刷新Token
            refresh_key = f\"token:refresh:{refresh_token}\"
            user_id_str = await self.redis.get(refresh_key)
            
            if not user_id_str:
                raise AuthenticationError(\"无效的刷新Token\")
            
            user_id = int(user_id_str)
            
            # 获取用户信息
            user = await User.get_or_none(id=user_id, is_active=True)
            if not user:
                raise AuthenticationError(\"用户不存在或已禁用\")
            
            # 获取用户权限
            permissions = await user.get_permissions()
            
            # 创建新的访问Token
            user_data = {
                \"user_id\": user.id,
                \"username\": user.username,
                \"permissions\": permissions
            }
            
            token_info = create_access_token(user_data)
            new_access_token = token_info[\"access_token\"]
            token_data = token_info[\"token_data\"]
            
            # 存储新Token
            await self._store_access_token(new_access_token, token_data)
            await self._add_user_token(user.id, new_access_token)
            
            # 延长刷新Token有效期
            await self.redis.expire(
                refresh_key, 
                settings.refresh_token_expire_days * 24 * 3600
            )
            
            return {
                \"access_token\": new_access_token,
                \"token_type\": \"bearer\",
                \"expires_in\": settings.access_token_expire_hours * 3600
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f\"Token刷新错误: {e}\")
            raise AuthenticationError(\"Token刷新失败\")
    
    async def get_user_by_token(self, token: str) -> Optional[User]:
        \"\"\"通过Token获取用户\"\"\"
        token_data = await self.verify_token(token)
        if not token_data:
            return None
        
        user_id = token_data.get(\"user_id\")
        if not user_id:
            return None
        
        return await User.get_or_none(id=user_id, is_active=True)
    
    async def check_permission(self, token: str, permission: str) -> bool:
        \"\"\"检查权限\"\"\"
        token_data = await self.verify_token(token)
        if not token_data:
            return False
        
        permissions = token_data.get(\"permissions\", [])
        return permission in permissions
    
    # 私有方法
    
    async def _store_access_token(self, token: str, token_data: Dict[str, Any]):
        \"\"\"存储访问Token\"\"\"
        token_key = f\"token:access:{token}\"
        expire_seconds = settings.access_token_expire_hours * 3600
        
        await self.redis.setex(
            token_key,
            expire_seconds,
            json.dumps(token_data, ensure_ascii=False)
        )
    
    async def _store_refresh_token(self, refresh_token: str, user_id: int):
        \"\"\"存储刷新Token\"\"\"
        refresh_key = f\"token:refresh:{refresh_token}\"
        expire_seconds = settings.refresh_token_expire_days * 24 * 3600
        
        await self.redis.setex(refresh_key, expire_seconds, str(user_id))
    
    async def _add_user_token(self, user_id: int, token: str):
        \"\"\"添加用户Token到列表\"\"\"
        user_tokens_key = f\"user:tokens:{user_id}\"
        expire_seconds = settings.access_token_expire_hours * 3600
        
        await self.redis.sadd(user_tokens_key, token)
        await self.redis.expire(user_tokens_key, expire_seconds)
    
    async def _remove_token(self, token: str):
        \"\"\"删除Token\"\"\"
        token_key = f\"token:access:{token}\"
        await self.redis.delete(token_key)
    
    async def _remove_user_token(self, user_id: int, token: str):
        \"\"\"从用户Token列表中删除Token\"\"\"
        user_tokens_key = f\"user:tokens:{user_id}\"
        await self.redis.srem(user_tokens_key, token)
    
    async def _remove_all_user_tokens(self, user_id: int):
        \"\"\"删除用户所有Token\"\"\"
        user_tokens_key = f\"user:tokens:{user_id}\"
        
        # 获取所有Token
        tokens = await self.redis.smembers(user_tokens_key)
        
        # 删除所有访问Token
        for token in tokens:
            await self._remove_token(token)
        
        # 删除用户Token列表
        await self.redis.delete(user_tokens_key)
    
    async def _check_login_attempts(self, ip_address: str):
        \"\"\"检查登录失败次数\"\"\"
        attempts_key = f\"login:attempts:{ip_address}\"
        attempts = await self.redis.get(attempts_key)
        
        if attempts and int(attempts) >= 5:
            raise AuthenticationError(\"登录失败次数过多，请30分钟后再试\")
    
    async def _record_login_failure(self, ip_address: str):
        \"\"\"记录登录失败\"\"\"
        attempts_key = f\"login:attempts:{ip_address}\"
        
        await self.redis.incr(attempts_key)
        await self.redis.expire(attempts_key, 1800)  # 30分钟过期
    
    async def _clear_login_failures(self, ip_address: str):
        \"\"\"清除登录失败记录\"\"\"
        attempts_key = f\"login:attempts:{ip_address}\"
        await self.redis.delete(attempts_key)"
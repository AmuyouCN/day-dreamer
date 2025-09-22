"""
安全相关工具模块

包含密码加密、Token生成和验证等安全功能
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def generate_token() -> str:
    """生成安全的随机Token"""
    return secrets.token_urlsafe(32)


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def create_access_token(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建访问Token"""
    token = generate_token()
    expire_time = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    token_data = {
        "token": token,
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "permissions": user_data.get("permissions", []),
        "login_time": datetime.utcnow().isoformat(),
        "expire_time": expire_time.isoformat(),
        "ip_address": user_data.get("ip_address"),
        "user_agent": user_data.get("user_agent")
    }
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "token_data": token_data
    }


def create_refresh_token(user_id: int) -> str:
    """创建刷新Token"""
    return generate_token()


def is_token_expired(expire_time: str) -> bool:
    """检查Token是否过期"""
    try:
        expire_dt = datetime.fromisoformat(expire_time)
        return datetime.utcnow() > expire_dt
    except (ValueError, TypeError):
        return True
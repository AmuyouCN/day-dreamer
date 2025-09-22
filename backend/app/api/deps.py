"""
API依赖注入模块

定义通用的依赖注入函数，包括认证、权限验证等
"""

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.exceptions import AuthenticationError, AuthorizationError

# OAuth2Bearer实例
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """获取当前用户"""
    
    token = credentials.credentials
    auth_service = AuthService()
    
    # 验证Token
    user = await auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """获取当前激活用户"""
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return current_user


def require_permission(permission: str):
    """权限验证装饰器"""
    
    async def permission_checker(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ) -> None:
        
        token = credentials.credentials
        auth_service = AuthService()
        
        # 检查权限
        has_permission = await auth_service.check_permission(token, permission)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {permission} 权限"
            )
    
    return Depends(permission_checker)


def require_permissions(*permissions: str):
    \"\"\"多权限验证装饰器\"\"\"
    
    async def permissions_checker(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ) -> None:
        
        token = credentials.credentials
        auth_service = AuthService()
        
        # 检查所有权限
        for permission in permissions:
            has_permission = await auth_service.check_permission(token, permission)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f\"权限不足：需要 {permission} 权限\"
                )
    
    return Depends(permissions_checker)


def require_any_permission(*permissions: str):
    \"\"\"任一权限验证装饰器\"\"\"
    
    async def any_permission_checker(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ) -> None:
        
        token = credentials.credentials
        auth_service = AuthService()
        
        # 检查是否有任一权限
        for permission in permissions:
            has_permission = await auth_service.check_permission(token, permission)
            if has_permission:
                return  # 有任一权限即可
        
        # 没有任何权限
        permissions_str = \" 或 \".join(permissions)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f\"权限不足：需要以下权限之一：{permissions_str}\"
        )
    
    return Depends(any_permission_checker)


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    \"\"\"获取可选的当前用户（不抛出异常）\"\"\"
    
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        auth_service = AuthService()
        return await auth_service.get_user_by_token(token)
    except Exception:
        return None


def get_client_ip(request: Request) -> str:
    \"\"\"获取客户端IP地址\"\"\"
    
    # 尝试从各种可能的头部获取真实IP
    x_forwarded_for = request.headers.get(\"X-Forwarded-For\")
    if x_forwarded_for:
        # X-Forwarded-For 可能包含多个IP，取第一个
        return x_forwarded_for.split(\",\")[0].strip()
    
    x_real_ip = request.headers.get(\"X-Real-IP\")
    if x_real_ip:
        return x_real_ip
    
    # 如果没有代理头，使用直接连接的IP
    if hasattr(request, \"client\") and request.client:
        return request.client.host
    
    return \"unknown\"


def get_user_agent(request: Request) -> str:
    \"\"\"获取用户代理\"\"\"
    return request.headers.get(\"User-Agent\", \"unknown\")"
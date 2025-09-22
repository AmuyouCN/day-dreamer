"""
认证相关API路由

提供用户登录、登出、Token刷新等认证功能
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import TokenResponse, RefreshTokenRequest, RefreshTokenResponse, MessageResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from app.models.user import User
from app.utils.response import success_response
from app.utils.exceptions import AuthenticationError

router = APIRouter()


@router.post(\"/login\", response_model=dict, summary=\"用户登录\")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    \"\"\"用户登录获取Token\"\"\"
    
    auth_service = AuthService()
    
    try:
        # 获取客户端信息
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # 执行用户认证
        token_data = await auth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return success_response(data=token_data, message=\"登录成功\")
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={\"WWW-Authenticate\": \"Bearer\"},
        )


@router.post(\"/logout\", response_model=dict, summary=\"用户登出\")
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    \"\"\"用户登出清除Token\"\"\"
    
    auth_service = AuthService()
    
    # 从请求头获取Token
    authorization = request.headers.get(\"Authorization\")
    token = None
    if authorization and authorization.startswith(\"Bearer \"):
        token = authorization[7:]
    
    # 执行登出
    success = await auth_service.logout_user(current_user.id, token)
    
    if success:
        return success_response(message=\"登出成功\")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"登出失败\"
        )


@router.get(\"/me\", response_model=dict, summary=\"获取当前用户信息\")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    \"\"\"获取当前登录用户的详细信息\"\"\"
    
    # 构建用户信息
    user_data = {
        \"id\": current_user.id,
        \"username\": current_user.username,
        \"email\": current_user.email,
        \"full_name\": current_user.full_name,
        \"is_active\": current_user.is_active,
        \"created_at\": current_user.created_at.isoformat(),
        \"updated_at\": current_user.updated_at.isoformat(),
        \"last_login\": current_user.last_login.isoformat() if current_user.last_login else None
    }
    
    # 获取用户权限
    permissions = await current_user.get_permissions()
    user_data[\"permissions\"] = permissions
    
    return success_response(data=user_data, message=\"获取用户信息成功\")


@router.post(\"/refresh\", response_model=dict, summary=\"刷新Token\")
async def refresh_token(
    refresh_data: RefreshTokenRequest
):
    \"\"\"使用刷新Token获取新的访问Token\"\"\"
    
    auth_service = AuthService()
    
    try:
        new_token_data = await auth_service.refresh_user_token(
            refresh_data.refresh_token
        )
        
        return success_response(data=new_token_data, message=\"Token刷新成功\")
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={\"WWW-Authenticate\": \"Bearer\"},
        )


@router.post(\"/change-password\", response_model=dict, summary=\"修改密码\")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    password_data: dict  # 简化的密码数据
):
    \"\"\"修改当前用户密码\"\"\"
    
    current_password = password_data.get(\"current_password\")
    new_password = password_data.get(\"new_password\")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=\"当前密码和新密码都不能为空\"
        )
    
    # 验证当前密码
    if not current_user.verify_password(current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=\"当前密码错误\"
        )
    
    # 设置新密码
    current_user.set_password(new_password)
    await current_user.save(update_fields=[\"password_hash\"])
    
    # 登出用户所有会话（强制重新登录）
    auth_service = AuthService()
    await auth_service.logout_user(current_user.id)
    
    return success_response(message=\"密码修改成功，请重新登录\")"
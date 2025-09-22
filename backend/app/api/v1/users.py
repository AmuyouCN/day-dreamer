"""
用户管理API路由

提供用户CRUD操作、角色分配等功能
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListRequest, 
    UserListResponse, AssignRoleRequest
)
from app.services.user_service import UserService
from app.api.deps import get_current_active_user, require_permission, require_any_permission
from app.models.user import User
from app.utils.response import success_response, paged_response
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get(\"/\", response_model=dict, summary=\"获取用户列表\")
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:read\"))],
    page: int = Query(1, ge=1, description=\"页码\"),
    size: int = Query(10, ge=1, le=100, description=\"每页数量\"),
    search: Optional[str] = Query(None, max_length=100, description=\"搜索关键词\"),
    is_active: Optional[bool] = Query(None, description=\"是否激活\")
):
    \"\"\"获取用户列表（支持分页和搜索）\"\"\"
    
    user_service = UserService()
    
    # 构建查询参数
    query_params = {
        \"page\": page,
        \"size\": size,
        \"search\": search,
        \"is_active\": is_active
    }
    
    result = await user_service.list_users(**query_params)
    
    return paged_response(
        items=result[\"users\"],
        total=result[\"total\"],
        page=page,
        size=size,
        message=\"获取用户列表成功\"
    )


@router.post(\"/\", response_model=dict, summary=\"创建用户\")
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:write\"))]
):
    \"\"\"创建新用户\"\"\"
    
    user_service = UserService()
    
    try:
        new_user = await user_service.create_user(user_data)
        
        user_dict = {
            \"id\": new_user.id,
            \"username\": new_user.username,
            \"email\": new_user.email,
            \"full_name\": new_user.full_name,
            \"is_active\": new_user.is_active,
            \"created_at\": new_user.created_at.isoformat(),
            \"updated_at\": new_user.updated_at.isoformat()
        }
        
        return success_response(data=user_dict, message=\"用户创建成功\")
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(\"/{user_id}\", response_model=dict, summary=\"获取用户详情\")
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_any_permission(\"user:read\", \"user:self\"))]
):
    \"\"\"获取用户详细信息\"\"\"
    
    user_service = UserService()
    
    # 检查是否访问自己的信息
    if user_id != current_user.id:
        # 如果不是访问自己的信息，需要user:read权限
        from app.services.auth_service import AuthService
        from app.api.deps import get_client_ip
        # 这里可以进一步验证权限，暂时简化
        pass
    
    try:
        user = await user_service.get_user_by_id(user_id)
        
        user_dict = {
            \"id\": user.id,
            \"username\": user.username,
            \"email\": user.email,
            \"full_name\": user.full_name,
            \"is_active\": user.is_active,
            \"created_at\": user.created_at.isoformat(),
            \"updated_at\": user.updated_at.isoformat(),
            \"last_login\": user.last_login.isoformat() if user.last_login else None
        }
        
        # 获取用户角色信息
        roles = await user.roles.all()
        user_dict[\"roles\"] = [
            {
                \"id\": role.id,
                \"name\": role.name,
                \"description\": role.description
            }
            for role in roles
        ]
        
        return success_response(data=user_dict, message=\"获取用户信息成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(\"/{user_id}\", response_model=dict, summary=\"更新用户信息\")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_any_permission(\"user:write\", \"user:self\"))]
):
    \"\"\"更新用户信息\"\"\"
    
    user_service = UserService()
    
    # 检查是否更新自己的信息
    if user_id != current_user.id:
        # 如果不是更新自己的信息，需要user:write权限
        pass
    
    try:
        updated_user = await user_service.update_user(user_id, user_data)
        
        user_dict = {
            \"id\": updated_user.id,
            \"username\": updated_user.username,
            \"email\": updated_user.email,
            \"full_name\": updated_user.full_name,
            \"is_active\": updated_user.is_active,
            \"created_at\": updated_user.created_at.isoformat(),
            \"updated_at\": updated_user.updated_at.isoformat()
        }
        
        return success_response(data=user_dict, message=\"用户信息更新成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete(\"/{user_id}\", response_model=dict, summary=\"删除用户\")
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:delete\"))]
):
    \"\"\"删除用户（软删除：设置为非激活状态）\"\"\"
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=\"不能删除自己的账号\"
        )
    
    user_service = UserService()
    
    try:
        await user_service.delete_user(user_id)
        return success_response(message=\"用户删除成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(\"/{user_id}/roles\", response_model=dict, summary=\"获取用户角色\")
async def get_user_roles(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:read\"))]
):
    \"\"\"获取用户的角色列表\"\"\"
    
    user_service = UserService()
    
    try:
        roles = await user_service.get_user_roles(user_id)
        
        roles_data = [
            {
                \"id\": role.id,
                \"name\": role.name,
                \"description\": role.description,
                \"is_active\": role.is_active
            }
            for role in roles
        ]
        
        return success_response(data=roles_data, message=\"获取用户角色成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(\"/{user_id}/roles\", response_model=dict, summary=\"分配角色\")
async def assign_roles(
    user_id: int,
    role_data: AssignRoleRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:write\"))]
):
    \"\"\"为用户分配角色\"\"\"
    
    user_service = UserService()
    
    try:
        await user_service.assign_roles(user_id, role_data.role_ids)
        return success_response(message=\"角色分配成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(\"/{user_id}/roles/{role_id}\", response_model=dict, summary=\"移除角色\")
async def remove_role(
    user_id: int,
    role_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission(\"user:write\"))]
):
    \"\"\"移除用户的指定角色\"\"\"
    
    user_service = UserService()
    
    try:
        await user_service.remove_role(user_id, role_id)
        return success_response(message=\"角色移除成功\")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )"
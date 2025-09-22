"""
环境管理API路由

提供环境配置的CRUD操作
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.environment import (
    EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse,
    EnvironmentListRequest
)
from app.services.environment_service import EnvironmentService
from app.api.deps import get_current_active_user, require_permission
from app.models.user import User
from app.utils.response import success_response, paged_response
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get("/", response_model=dict, summary="获取环境列表")
async def list_environments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活过滤")
):
    """获取环境列表（支持分页和搜索）"""
    
    environment_service = EnvironmentService()
    
    result = await environment_service.list_environments(
        page=page,
        size=size,
        search=search,
        is_active=is_active
    )
    
    return paged_response(
        items=result["environments"],
        total=result["total"],
        page=page,
        size=size,
        message="获取环境列表成功"
    )


@router.post("/", response_model=dict, summary="创建环境")
async def create_environment(
    env_data: EnvironmentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("system:admin"))]
):
    """创建新环境（需要管理员权限）"""
    
    environment_service = EnvironmentService()
    
    try:
        new_env = await environment_service.create_environment(env_data)
        
        env_dict = {
            "id": new_env.id,
            "name": new_env.name,
            "description": new_env.description,
            "config": new_env.config,
            "is_active": new_env.is_active,
            "created_at": new_env.created_at.isoformat(),
            "updated_at": new_env.updated_at.isoformat()
        }
        
        return success_response(data=env_dict, message="环境创建成功")
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"环境创建失败: {str(e)}"
        )


@router.get("/{env_id}", response_model=dict, summary="获取环境详情")
async def get_environment(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """获取环境详细信息"""
    
    environment_service = EnvironmentService()
    
    try:
        environment = await environment_service.get_environment_by_id(env_id)
        
        env_dict = {
            "id": environment.id,
            "name": environment.name,
            "description": environment.description,
            "config": environment.config,
            "is_active": environment.is_active,
            "created_at": environment.created_at.isoformat(),
            "updated_at": environment.updated_at.isoformat()
        }
        
        # 获取环境变量
        variables = await environment_service.get_environment_variables(env_id)
        env_dict["variables"] = variables
        
        return success_response(data=env_dict, message="获取环境信息成功")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{env_id}", response_model=dict, summary="更新环境")
async def update_environment(
    env_id: int,
    env_data: EnvironmentUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("system:admin"))]
):
    """更新环境配置（需要管理员权限）"""
    
    environment_service = EnvironmentService()
    
    try:
        updated_env = await environment_service.update_environment(env_id, env_data)
        
        env_dict = {
            "id": updated_env.id,
            "name": updated_env.name,
            "description": updated_env.description,
            "config": updated_env.config,
            "is_active": updated_env.is_active,
            "created_at": updated_env.created_at.isoformat(),
            "updated_at": updated_env.updated_at.isoformat()
        }
        
        return success_response(data=env_dict, message="环境更新成功")
        
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


@router.delete("/{env_id}", response_model=dict, summary="删除环境")
async def delete_environment(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("system:admin"))]
):
    """删除环境（需要管理员权限）"""
    
    environment_service = EnvironmentService()
    
    try:
        await environment_service.delete_environment(env_id)
        return success_response(message="环境删除成功")
        
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


@router.post("/{env_id}/test", response_model=dict, summary="测试环境连通性")
async def test_environment_connectivity(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """测试环境连通性"""
    
    environment_service = EnvironmentService()
    
    try:
        result = await environment_service.test_environment_connectivity(env_id)
        return success_response(data=result, message="环境连通性测试完成")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{env_id}/copy", response_model=dict, summary="复制环境")
async def copy_environment(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("system:admin"))],
    new_name: str = Query(..., description="新环境名称")
):
    """复制环境（需要管理员权限）"""
    
    environment_service = EnvironmentService()
    
    try:
        copied_env = await environment_service.copy_environment(env_id, new_name)
        
        env_dict = {
            "id": copied_env.id,
            "name": copied_env.name,
            "description": copied_env.description,
            "config": copied_env.config,
            "is_active": copied_env.is_active,
            "created_at": copied_env.created_at.isoformat(),
            "updated_at": copied_env.updated_at.isoformat()
        }
        
        return success_response(data=env_dict, message="环境复制成功")
        
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
"""
接口管理API路由

提供接口定义的CRUD操作和测试功能
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.api import (
    ApiDefinitionCreate, ApiDefinitionUpdate, ApiDefinitionResponse,
    TestApiRequest, TestApiResponse, ApiListRequest
)
from app.services.api_service import ApiService
from app.api.deps import get_current_active_user, require_permission, require_any_permission
from app.models.user import User
from app.utils.response import success_response, paged_response
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get("/", response_model=dict, summary="获取接口列表")
async def list_apis(
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("api:read"))],
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
    method: Optional[str] = Query(None, description="HTTP方法过滤"),
    is_public: Optional[bool] = Query(None, description="是否公开过滤")
):
    """获取接口列表（支持分页和搜索）"""
    
    api_service = ApiService()
    
    result = await api_service.list_apis(
        user_id=current_user.id,
        page=page,
        size=size,
        search=search,
        method=method,
        is_public=is_public
    )
    
    return paged_response(
        items=result["apis"],
        total=result["total"],
        page=page,
        size=size,
        message="获取接口列表成功"
    )


@router.post("/", response_model=dict, summary="创建接口")
async def create_api(
    api_data: ApiDefinitionCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("api:write"))]
):
    """创建新的接口定义"""
    
    api_service = ApiService()
    
    try:
        new_api = await api_service.create_api(api_data, current_user.id)
        
        api_dict = {
            "id": new_api.id,
            "name": new_api.name,
            "description": new_api.description,
            "method": new_api.method,
            "url": new_api.url,
            "headers": new_api.headers,
            "query_params": new_api.query_params,
            "body_schema": new_api.body_schema,
            "response_schema": new_api.response_schema,
            "creator_id": new_api.creator_id,
            "is_public": new_api.is_public,
            "created_at": new_api.created_at.isoformat(),
            "updated_at": new_api.updated_at.isoformat()
        }
        
        return success_response(data=api_dict, message="接口创建成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"接口创建失败: {str(e)}"
        )


@router.get("/{api_id}", response_model=dict, summary="获取接口详情")
async def get_api(
    api_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("api:read"))]
):
    """获取接口详细信息"""
    
    api_service = ApiService()
    
    try:
        api = await api_service.get_api_by_id(api_id, current_user.id)
        
        api_dict = {
            "id": api.id,
            "name": api.name,
            "description": api.description,
            "method": api.method,
            "url": api.url,
            "headers": api.headers,
            "query_params": api.query_params,
            "body_schema": api.body_schema,
            "response_schema": api.response_schema,
            "creator_id": api.creator_id,
            "is_public": api.is_public,
            "created_at": api.created_at.isoformat(),
            "updated_at": api.updated_at.isoformat()
        }
        
        # 获取测试用例数量
        test_case_count = await api.get_test_case_count()
        api_dict["test_case_count"] = test_case_count
        
        return success_response(data=api_dict, message="获取接口信息成功")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{api_id}", response_model=dict, summary="更新接口")
async def update_api(
    api_id: int,
    api_data: ApiDefinitionUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("api:write"))]
):
    """更新接口定义"""
    
    api_service = ApiService()
    
    try:
        updated_api = await api_service.update_api(api_id, api_data, current_user.id)
        
        api_dict = {
            "id": updated_api.id,
            "name": updated_api.name,
            "description": updated_api.description,
            "method": updated_api.method,
            "url": updated_api.url,
            "headers": updated_api.headers,
            "query_params": updated_api.query_params,
            "body_schema": updated_api.body_schema,
            "response_schema": updated_api.response_schema,
            "creator_id": updated_api.creator_id,
            "is_public": updated_api.is_public,
            "created_at": updated_api.created_at.isoformat(),
            "updated_at": updated_api.updated_at.isoformat()
        }
        
        return success_response(data=api_dict, message="接口更新成功")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{api_id}", response_model=dict, summary="删除接口")
async def delete_api(
    api_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_any_permission("api:delete", "api:write"))]
):
    """删除接口定义"""
    
    api_service = ApiService()
    
    try:
        await api_service.delete_api(api_id, current_user.id)
        return success_response(message="接口删除成功")
        
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


@router.post("/{api_id}/test", response_model=dict, summary="测试接口")
async def test_api(
    api_id: int,
    test_data: TestApiRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:execute"))]
):
    """执行接口测试"""
    
    api_service = ApiService()
    
    try:
        result = await api_service.test_api(api_id, test_data, current_user.id)
        return success_response(data=result, message="接口测试完成")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"接口测试失败: {str(e)}"
        )


@router.get("/{api_id}/test-cases", response_model=dict, summary="获取接口的测试用例")
async def get_api_test_cases(
    api_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:read"))],
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """获取指定接口的测试用例列表"""
    
    from app.services.test_case_service import TestCaseService
    
    # 先检查接口是否存在
    api_service = ApiService()
    try:
        await api_service.get_api_by_id(api_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # 获取测试用例列表
    test_case_service = TestCaseService()
    result = await test_case_service.list_test_cases(
        user_id=current_user.id,
        page=page,
        size=size,
        api_id=api_id,
        is_active=True
    )
    
    return paged_response(
        items=result["test_cases"],
        total=result["total"],
        page=page,
        size=size,
        message="获取接口测试用例成功"
    )


@router.get("/statistics/overview", response_model=dict, summary="获取接口统计概览")
async def get_api_statistics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("api:read"))]
):
    """获取用户的接口统计信息"""
    
    api_service = ApiService()
    
    try:
        stats = await api_service.get_api_statistics(current_user.id)
        return success_response(data=stats, message="获取接口统计成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
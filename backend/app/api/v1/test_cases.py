"""
测试用例API路由

提供测试用例的CRUD操作和执行功能
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    RunTestCaseRequest, TestCaseExecutionResult,
    CopyTestCaseRequest, BatchExecutionRequest
)
from app.services.test_case_service import TestCaseService
from app.api.deps import get_current_active_user, require_permission
from app.models.user import User
from app.utils.response import success_response, paged_response
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get("/", response_model=dict, summary="获取测试用例列表")
async def list_test_cases(
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:read"))],
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
    api_id: Optional[int] = Query(None, description="接口ID过滤"),
    is_active: Optional[bool] = Query(None, description="是否激活过滤")
):
    """获取测试用例列表（支持分页和搜索）"""
    
    test_case_service = TestCaseService()
    
    result = await test_case_service.list_test_cases(
        user_id=current_user.id,
        page=page,
        size=size,
        search=search,
        api_id=api_id,
        is_active=is_active
    )
    
    return paged_response(
        items=result["test_cases"],
        total=result["total"],
        page=page,
        size=size,
        message="获取测试用例列表成功"
    )


@router.post("/", response_model=dict, summary="创建测试用例")
async def create_test_case(
    test_case_data: TestCaseCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:manage"))]
):
    """创建新的测试用例"""
    
    test_case_service = TestCaseService()
    
    try:
        new_test_case = await test_case_service.create_test_case(test_case_data, current_user.id)
        
        test_case_dict = {
            "id": new_test_case.id,
            "name": new_test_case.name,
            "description": new_test_case.description,
            "api_id": new_test_case.api_id,
            "request_data": new_test_case.request_data,
            "expected_response": new_test_case.expected_response,
            "assertions": new_test_case.assertions,
            "creator_id": new_test_case.creator_id,
            "is_active": new_test_case.is_active,
            "created_at": new_test_case.created_at.isoformat(),
            "updated_at": new_test_case.updated_at.isoformat()
        }
        
        return success_response(data=test_case_dict, message="测试用例创建成功")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试用例创建失败: {str(e)}"
        )


@router.get("/{test_case_id}", response_model=dict, summary="获取测试用例详情")
async def get_test_case(
    test_case_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:read"))]
):
    """获取测试用例详细信息"""
    
    test_case_service = TestCaseService()
    
    try:
        test_case = await test_case_service.get_test_case_by_id(test_case_id, current_user.id)
        
        test_case_dict = {
            "id": test_case.id,
            "name": test_case.name,
            "description": test_case.description,
            "api_id": test_case.api_id,
            "request_data": test_case.request_data,
            "expected_response": test_case.expected_response,
            "assertions": test_case.assertions,
            "creator_id": test_case.creator_id,
            "is_active": test_case.is_active,
            "created_at": test_case.created_at.isoformat(),
            "updated_at": test_case.updated_at.isoformat()
        }
        
        # 获取统计信息
        execution_count = await test_case.get_execution_count()
        success_rate = await test_case.get_success_rate()
        
        test_case_dict["execution_count"] = execution_count
        test_case_dict["success_rate"] = success_rate
        
        return success_response(data=test_case_dict, message="获取测试用例信息成功")
        
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


@router.put("/{test_case_id}", response_model=dict, summary="更新测试用例")
async def update_test_case(
    test_case_id: int,
    test_case_data: TestCaseUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:manage"))]
):
    """更新测试用例"""
    
    test_case_service = TestCaseService()
    
    try:
        updated_test_case = await test_case_service.update_test_case(
            test_case_id, test_case_data, current_user.id
        )
        
        test_case_dict = {
            "id": updated_test_case.id,
            "name": updated_test_case.name,
            "description": updated_test_case.description,
            "api_id": updated_test_case.api_id,
            "request_data": updated_test_case.request_data,
            "expected_response": updated_test_case.expected_response,
            "assertions": updated_test_case.assertions,
            "creator_id": updated_test_case.creator_id,
            "is_active": updated_test_case.is_active,
            "created_at": updated_test_case.created_at.isoformat(),
            "updated_at": updated_test_case.updated_at.isoformat()
        }
        
        return success_response(data=test_case_dict, message="测试用例更新成功")
        
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


@router.delete("/{test_case_id}", response_model=dict, summary="删除测试用例")
async def delete_test_case(
    test_case_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:manage"))]
):
    """删除测试用例（软删除）"""
    
    test_case_service = TestCaseService()
    
    try:
        await test_case_service.delete_test_case(test_case_id, current_user.id)
        return success_response(message="测试用例删除成功")
        
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


@router.post("/{test_case_id}/run", response_model=dict, summary="执行测试用例")
async def run_test_case(
    test_case_id: int,
    run_data: RunTestCaseRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:execute"))]
):
    """执行单个测试用例"""
    
    test_case_service = TestCaseService()
    
    try:
        result = await test_case_service.run_test_case(test_case_id, run_data, current_user.id)
        
        result_dict = {
            "test_case_id": result.test_case_id,
            "status": result.status,
            "duration": result.duration,
            "request_data": result.request_data,
            "response_data": result.response_data,
            "assertion_results": result.assertion_results,
            "error_message": result.error_message
        }
        
        return success_response(data=result_dict, message="测试用例执行完成")
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试用例执行失败: {str(e)}"
        )


@router.post("/{test_case_id}/copy", response_model=dict, summary="复制测试用例")
async def copy_test_case(
    test_case_id: int,
    copy_data: CopyTestCaseRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:manage"))]
):
    """复制测试用例"""
    
    test_case_service = TestCaseService()
    
    try:
        copied_test_case = await test_case_service.copy_test_case(
            test_case_id=test_case_id,
            new_name=copy_data.new_name,
            user_id=current_user.id,
            copy_to_api_id=copy_data.copy_to_api_id
        )
        
        test_case_dict = {
            "id": copied_test_case.id,
            "name": copied_test_case.name,
            "description": copied_test_case.description,
            "api_id": copied_test_case.api_id,
            "request_data": copied_test_case.request_data,
            "expected_response": copied_test_case.expected_response,
            "assertions": copied_test_case.assertions,
            "creator_id": copied_test_case.creator_id,
            "is_active": copied_test_case.is_active,
            "created_at": copied_test_case.created_at.isoformat(),
            "updated_at": copied_test_case.updated_at.isoformat()
        }
        
        return success_response(data=test_case_dict, message="测试用例复制成功")
        
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


@router.post("/batch/run", response_model=dict, summary="批量执行测试用例")
async def batch_run_test_cases(
    batch_data: BatchExecutionRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:execute"))]
):
    """批量执行测试用例"""
    
    # 这里暂时返回简单响应，实际实现需要异步任务支持
    return success_response(
        data={
            "execution_id": "batch_123",
            "test_case_ids": batch_data.test_case_ids,
            "status": "started",
            "message": "批量测试已开始，请查看执行历史获取结果"
        },
        message="批量测试已启动"
    )


@router.get("/statistics/overview", response_model=dict, summary="获取测试用例统计概览")
async def get_test_case_statistics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    _: Annotated[None, Depends(require_permission("test:read"))]
):
    """获取用户的测试用例统计信息"""
    
    test_case_service = TestCaseService()
    
    try:
        stats = await test_case_service.get_test_case_statistics(current_user.id)
        return success_response(data=stats, message="获取测试用例统计成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
"""
变量管理API路由

提供变量的CRUD操作接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional, List

from app.models.variable import (
    Variable, VariableCreate, VariableUpdate, VariableResponse,
    VariableQuery, VariableBatch, VariableExport, VariableScope
)
from app.models.user import User
from app.services.variable_service import VariableService
from app.utils.auth import get_current_user
from app.utils.response import success_response, error_response
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=dict)
async def create_variable(
    variable_data: VariableCreate,
    current_user: User = Depends(get_current_user)
):
    """创建变量"""
    try:
        # 权限检查：环境变量需要管理员权限，个人变量只能创建自己的
        if variable_data.scope == VariableScope.GLOBAL and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="只有管理员可以创建全局变量")
        
        if variable_data.scope == VariableScope.PERSONAL:
            variable_data.user_id = current_user.id
        
        variable = await VariableService.create_variable(
            name=variable_data.name,
            value=variable_data.value,
            scope=variable_data.scope,
            created_by=current_user.id,
            type=variable_data.type,
            description=variable_data.description,
            environment_id=variable_data.environment_id,
            user_id=variable_data.user_id,
            session_id=variable_data.session_id,
            is_sensitive=variable_data.is_sensitive
        )
        
        # 转换为响应模型
        response_data = VariableResponse(
            id=variable.id,
            name=variable.name,
            value=variable.value,
            type=variable.type,
            scope=variable.scope,
            description=variable.description,
            environment_id=variable.environment_id,
            user_id=variable.user_id,
            session_id=variable.session_id,
            created_by=variable.created_by,
            created_at=variable.created_at.isoformat(),
            updated_at=variable.updated_at.isoformat(),
            is_active=variable.is_active,
            is_sensitive=variable.is_sensitive,
            display_value=variable.display_value
        )
        
        return success_response(response_data, "变量创建成功")
        
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        logger.error(f"创建变量失败: {str(e)}")
        return error_response("变量创建失败")


@router.get("/", response_model=dict)
async def list_variables(
    scope: Optional[VariableScope] = Query(None, description="变量作用域"),
    environment_id: Optional[int] = Query(None, description="环境ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    session_id: Optional[str] = Query(None, description="会话ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user)
):
    """获取变量列表"""
    try:
        # 权限过滤：普通用户只能查看自己的个人变量
        if not current_user.is_admin:
            if scope == VariableScope.PERSONAL:
                user_id = current_user.id
            elif scope == VariableScope.GLOBAL:
                # 普通用户可以查看全局变量
                pass
            else:
                # 其他作用域需要管理员权限
                if scope in [VariableScope.ENVIRONMENT, VariableScope.TEMPORARY]:
                    raise HTTPException(status_code=403, detail="权限不足")
        
        offset = (page - 1) * page_size
        variables, total = await VariableService.list_variables(
            scope=scope,
            environment_id=environment_id,
            user_id=user_id,
            session_id=session_id,
            keyword=keyword,
            offset=offset,
            limit=page_size
        )
        
        # 转换为响应模型
        variable_list = []
        for variable in variables:
            response_data = VariableResponse(
                id=variable.id,
                name=variable.name,
                value=variable.value,
                type=variable.type,
                scope=variable.scope,
                description=variable.description,
                environment_id=variable.environment_id,
                user_id=variable.user_id,
                session_id=variable.session_id,
                created_by=variable.created_by,
                created_at=variable.created_at.isoformat(),
                updated_at=variable.updated_at.isoformat(),
                is_active=variable.is_active,
                is_sensitive=variable.is_sensitive,
                display_value=variable.display_value
            )
            variable_list.append(response_data)
        
        return success_response({
            "variables": variable_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取变量列表失败: {str(e)}")
        return error_response("获取变量列表失败")


@router.get("/{variable_id}", response_model=dict)
async def get_variable(
    variable_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取单个变量"""
    try:
        variable = await VariableService.get_variable(variable_id)
        
        # 权限检查：普通用户只能查看自己的个人变量和全局变量
        if not current_user.is_admin:
            if variable.scope == VariableScope.PERSONAL and variable.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="权限不足")
            elif variable.scope in [VariableScope.ENVIRONMENT, VariableScope.TEMPORARY]:
                raise HTTPException(status_code=403, detail="权限不足")
        
        response_data = VariableResponse(
            id=variable.id,
            name=variable.name,
            value=variable.value,
            type=variable.type,
            scope=variable.scope,
            description=variable.description,
            environment_id=variable.environment_id,
            user_id=variable.user_id,
            session_id=variable.session_id,
            created_by=variable.created_by,
            created_at=variable.created_at.isoformat(),
            updated_at=variable.updated_at.isoformat(),
            is_active=variable.is_active,
            is_sensitive=variable.is_sensitive,
            display_value=variable.display_value
        )
        
        return success_response(response_data)
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"获取变量失败: {str(e)}")
        return error_response("获取变量失败")


@router.put("/{variable_id}", response_model=dict)
async def update_variable(
    variable_id: int,
    variable_data: VariableUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新变量"""
    try:
        # 先获取变量检查权限
        variable = await VariableService.get_variable(variable_id)
        
        # 权限检查
        if not current_user.is_admin:
            if variable.scope == VariableScope.GLOBAL:
                raise HTTPException(status_code=403, detail="只有管理员可以修改全局变量")
            elif variable.scope == VariableScope.PERSONAL and variable.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="只能修改自己的个人变量")
            elif variable.scope in [VariableScope.ENVIRONMENT, VariableScope.TEMPORARY]:
                raise HTTPException(status_code=403, detail="权限不足")
        
        updated_variable = await VariableService.update_variable(
            variable_id=variable_id,
            name=variable_data.name,
            value=variable_data.value,
            type=variable_data.type,
            description=variable_data.description,
            is_active=variable_data.is_active,
            is_sensitive=variable_data.is_sensitive
        )
        
        response_data = VariableResponse(
            id=updated_variable.id,
            name=updated_variable.name,
            value=updated_variable.value,
            type=updated_variable.type,
            scope=updated_variable.scope,
            description=updated_variable.description,
            environment_id=updated_variable.environment_id,
            user_id=updated_variable.user_id,
            session_id=updated_variable.session_id,
            created_by=updated_variable.created_by,
            created_at=updated_variable.created_at.isoformat(),
            updated_at=updated_variable.updated_at.isoformat(),
            is_active=updated_variable.is_active,
            is_sensitive=updated_variable.is_sensitive,
            display_value=updated_variable.display_value
        )
        
        return success_response(response_data, "变量更新成功")
        
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        logger.error(f"更新变量失败: {str(e)}")
        return error_response("更新变量失败")


@router.delete("/{variable_id}", response_model=dict)
async def delete_variable(
    variable_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除变量"""
    try:
        # 先获取变量检查权限
        variable = await VariableService.get_variable(variable_id)
        
        # 权限检查
        if not current_user.is_admin:
            if variable.scope == VariableScope.GLOBAL:
                raise HTTPException(status_code=403, detail="只有管理员可以删除全局变量")
            elif variable.scope == VariableScope.PERSONAL and variable.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="只能删除自己的个人变量")
            elif variable.scope in [VariableScope.ENVIRONMENT, VariableScope.TEMPORARY]:
                raise HTTPException(status_code=403, detail="权限不足")
        
        await VariableService.delete_variable(variable_id)
        
        return success_response(None, "变量删除成功")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"删除变量失败: {str(e)}")
        return error_response("删除变量失败")


@router.post("/batch", response_model=dict)
async def batch_create_variables(
    batch_data: VariableBatch,
    current_user: User = Depends(get_current_user)
):
    """批量创建变量"""
    try:
        # 权限检查和数据预处理
        variables_data = []
        for var_data in batch_data.variables:
            if var_data.scope == VariableScope.GLOBAL and not current_user.is_admin:
                continue  # 跳过没有权限的全局变量
            
            if var_data.scope == VariableScope.PERSONAL:
                var_data.user_id = current_user.id
            
            variables_data.append(var_data.dict())
        
        variables = await VariableService.batch_create_variables(
            variables_data, current_user.id
        )
        
        return success_response({
            "created_count": len(variables),
            "total_count": len(batch_data.variables)
        }, "批量创建变量完成")
        
    except Exception as e:
        logger.error(f"批量创建变量失败: {str(e)}")
        return error_response("批量创建变量失败")


@router.post("/resolve", response_model=dict)
async def resolve_variables(
    text: str = Body(..., description="需要解析的文本"),
    environment_id: Optional[int] = Body(None, description="环境ID"),
    session_id: Optional[str] = Body(None, description="会话ID"),
    current_user: User = Depends(get_current_user)
):
    """解析文本中的变量引用"""
    try:
        resolved_text = await VariableService.resolve_variables(
            text=text,
            environment_id=environment_id,
            user_id=current_user.id,
            session_id=session_id
        )
        
        return success_response({
            "original_text": text,
            "resolved_text": resolved_text
        })
        
    except Exception as e:
        logger.error(f"变量解析失败: {str(e)}")
        return error_response("变量解析失败")


@router.post("/export", response_model=dict)
async def export_variables(
    export_config: VariableExport,
    current_user: User = Depends(get_current_user)
):
    """导出变量"""
    try:
        # 权限检查
        if not current_user.is_admin and export_config.scope != VariableScope.PERSONAL:
            raise HTTPException(status_code=403, detail="只有管理员可以导出非个人变量")
        
        export_data = await VariableService.export_variables(
            format=export_config.format,
            scope=export_config.scope,
            environment_id=export_config.environment_id,
            include_sensitive=export_config.include_sensitive and current_user.is_admin
        )
        
        return success_response({
            "format": export_config.format,
            "data": export_data
        })
        
    except Exception as e:
        logger.error(f"导出变量失败: {str(e)}")
        return error_response("导出变量失败")


@router.post("/cleanup-temp", response_model=dict)
async def cleanup_temporary_variables(
    max_age_hours: int = Body(24, description="最大保留时间（小时）"),
    current_user: User = Depends(get_current_user)
):
    """清理过期的临时变量"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="只有管理员可以执行清理操作")
        
        count = await VariableService.cleanup_temporary_variables(max_age_hours)
        
        return success_response({
            "cleaned_count": count
        }, f"清理了 {count} 个过期临时变量")
        
    except Exception as e:
        logger.error(f"清理临时变量失败: {str(e)}")
        return error_response("清理临时变量失败")
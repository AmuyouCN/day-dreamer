"""
统一响应格式模块

提供标准的API响应格式
"""

from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class ApiResponse(BaseModel):
    """API标准响应模型"""
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: str = datetime.utcnow().isoformat()


class PagedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class ErrorDetail(BaseModel):
    """错误详情模型"""
    field: str
    message: str


def success_response(data: Any = None, message: str = "success") -> dict:
    """创建成功响应"""
    return ApiResponse(data=data, message=message).dict()


def error_response(
    code: int, 
    message: str, 
    errors: Optional[List[ErrorDetail]] = None
) -> dict:
    """创建错误响应"""
    response = ApiResponse(code=code, message=message, data=None).dict()
    if errors:
        response["errors"] = [error.dict() if isinstance(error, ErrorDetail) else error for error in errors]
    return response


def paged_response(
    items: List[Any],
    total: int,
    page: int,
    size: int,
    message: str = "success"
) -> dict:
    """创建分页响应"""
    pages = (total + size - 1) // size if size > 0 else 0
    paged_data = PagedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
    return success_response(data=paged_data.dict(), message=message)
"""
自定义异常和全局异常处理模块

定义业务异常和全局异常处理器
"""

import traceback
from typing import Any, Optional, List
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from datetime import datetime


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, message: str, code: int = 400, errors: Optional[List] = None):
        self.message = message
        self.code = code
        self.errors = errors or []
        super().__init__(self.message)


class ValidationError(BusinessException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败", errors: Optional[List] = None):
        super().__init__(message, 422, errors)


class AuthenticationError(BusinessException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, 401)


class AuthorizationError(BusinessException):
    """权限异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)


class NotFoundError(BusinessException):
    """资源不存在异常"""
    
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class ConflictError(BusinessException):
    """数据冲突异常"""
    
    def __init__(self, message: str = "数据冲突"):
        super().__init__(message, 409)


class DatabaseError(BusinessException):
    """数据库异常"""
    
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, 500)


def create_error_response(
    code: int, 
    message: str, 
    errors: Optional[List] = None
) -> dict:
    """创建错误响应"""
    response = {
        "code": code,
        "message": message,
        "data": None,
        "timestamp": datetime.utcnow().isoformat()
    }
    if errors:
        response["errors"] = errors
    return response


def create_success_response(
    data: Any = None, 
    message: str = "success"
) -> dict:
    """创建成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    
    # 记录异常信息
    logger.error(f"全局异常捕获: {type(exc).__name__}: {exc}")
    logger.error(f"请求路径: {request.method} {request.url}")
    
    if logger.level("DEBUG").no >= logger._core.min_level:
        logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    # 处理自定义业务异常
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=exc.code,
            content=create_error_response(exc.code, exc.message, exc.errors)
        )
    
    # 处理FastAPI的HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(exc.status_code, exc.detail)
        )
    
    # 处理其他未知异常
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, "内部服务器错误")
    )
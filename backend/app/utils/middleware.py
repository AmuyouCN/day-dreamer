"""
请求日志和监控中间件

记录请求日志和性能监控
"""

import time
import uuid
from fastapi import Request
from loguru import logger


async def logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    
    # 生成请求ID
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # 记录请求开始
    logger.info(
        f"[{request_id}] {request.method} {request.url} - "
        f"客户端IP: {request.client.host if request.client else 'unknown'}"
    )
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录请求结束
    logger.info(
        f"[{request_id}] {request.method} {request.url} - "
        f"状态码: {response.status_code} - "
        f"处理时间: {process_time:.3f}s"
    )
    
    # 添加响应头
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


async def cors_middleware(request: Request, call_next):
    """CORS中间件（如果需要自定义CORS处理）"""
    response = await call_next(request)
    
    # 添加CORS头（通常由FastAPI的CORSMiddleware处理）
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response
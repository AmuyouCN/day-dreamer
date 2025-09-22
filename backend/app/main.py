"""
FastAPI应用入口

配置和启动FastAPI应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.redis import init_redis, close_redis
from app.utils.logger import setup_logger
from app.utils.exceptions import global_exception_handler
from app.utils.middleware import logging_middleware
from app.api.v1 import auth, users, interfaces, test_cases, environments, variables, tasks, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    
    # 启动时初始化
    logger.info("应用启动中...")
    
    # 初始化日志系统
    setup_logger()
    
    # 初始化数据库
    await init_database()
    
    # 初始化Redis
    await init_redis()
    
    logger.info(f"应用启动完成 - {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # FastAPI应用配置
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于FastAPI的用户权限管理和接口测试平台",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    yield
    
    # 关闭时清理
    logger.info("应用关闭中...")
    await close_redis()
    await close_database()
    logger.info("应用已关闭")


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.middleware("http")(logging_middleware)

# 添加全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)

# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(interfaces.router, prefix="/api/v1/interfaces", tags=["接口管理"])
app.include_router(test_cases.router, prefix="/api/v1/test-cases", tags=["测试用例"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["环境管理"])
app.include_router(variables.router, prefix="/api/v1/variables", tags=["变量管理"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务管理"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["报告管理"])

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"{settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/info")
async def app_info():
    """应用信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "environment": "development" if settings.DEBUG else "production"
    }
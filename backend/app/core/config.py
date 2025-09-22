"""
核心配置管理模块
基于 pydantic-settings 的配置管理，支持环境变量和配置文件
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基本配置
    APP_NAME: str = Field(default="接口自动化测试平台", alias="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", alias="APP_VERSION")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    PORT: int = Field(default=8000, alias="PORT")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    
    # 数据库配置
    DATABASE_HOST: str = Field(default="localhost", alias="DATABASE_HOST")
    DATABASE_PORT: int = Field(default=3306, alias="DATABASE_PORT")
    DATABASE_USER: str = Field(default="root", alias="DATABASE_USER")
    DATABASE_PASSWORD: str = Field(default="", alias="DATABASE_PASSWORD")
    DATABASE_NAME: str = Field(default="test_platform", alias="DATABASE_NAME")
    DATABASE_ECHO: bool = Field(default=False, alias="DATABASE_ECHO")
    
    # Redis配置
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(default=0, alias="REDIS_DB")
    REDIS_PASSWORD: str = Field(default="", alias="REDIS_PASSWORD")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    
    # 安全配置
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=2, alias="ACCESS_TOKEN_EXPIRE_HOURS")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Celery配置
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_DIR: str = Field(default="logs", alias="LOG_DIR")
    LOG_ROTATION: str = Field(default="100 MB", alias="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", alias="LOG_RETENTION")
    
    # 测试配置
    MAX_CONCURRENT_TESTS: int = Field(default=10, alias="MAX_CONCURRENT_TESTS")
    TEST_TIMEOUT: int = Field(default=300, alias="TEST_TIMEOUT")
    
    # 文件上传配置
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024, alias="UPLOAD_MAX_SIZE")  # 10MB
    UPLOAD_ALLOWED_TYPES: List[str] = Field(
        default=[".json", ".yaml", ".yml", ".csv", ".xlsx"],
        alias="UPLOAD_ALLOWED_TYPES"
    )
    
    @property
    def database_config(self) -> dict:
        """Tortoise ORM数据库配置"""
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self.DATABASE_HOST,
                        "port": self.DATABASE_PORT,
                        "user": self.DATABASE_USER,
                        "password": self.DATABASE_PASSWORD,
                        "database": self.DATABASE_NAME,
                        "charset": "utf8mb4",
                        "echo": self.DATABASE_ECHO
                    }
                }
            },
            "apps": {
                "models": {
                    "models": [
                        "app.models.user",
                        "app.models.role",
                        "app.models.permission",
                        "app.models.interface",
                        "app.models.test_case",
                        "app.models.environment",
                        "app.models.variable",
                        "app.services.report_service"
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "Asia/Shanghai"
        }
    
    @property
    def redis_config(self) -> dict:
        """Redis连接配置"""
        return {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD or None,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "decode_responses": True
        }
    
    @property
    def celery_config(self) -> dict:
        """Celery配置"""
        return {
            "broker_url": self.CELERY_BROKER_URL,
            "result_backend": self.CELERY_RESULT_BACKEND,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "Asia/Shanghai",
            "enable_utc": True,
            "worker_prefetch_multiplier": 1,
            "task_acks_late": True,
            "task_reject_on_worker_lost": True
        }


settings = Settings()
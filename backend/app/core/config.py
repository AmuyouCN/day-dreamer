"""
核心配置管理模块

基于 pydantic-settings 的配置管理，支持环境变量和配置文件
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
import urllib.parse as urlparse

class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基本配置
    app_name: str = Field(default="接口自动化测试平台", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    allowed_hosts: List[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    
    # 数据库配置
    database_url: str = Field(default="sqlite://test.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    
    # 安全配置
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    access_token_expire_hours: int = Field(default=2, alias="ACCESS_TOKEN_EXPIRE_HOURS")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Celery配置
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")
    log_rotation: str = Field(default="100 MB", alias="LOG_ROTATION")
    log_retention: str = Field(default="30 days", alias="LOG_RETENTION")
    
    # 测试配置
    max_concurrent_tests: int = Field(default=10, alias="MAX_CONCURRENT_TESTS")
    test_timeout: int = Field(default=300, alias="TEST_TIMEOUT")  # 秒
    
    # 文件上传配置
    upload_max_size: int = Field(default=10 * 1024 * 1024, alias="UPLOAD_MAX_SIZE")  # 10MB
    upload_allowed_types: List[str] = Field(
        default=[".json", ".yaml", ".yml", ".csv", ".xlsx"],
        alias="UPLOAD_ALLOWED_TYPES"
    )
    
    # 邮件配置(可选)
    smtp_server: Optional[str] = Field(default=None, alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    
    # 监控配置
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    
    def _parse_db_url(self) -> dict:
        """解析数据库URL"""
        parsed = urlparse.urlparse(self.database_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "username": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/") if parsed.path else None
        }
    
    @property
    def database_config(self) -> dict:
        """Tortoise ORM数据库配置"""
        db_info = self._parse_db_url()
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": db_info["host"],
                        "port": db_info["port"],
                        "user": db_info["username"],
                        "password": db_info["password"],
                        "database": db_info["database"],
                        "charset": "utf8mb4",
                        "echo": self.database_echo
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
        parsed = urlparse.urlparse(self.redis_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "max_connections": self.redis_max_connections,
            "decode_responses": True
        }
    
    @property
    def celery_config(self) -> dict:
        """Celery配置"""
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "Asia/Shanghai",
            "enable_utc": True,
            "worker_prefetch_multiplier": 1,
            "task_acks_late": True,
            "task_reject_on_worker_lost": True
        }


# 创建全局配置实例
settings = Settings()
"""
Aerich 数据库配置文件

专门为 aerich 迁移工具提供的 Tortoise ORM 配置
"""

from app.core.config import settings

# Aerich 配置
TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "localhost",
                "port": 3306,
                "user": "root", 
                "password": "password",
                "database": "test_platform_dev",
                "charset": "utf8mb4",
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.role", 
                "app.models.permission",
                "app.models.environment",
                "app.models.api_definition",
                "app.models.test_case",
                "app.models.variable",
                "app.models.test_execution",
                "aerich.models"  # aerich 自身的模型
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "Asia/Shanghai"
}
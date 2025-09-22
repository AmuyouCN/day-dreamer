"""
Aerich 数据库配置文件
专门为 aerich 迁移工具提供的 Tortoise ORM 配置
使用统一的配置源，避免重复
"""

import copy
from app.core.config import settings

# 基于应用的数据库配置创建 Aerich 配置
def get_tortoise_config():
    """获取Aerich使用的Tortoise配置"""
    app_config = settings.database_config
    
    # 深拷贝应用配置，确保修改不影响原始配置
    aerich_config = copy.deepcopy(app_config)
    
    # 添加Aerich自身需要的模型
    aerich_config["apps"]["models"]["models"].extend([
        "app.models.api_definition",
        "app.models.test_execution",
        "aerich.models"  # aerich 自身的模型
    ])
    
    return aerich_config

# Aerich 配置
TORTOISE_CONFIG = get_tortoise_config()
"""
环境配置数据模型

定义测试环境配置
"""

from tortoise.models import Model
from tortoise import fields


class Environment(Model):
    """环境模型"""
    
    id = fields.IntField(pk=True, description="环境ID")
    name = fields.CharField(max_length=50, unique=True, description="环境名称")
    description = fields.CharField(max_length=200, null=True, description="环境描述")
    config = fields.JSONField(default=dict, description="环境配置")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 关联字段
    variables = fields.ReverseRelation["Variable"]
    test_executions = fields.ReverseRelation["TestExecution"]
    
    class Meta:
        table = "environments"
        description = "环境表"
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.config.get("base_url", "")
    
    def get_headers(self) -> dict:
        """获取默认请求头"""
        return self.config.get("headers", {})
    
    def __str__(self):
        return f"Environment(id={self.id}, name='{self.name}')"
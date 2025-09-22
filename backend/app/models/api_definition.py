"""
接口定义数据模型

定义API接口的基本信息和配置
"""

from tortoise.models import Model
from tortoise import fields
from enum import Enum


class HttpMethod(str, Enum):
    """HTTP请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiDefinition(Model):
    """接口定义模型"""
    
    id = fields.IntField(pk=True, description="接口ID")
    name = fields.CharField(max_length=100, description="接口名称")
    description = fields.TextField(null=True, description="接口描述")
    method = fields.CharEnumField(HttpMethod, description="HTTP方法")
    url = fields.CharField(max_length=500, description="接口URL")
    headers = fields.JSONField(default=dict, description="请求头")
    query_params = fields.JSONField(default=dict, description="查询参数")
    body_schema = fields.JSONField(default=dict, description="请求体模式")
    response_schema = fields.JSONField(default=dict, description="响应模式")
    is_public = fields.BooleanField(default=False, description="是否公开")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 关联字段
    creator = fields.ForeignKeyField(
        "models.User", 
        related_name="created_apis",
        description="创建者"
    )
    test_cases = fields.ReverseRelation["TestCase"]
    
    class Meta:
        table = "api_definitions"
        description = "接口定义表"
        indexes = [
            ("method", "url"),  # 方法和URL的组合索引
            "creator_id",
        ]
    
    def get_full_url(self, base_url: str = "") -> str:
        """获取完整URL"""
        if self.url.startswith("http"):
            return self.url
        return f"{base_url.rstrip('/')}/{self.url.lstrip('/')}"
    
    async def get_test_case_count(self) -> int:
        """获取测试用例数量"""
        return await self.test_cases.filter(is_active=True).count()
    
    def __str__(self):
        return f"ApiDefinition(id={self.id}, name='{self.name}', method='{self.method}')"
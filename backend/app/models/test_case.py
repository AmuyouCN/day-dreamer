"""
测试用例数据模型

定义测试用例的结构和断言规则
"""

from tortoise.models import Model
from tortoise import fields
from enum import Enum


class AssertionType(str, Enum):
    """断言类型"""
    STATUS_CODE = "status_code"
    RESPONSE_TIME = "response_time"
    JSON_PATH = "json_path"
    REGEX = "regex"
    CONTAINS = "contains"
    EQUALS = "equals"


class TestCase(Model):
    """测试用例模型"""
    
    id = fields.IntField(pk=True, description="测试用例ID")
    name = fields.CharField(max_length=100, description="测试用例名称")
    description = fields.TextField(null=True, description="测试用例描述")
    request_data = fields.JSONField(default=dict, description="请求数据")
    expected_response = fields.JSONField(default=dict, description="期望响应")
    assertions = fields.JSONField(default=list, description="断言规则")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 关联字段
    api = fields.ForeignKeyField(
        "models.ApiDefinition", 
        related_name="test_cases",
        description="关联接口"
    )
    creator = fields.ForeignKeyField(
        "models.User", 
        related_name="created_test_cases",
        description="创建者"
    )
    test_results = fields.ReverseRelation["TestResult"]
    
    class Meta:
        table = "test_cases"
        description = "测试用例表"
        indexes = [
            "api_id",
            "creator_id",
            ("is_active", "created_at"),
        ]
    
    def get_request_headers(self) -> dict:
        """获取请求头"""
        return self.request_data.get("headers", {})
    
    def get_request_body(self) -> dict:
        """获取请求体"""
        return self.request_data.get("body", {})
    
    def get_query_params(self) -> dict:
        """获取查询参数"""
        return self.request_data.get("query_params", {})
    
    async def get_execution_count(self) -> int:
        """获取执行次数"""
        return await self.test_results.all().count()
    
    async def get_success_rate(self) -> float:
        """获取成功率"""
        total = await self.test_results.all().count()
        if total == 0:
            return 0.0
        
        success = await self.test_results.filter(status="pass").count()
        return round(success / total * 100, 2)
    
    def __str__(self):
        return f"TestCase(id={self.id}, name='{self.name}')"
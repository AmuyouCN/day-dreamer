"""
变量管理相关数据模型

支持全局变量、环境变量、个人变量和临时变量
"""

from tortoise.models import Model
from tortoise import fields
from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel


class VariableScope(str, Enum):
    """变量作用域枚举"""
    GLOBAL = "global"        # 全局变量
    ENVIRONMENT = "environment"  # 环境变量
    PERSONAL = "personal"    # 个人变量
    TEMPORARY = "temporary"  # 临时变量


class VariableType(str, Enum):
    """变量类型枚举"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    FILE = "file"


class Variable(Model):
    """变量模型"""
    
    id = fields.IntField(pk=True, description="主键ID")
    name = fields.CharField(max_length=100, description="变量名称")
    value = fields.TextField(description="变量值")
    type = fields.CharEnumField(VariableType, default=VariableType.STRING, description="变量类型")
    scope = fields.CharEnumField(VariableScope, description="变量作用域")
    description = fields.TextField(null=True, description="变量描述")
    
    # 关联字段
    environment_id = fields.IntField(null=True, description="关联环境ID（环境变量）")
    user_id = fields.IntField(null=True, description="关联用户ID（个人变量）")
    session_id = fields.CharField(max_length=100, null=True, description="会话ID（临时变量）")
    
    # 元数据
    created_by = fields.IntField(description="创建者ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    is_active = fields.BooleanField(default=True, description="是否启用")
    is_sensitive = fields.BooleanField(default=False, description="是否敏感数据")
    
    class Meta:
        table = "variables"
        table_description = "变量管理表"
        indexes = [
            ("name", "scope"),
            ("environment_id",),
            ("user_id",),
            ("session_id",),
        ]
    
    def __str__(self):
        return f"{self.name}({self.scope})"
    
    @property
    def display_value(self) -> str:
        """显示值（敏感数据脱敏）"""
        if self.is_sensitive:
            return "***"
        return self.value
    
    def get_typed_value(self) -> Any:
        """获取类型化的值"""
        if self.type == VariableType.STRING:
            return self.value
        elif self.type == VariableType.NUMBER:
            try:
                return float(self.value) if '.' in self.value else int(self.value)
            except ValueError:
                return self.value
        elif self.type == VariableType.BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.type == VariableType.JSON:
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return self.value
        else:
            return self.value


# Pydantic模型用于API交互

class VariableCreate(BaseModel):
    """创建变量请求模型"""
    name: str
    value: str
    type: VariableType = VariableType.STRING
    scope: VariableScope
    description: Optional[str] = None
    environment_id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    is_sensitive: bool = False


class VariableUpdate(BaseModel):
    """更新变量请求模型"""
    name: Optional[str] = None
    value: Optional[str] = None
    type: Optional[VariableType] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_sensitive: Optional[bool] = None


class VariableResponse(BaseModel):
    """变量响应模型"""
    id: int
    name: str
    value: str
    type: VariableType
    scope: VariableScope
    description: Optional[str]
    environment_id: Optional[int]
    user_id: Optional[int]
    session_id: Optional[str]
    created_by: int
    created_at: str
    updated_at: str
    is_active: bool
    is_sensitive: bool
    display_value: str
    
    class Config:
        from_attributes = True


class VariableQuery(BaseModel):
    """变量查询模型"""
    scope: Optional[VariableScope] = None
    environment_id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    is_active: Optional[bool] = True
    keyword: Optional[str] = None


class VariableBatch(BaseModel):
    """批量变量操作模型"""
    variables: list[VariableCreate]


class VariableExport(BaseModel):
    """变量导出模型"""
    format: str = "json"  # json, csv, env
    scope: Optional[VariableScope] = None
    environment_id: Optional[int] = None
    include_sensitive: bool = False
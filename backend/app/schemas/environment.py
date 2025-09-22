"""
环境管理相关的数据传输对象

定义环境配置的请求和响应格式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EnvironmentCreate(BaseModel):
    """创建环境请求"""
    name: str = Field(..., min_length=1, max_length=50, description="环境名称")
    description: Optional[str] = Field(None, max_length=200, description="环境描述")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="环境配置")
    is_active: bool = Field(default=True, description="是否激活")


class EnvironmentUpdate(BaseModel):
    """更新环境请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="环境名称")
    description: Optional[str] = Field(None, max_length=200, description="环境描述")
    config: Optional[Dict[str, Any]] = Field(None, description="环境配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class EnvironmentResponse(BaseModel):
    """环境响应"""
    id: int = Field(..., description="环境ID")
    name: str = Field(..., description="环境名称")
    description: Optional[str] = Field(None, description="环境描述")
    config: Dict[str, Any] = Field(..., description="环境配置")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = {"from_attributes": True}


class EnvironmentListRequest(BaseModel):
    """环境列表请求"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否激活过滤")
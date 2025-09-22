"""
接口管理相关的数据传输对象

定义接口定义、测试等相关的请求和响应格式
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
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


class ApiDefinitionCreate(BaseModel):
    """创建接口定义请求"""
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: HttpMethod = Field(..., description="HTTP方法")
    url: str = Field(..., min_length=1, max_length=500, description="接口URL")
    headers: Optional[Dict[str, Any]] = Field(default_factory=dict, description="请求头")
    query_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="查询参数")
    body_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="请求体模式")
    response_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="响应模式")
    is_public: bool = Field(default=False, description="是否公开")


class ApiDefinitionUpdate(BaseModel):
    """更新接口定义请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: Optional[HttpMethod] = Field(None, description="HTTP方法")
    url: Optional[str] = Field(None, min_length=1, max_length=500, description="接口URL")
    headers: Optional[Dict[str, Any]] = Field(None, description="请求头")
    query_params: Optional[Dict[str, Any]] = Field(None, description="查询参数")
    body_schema: Optional[Dict[str, Any]] = Field(None, description="请求体模式")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="响应模式")
    is_public: Optional[bool] = Field(None, description="是否公开")


class ApiDefinitionResponse(BaseModel):
    """接口定义响应"""
    id: int = Field(..., description="接口ID")
    name: str = Field(..., description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: str = Field(..., description="HTTP方法")
    url: str = Field(..., description="接口URL")
    headers: Dict[str, Any] = Field(..., description="请求头")
    query_params: Dict[str, Any] = Field(..., description="查询参数")
    body_schema: Dict[str, Any] = Field(..., description="请求体模式")
    response_schema: Dict[str, Any] = Field(..., description="响应模式")
    creator_id: int = Field(..., description="创建者ID")
    is_public: bool = Field(..., description="是否公开")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = {"from_attributes": True}


class TestApiRequest(BaseModel):
    """测试接口请求"""
    request_data: Dict[str, Any] = Field(default_factory=dict, description="请求数据")
    environment_id: Optional[int] = Field(None, description="环境ID")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict, description="变量")


class TestApiResponse(BaseModel):
    """测试接口响应"""
    success: bool = Field(..., description="是否成功")
    status_code: int = Field(..., description="响应状态码")
    response_time: float = Field(..., description="响应时间（毫秒）")
    response_data: Dict[str, Any] = Field(..., description="响应数据")
    headers: Dict[str, str] = Field(..., description="响应头")
    error_message: Optional[str] = Field(None, description="错误信息")


class ApiListRequest(BaseModel):
    """接口列表请求"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    method: Optional[HttpMethod] = Field(None, description="HTTP方法过滤")
    is_public: Optional[bool] = Field(None, description="是否公开过滤")
    creator_id: Optional[int] = Field(None, description="创建者过滤")


class ApiImportRequest(BaseModel):
    """接口导入请求"""
    import_type: str = Field(..., description="导入类型：swagger/postman/har")
    import_data: Dict[str, Any] = Field(..., description="导入数据")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的接口")
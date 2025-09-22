"""
测试用例相关的数据传输对象

定义测试用例CRUD操作的请求和响应格式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AssertionType(str, Enum):
    """断言类型"""
    STATUS_CODE = "status_code"
    RESPONSE_TIME = "response_time"
    JSON_PATH = "json_path"
    REGEX = "regex"
    CONTAINS = "contains"
    EQUALS = "equals"


class AssertionOperator(str, Enum):
    """断言操作符"""
    EQ = "eq"  # 等于
    NE = "ne"  # 不等于
    GT = "gt"  # 大于
    LT = "lt"  # 小于
    GTE = "gte"  # 大于等于
    LTE = "lte"  # 小于等于
    CONTAINS = "contains"  # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    REGEX = "regex"  # 正则匹配


class AssertionRule(BaseModel):
    """断言规则"""
    type: AssertionType = Field(..., description="断言类型")
    field: Optional[str] = Field(None, description="断言字段")
    operator: AssertionOperator = Field(..., description="断言操作符")
    expected: Any = Field(..., description="期望值")
    description: Optional[str] = Field(None, description="断言描述")


class TestCaseCreate(BaseModel):
    """创建测试用例请求"""
    name: str = Field(..., min_length=1, max_length=100, description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    api_id: int = Field(..., description="关联接口ID")
    request_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="请求数据")
    expected_response: Optional[Dict[str, Any]] = Field(default_factory=dict, description="期望响应")
    assertions: List[AssertionRule] = Field(default_factory=list, description="断言规则")
    is_active: bool = Field(default=True, description="是否激活")


class TestCaseUpdate(BaseModel):
    """更新测试用例请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    request_data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    expected_response: Optional[Dict[str, Any]] = Field(None, description="期望响应")
    assertions: Optional[List[AssertionRule]] = Field(None, description="断言规则")
    is_active: Optional[bool] = Field(None, description="是否激活")


class TestCaseResponse(BaseModel):
    """测试用例响应"""
    id: int = Field(..., description="测试用例ID")
    name: str = Field(..., description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    api_id: int = Field(..., description="关联接口ID")
    request_data: Dict[str, Any] = Field(..., description="请求数据")
    expected_response: Dict[str, Any] = Field(..., description="期望响应")
    assertions: List[AssertionRule] = Field(..., description="断言规则")
    creator_id: int = Field(..., description="创建者ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 统计信息
    execution_count: Optional[int] = Field(None, description="执行次数")
    success_rate: Optional[float] = Field(None, description="成功率")
    
    model_config = {"from_attributes": True}


class RunTestCaseRequest(BaseModel):
    """执行测试用例请求"""
    environment_id: int = Field(..., description="环境ID")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict, description="变量")
    save_result: bool = Field(default=True, description="是否保存结果")


class TestCaseExecutionResult(BaseModel):
    """测试用例执行结果"""
    test_case_id: int = Field(..., description="测试用例ID")
    status: str = Field(..., description="执行状态")
    duration: float = Field(..., description="执行时间（毫秒）")
    request_data: Dict[str, Any] = Field(..., description="实际请求数据")
    response_data: Dict[str, Any] = Field(..., description="实际响应数据")
    assertion_results: List[Dict[str, Any]] = Field(..., description="断言结果")
    error_message: Optional[str] = Field(None, description="错误信息")


class TestCaseListRequest(BaseModel):
    """测试用例列表请求"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    api_id: Optional[int] = Field(None, description="接口ID过滤")
    is_active: Optional[bool] = Field(None, description="是否激活过滤")
    creator_id: Optional[int] = Field(None, description="创建者过滤")


class CopyTestCaseRequest(BaseModel):
    """复制测试用例请求"""
    new_name: str = Field(..., min_length=1, max_length=100, description="新测试用例名称")
    copy_to_api_id: Optional[int] = Field(None, description="复制到指定接口ID")


class BatchExecutionRequest(BaseModel):
    """批量执行请求"""
    test_case_ids: List[int] = Field(..., min_items=1, description="测试用例ID列表")
    environment_id: int = Field(..., description="环境ID")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict, description="全局变量")
    parallel: bool = Field(default=False, description="是否并行执行")
    max_workers: Optional[int] = Field(default=5, ge=1, le=20, description="最大并发数")
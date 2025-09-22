"""
用户相关的数据传输对象

定义用户CRUD操作的请求和响应格式
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserPasswordUpdate(BaseModel):
    \"\"\"用户密码更新请求\"\"\"
    current_password: str = Field(..., description=\"当前密码\")
    new_password: str = Field(..., min_length=6, max_length=100, description=\"新密码\")


class UserResponse(UserBase):
    \"\"\"用户响应\"\"\"
    id: int = Field(..., description=\"用户ID\")
    created_at: datetime = Field(..., description=\"创建时间\")
    updated_at: datetime = Field(..., description=\"更新时间\")
    last_login: Optional[datetime] = Field(None, description=\"最后登录时间\")
    
    model_config = {\"from_attributes\": True}


class UserListRequest(BaseModel):
    \"\"\"用户列表请求\"\"\"
    page: int = Field(default=1, ge=1, description=\"页码\")
    size: int = Field(default=10, ge=1, le=100, description=\"每页数量\")
    search: Optional[str] = Field(None, max_length=100, description=\"搜索关键词\")
    is_active: Optional[bool] = Field(None, description=\"是否激活\")


class UserListResponse(BaseModel):
    \"\"\"用户列表响应\"\"\"
    users: List[UserResponse] = Field(..., description=\"用户列表\")
    total: int = Field(..., description=\"总数量\")
    page: int = Field(..., description=\"当前页码\")
    size: int = Field(..., description=\"每页数量\")
    pages: int = Field(..., description=\"总页数\")


class AssignRoleRequest(BaseModel):
    \"\"\"分配角色请求\"\"\"
    role_ids: List[int] = Field(..., description=\"角色ID列表\")"
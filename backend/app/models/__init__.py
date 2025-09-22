"""
数据模型模块

导入所有数据模型，用于Tortoise ORM自动发现
"""

from .user import User
from .role import Role
from .permission import Permission
from .environment import Environment
from .api_definition import ApiDefinition
from .test_case import TestCase
from .variable import Variable
from .test_execution import TestExecution, TestResult

__all__ = [
    "User",
    "Role", 
    "Permission",
    "Environment",
    "ApiDefinition",
    "TestCase",
    "Variable",
    "TestExecution",
    "TestResult"
]
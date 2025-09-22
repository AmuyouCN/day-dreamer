"""
测试执行和结果数据模型

定义测试执行记录和结果存储
"""

from tortoise.models import Model
from tortoise import fields
from enum import Enum


class ExecutionType(str, Enum):
    """执行类型"""
    SINGLE = "single"  # 单个测试用例
    SCENARIO = "scenario"  # 测试场景
    BATCH = "batch"  # 批量测试


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消


class TestResultStatus(str, Enum):
    """测试结果状态"""
    PASS = "pass"  # 通过
    FAIL = "fail"  # 失败
    ERROR = "error"  # 错误
    SKIP = "skip"  # 跳过


class TestExecution(Model):
    """测试执行模型"""
    
    id = fields.IntField(pk=True, description="执行ID")
    execution_type = fields.CharEnumField(ExecutionType, description="执行类型")
    target_id = fields.IntField(description="目标ID（测试用例或场景ID）")
    status = fields.CharEnumField(ExecutionStatus, default=ExecutionStatus.PENDING, description="执行状态")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    finished_at = fields.DatetimeField(null=True, description="结束时间")
    execution_config = fields.JSONField(default=dict, description="执行配置")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    
    # 关联字段
    executor = fields.ForeignKeyField(
        "models.User", 
        related_name="test_executions",
        description="执行者"
    )
    environment = fields.ForeignKeyField(
        "models.Environment", 
        related_name="test_executions",
        description="执行环境"
    )
    test_results = fields.ReverseRelation["TestResult"]
    
    class Meta:
        table = "test_executions"
        description = "测试执行表"
        indexes = [
            "executor_id",
            "status",
            "created_at",
            ("execution_type", "target_id"),
        ]
    
    @property
    def duration(self) -> float:
        """执行时长（秒）"""
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            return delta.total_seconds()
        return 0.0
    
    async def get_result_summary(self) -> dict:
        """获取结果汇总"""
        results = await self.test_results.all()
        
        summary = {
            "total": len(results),
            "pass": 0,
            "fail": 0,
            "error": 0,
            "skip": 0
        }
        
        for result in results:
            summary[result.status] += 1
        
        if summary["total"] > 0:
            summary["pass_rate"] = round(summary["pass"] / summary["total"] * 100, 2)
        else:
            summary["pass_rate"] = 0.0
        
        return summary
    
    def __str__(self):
        return f"TestExecution(id={self.id}, type='{self.execution_type}', status='{self.status}')"


class TestResult(Model):
    """测试结果模型"""
    
    id = fields.IntField(pk=True, description="结果ID")
    status = fields.CharEnumField(TestResultStatus, description="测试状态")
    request_data = fields.JSONField(null=True, description="实际请求数据")
    response_data = fields.JSONField(null=True, description="实际响应数据")
    assertion_results = fields.JSONField(default=list, description="断言结果")
    duration = fields.FloatField(null=True, description="执行时间（毫秒）")
    error_message = fields.TextField(null=True, description="错误信息")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    
    # 关联字段
    execution = fields.ForeignKeyField(
        "models.TestExecution", 
        related_name="test_results",
        description="执行记录"
    )
    test_case = fields.ForeignKeyField(
        "models.TestCase", 
        related_name="test_results",
        description="测试用例"
    )
    
    class Meta:
        table = "test_results"
        description = "测试结果表"
        indexes = [
            "execution_id",
            "test_case_id",
            "status",
            "created_at",
        ]
    
    def get_response_status_code(self) -> int:
        """获取响应状态码"""
        if self.response_data:
            return self.response_data.get("status_code", 0)
        return 0
    
    def get_response_time(self) -> float:
        """获取响应时间"""
        return self.duration or 0.0
    
    def __str__(self):
        return f"TestResult(id={self.id}, status='{self.status}')"
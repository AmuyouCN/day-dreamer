"""
异步任务模块

包含测试执行、报告生成、系统维护等异步任务
"""

from app.tasks.test_execution import (
    execute_single_test,
    execute_batch_tests,
    execute_test_suite,
    schedule_test_execution
)

from app.tasks.report_generation import (
    generate_test_report,
    generate_trend_report
)

from app.tasks.system_maintenance import (
    cleanup_system_data,
    backup_system_data,
    system_health_check
)

__all__ = [
    # 测试执行任务
    "execute_single_test",
    "execute_batch_tests", 
    "execute_test_suite",
    "schedule_test_execution",
    
    # 报告生成任务
    "generate_test_report",
    "generate_trend_report",
    
    # 系统维护任务
    "cleanup_system_data",
    "backup_system_data",
    "system_health_check",
]
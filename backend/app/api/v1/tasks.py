"""
任务管理API路由

提供异步任务的提交、查询、管理接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from celery.result import AsyncResult

from app.models.user import User
from app.core.celery_app import celery_app
from app.tasks import (
    execute_single_test,
    execute_batch_tests,
    execute_test_suite,
    generate_test_report,
    generate_trend_report,
    cleanup_system_data,
    backup_system_data,
    system_health_check
)
from app.utils.auth import get_current_user, require_permission
from app.utils.response import success_response, error_response
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()


# 请求模型
class SingleTestRequest(BaseModel):
    test_case_id: int
    environment_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None


class BatchTestRequest(BaseModel):
    test_case_ids: List[int]
    environment_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    parallel: bool = False


class TestSuiteRequest(BaseModel):
    test_suite_id: int
    environment_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None


class ReportRequest(BaseModel):
    execution_results: List[Dict[str, Any]]
    report_type: str = "html"  # html, json, pdf, excel
    report_config: Optional[Dict[str, Any]] = None


class TrendReportRequest(BaseModel):
    date_range: Dict[str, str]  # {"start_date": "2024-01-01", "end_date": "2024-01-31"}
    test_case_ids: Optional[List[int]] = None
    environment_ids: Optional[List[int]] = None


class CleanupRequest(BaseModel):
    temp_var_max_age: int = 24  # 小时
    report_max_age: int = 30  # 天
    log_max_age: int = 7  # 天
    cache_max_age: int = 48  # 小时


class BackupRequest(BaseModel):
    backup_path: str = "/tmp/backups"
    backup_database: bool = True
    backup_config: bool = True
    backup_uploads: bool = True
    compress: bool = True


# 测试执行任务接口

@router.post("/execute/single", response_model=dict)
async def submit_single_test(
    request: SingleTestRequest,
    current_user: User = Depends(get_current_user)
):
    """提交单个测试执行任务"""
    try:
        task = execute_single_test.delay(
            test_case_id=request.test_case_id,
            environment_id=request.environment_id,
            variables=request.variables,
            user_id=current_user.id
        )
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "单个测试任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交单个测试任务失败: {str(e)}")
        return error_response("提交测试任务失败")


@router.post("/execute/batch", response_model=dict)
async def submit_batch_tests(
    request: BatchTestRequest,
    current_user: User = Depends(get_current_user)
):
    """提交批量测试执行任务"""
    try:
        if not request.test_case_ids:
            return error_response("测试用例ID列表不能为空")
        
        task = execute_batch_tests.delay(
            test_case_ids=request.test_case_ids,
            environment_id=request.environment_id,
            variables=request.variables,
            user_id=current_user.id,
            parallel=request.parallel
        )
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "test_count": len(request.test_case_ids),
            "execution_mode": "parallel" if request.parallel else "sequential",
            "message": "批量测试任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交批量测试任务失败: {str(e)}")
        return error_response("提交批量测试任务失败")


@router.post("/execute/suite", response_model=dict)
async def submit_test_suite(
    request: TestSuiteRequest,
    current_user: User = Depends(get_current_user)
):
    """提交测试套件执行任务"""
    try:
        task = execute_test_suite.delay(
            test_suite_id=request.test_suite_id,
            environment_id=request.environment_id,
            variables=request.variables,
            user_id=current_user.id
        )
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "测试套件任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交测试套件任务失败: {str(e)}")
        return error_response("提交测试套件任务失败")


# 报告生成任务接口

@router.post("/report/generate", response_model=dict)
async def submit_report_generation(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """提交测试报告生成任务"""
    try:
        if not request.execution_results:
            return error_response("执行结果不能为空")
        
        task = generate_test_report.delay(
            execution_results=request.execution_results,
            report_type=request.report_type,
            report_config=request.report_config
        )
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "report_type": request.report_type,
            "message": "报告生成任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交报告生成任务失败: {str(e)}")
        return error_response("提交报告生成任务失败")


@router.post("/report/trend", response_model=dict)
async def submit_trend_report(
    request: TrendReportRequest,
    current_user: User = Depends(get_current_user)
):
    """提交趋势报告生成任务"""
    try:
        task = generate_trend_report.delay(
            date_range=request.date_range,
            test_case_ids=request.test_case_ids,
            environment_ids=request.environment_ids
        )
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "趋势报告任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交趋势报告任务失败: {str(e)}")
        return error_response("提交趋势报告任务失败")


# 系统维护任务接口

@router.post("/maintenance/cleanup", response_model=dict)
async def submit_system_cleanup(
    request: CleanupRequest,
    current_user: User = Depends(require_permission("system:maintenance"))
):
    """提交系统清理任务"""
    try:
        cleanup_config = {
            "temp_var_max_age": request.temp_var_max_age,
            "report_max_age": request.report_max_age,
            "log_max_age": request.log_max_age,
            "cache_max_age": request.cache_max_age
        }
        
        task = cleanup_system_data.delay(cleanup_config=cleanup_config)
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "系统清理任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交系统清理任务失败: {str(e)}")
        return error_response("提交系统清理任务失败")


@router.post("/maintenance/backup", response_model=dict)
async def submit_system_backup(
    request: BackupRequest,
    current_user: User = Depends(require_permission("system:maintenance"))
):
    """提交系统备份任务"""
    try:
        backup_config = {
            "backup_path": request.backup_path,
            "backup_database": request.backup_database,
            "backup_config": request.backup_config,
            "backup_uploads": request.backup_uploads,
            "compress": request.compress
        }
        
        task = backup_system_data.delay(backup_config=backup_config)
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "系统备份任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交系统备份任务失败: {str(e)}")
        return error_response("提交系统备份任务失败")


@router.post("/maintenance/health-check", response_model=dict)
async def submit_health_check(
    current_user: User = Depends(require_permission("system:maintenance"))
):
    """提交系统健康检查任务"""
    try:
        task = system_health_check.delay()
        
        return success_response({
            "task_id": task.id,
            "status": "submitted",
            "message": "健康检查任务已提交"
        })
        
    except Exception as e:
        logger.error(f"提交健康检查任务失败: {str(e)}")
        return error_response("提交健康检查任务失败")


# 任务查询和管理接口

@router.get("/status/{task_id}", response_model=dict)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取任务状态"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        response_data = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "info": result.info
        }
        
        if result.status == "PENDING":
            response_data["message"] = "任务等待执行"
        elif result.status == "STARTED":
            response_data["message"] = "任务正在执行"
        elif result.status == "SUCCESS":
            response_data["message"] = "任务执行成功"
        elif result.status == "FAILURE":
            response_data["message"] = "任务执行失败"
            response_data["error"] = str(result.info)
        elif result.status == "RETRY":
            response_data["message"] = "任务重试中"
        elif result.status == "REVOKED":
            response_data["message"] = "任务已取消"
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return error_response("获取任务状态失败")


@router.get("/result/{task_id}", response_model=dict)
async def get_task_result(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取任务执行结果"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.status == "SUCCESS":
            return success_response({
                "task_id": task_id,
                "status": result.status,
                "result": result.result
            })
        elif result.status == "FAILURE":
            return error_response(f"任务执行失败: {str(result.info)}")
        else:
            return success_response({
                "task_id": task_id,
                "status": result.status,
                "message": "任务尚未完成"
            })
        
    except Exception as e:
        logger.error(f"获取任务结果失败: {str(e)}")
        return error_response("获取任务结果失败")


@router.delete("/cancel/{task_id}", response_model=dict)
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """取消任务"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        return success_response({
            "task_id": task_id,
            "message": "任务取消请求已发送"
        })
        
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        return error_response("取消任务失败")


@router.get("/active", response_model=dict)
async def get_active_tasks(
    current_user: User = Depends(require_permission("system:monitoring"))
):
    """获取活跃任务列表"""
    try:
        # 获取活跃任务
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            active_tasks = {}
        
        # 统计任务数量
        total_active = sum(len(tasks) for tasks in active_tasks.values())
        
        return success_response({
            "total_active": total_active,
            "active_tasks": active_tasks
        })
        
    except Exception as e:
        logger.error(f"获取活跃任务失败: {str(e)}")
        return error_response("获取活跃任务失败")


@router.get("/stats", response_model=dict)
async def get_task_stats(
    current_user: User = Depends(require_permission("system:monitoring"))
):
    """获取任务统计信息"""
    try:
        inspect = celery_app.control.inspect()
        
        # 获取各种任务状态
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        
        # 统计数量
        stats = {
            "active_tasks": sum(len(tasks) for tasks in active.values()),
            "scheduled_tasks": sum(len(tasks) for tasks in scheduled.values()),
            "reserved_tasks": sum(len(tasks) for tasks in reserved.values()),
            "worker_count": len(active.keys())
        }
        
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"获取任务统计失败: {str(e)}")
        return error_response("获取任务统计失败")
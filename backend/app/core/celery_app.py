"""
Celery异步任务配置

配置Celery任务队列系统
"""

from celery import Celery
from app.core.config import settings
from loguru import logger

# 创建Celery应用实例
celery_app = Celery(
    "twodreamer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.test_execution",
        "app.tasks.report_generation",
        "app.tasks.system_maintenance"
    ]
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    
    # 结果配置
    result_expires=3600,  # 结果保留1小时
    
    # 任务路由配置
    task_routes={
        "app.tasks.test_execution.*": {"queue": "test_execution"},
        "app.tasks.report_generation.*": {"queue": "report_generation"},
        "app.tasks.system_maintenance.*": {"queue": "system_maintenance"},
    },
    
    # 队列配置
    task_default_queue="default",
    task_default_exchange="default",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
    
    # 日志配置
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 任务状态常量
class TaskStatus:
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f"Request: {self.request!r}")
    return "Celery is working!"


# Celery事件监听器
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """设置定期任务"""
    # 每天凌晨2点清理过期的临时变量
    sender.add_periodic_task(
        3600.0 * 24,  # 24小时
        cleanup_temporary_variables.s(),
        name="cleanup temporary variables daily"
    )
    
    # 每小时清理过期的测试报告
    sender.add_periodic_task(
        3600.0,  # 1小时
        cleanup_expired_reports.s(),
        name="cleanup expired reports hourly"
    )


# 导入任务模块（避免循环导入）
def import_tasks():
    """导入所有任务模块"""
    try:
        from app.tasks import test_execution
        from app.tasks import report_generation
        from app.tasks import system_maintenance
        logger.info("Celery任务模块导入成功")
    except Exception as e:
        logger.error(f"Celery任务模块导入失败: {e}")


# 启动时导入任务
import_tasks()


# 延迟导入的任务（避免循环导入）
@celery_app.task
def cleanup_temporary_variables():
    """清理过期临时变量的任务"""
    from app.services.variable_service import VariableService
    import asyncio
    
    async def cleanup():
        return await VariableService.cleanup_temporary_variables()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(cleanup())
        return {"cleaned_count": result}
    finally:
        loop.close()


@celery_app.task
def cleanup_expired_reports():
    """清理过期测试报告的任务"""
    from app.services.report_service import ReportService
    import asyncio
    
    async def cleanup():
        return await ReportService.cleanup_expired_reports()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(cleanup())
        return {"cleaned_count": result}
    finally:
        loop.close()


if __name__ == "__main__":
    celery_app.start()
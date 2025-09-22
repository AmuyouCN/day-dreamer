"""
Celery异步任务配置模块

配置Celery实例和任务调度
"""

from celery import Celery
from app.core.config import settings

# 创建Celery实例
celery_app = Celery(
    "test_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# 配置Celery
celery_app.conf.update(settings.celery_config)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
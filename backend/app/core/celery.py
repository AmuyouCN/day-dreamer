"""
Celery异步任务配置模块

配置Celery实例和任务调度
"""

from celery import Celery
from app.core.config import settings

# 创建Celery实例
celery_app = Celery(
    "test_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# 配置Celery
celery_app.conf.update(settings.CELERY_CONFIG)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
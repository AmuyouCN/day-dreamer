#!/usr/bin/env python3
"""
Celery启动脚本

用于启动Celery Worker
"""

import os
from celery import Celery
from app.core.config import settings

os.environ.setdefault('CELERY_CONFIG_MODULE', 'app.core.celery')

celery_app = Celery('test_platform')
celery_app.config_from_object(settings.celery_config)
celery_app.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    celery_app.start()
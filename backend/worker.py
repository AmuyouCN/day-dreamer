#!/usr/bin/env python3
"""
Celery Worker启动脚本

启动Celery Worker进程处理异步任务
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # 启动Celery Worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--queues=default,test_execution,report_generation,system_maintenance"
    ])
#!/usr/bin/env python3
"""
统一的Celery应用启动和管理脚本
"""

import os
import sys
import argparse
from typing import List, Optional
from celery import Celery
from app.core.config import settings

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_celery_app() -> Celery:
    """创建Celery应用实例"""
    celery_app = Celery(
        "twodreamer",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
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
    
    return celery_app

def start_worker(celery_app: Celery, args: Optional[List[str]] = None):
    """启动Celery Worker"""
    worker_args = [
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--queues=default,test_execution,report_generation,system_maintenance"
    ]
    
    if args:
        worker_args.extend(args)
    
    print("🚀 启动Celery Worker...")
    print(f"📊 队列: default, test_execution, report_generation, system_maintenance")
    print(f"⚡ 并发数: 4")
    print(f"📝 日志级别: info")
    print("=" * 60)
    
    celery_app.worker_main(worker_args)

def start_beat(celery_app: Celery):
    """启动Celery Beat（定时任务调度器）"""
    print("⏰ 启动Celery Beat定时任务调度器...")
    print("=" * 60)
    
    celery_app.start(["beat"])

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Celery应用管理")
    parser.add_argument(
        "mode", 
        choices=["worker", "beat", "shell"], 
        nargs="?", 
        default="worker",
        help="运行模式: worker(默认), beat, shell"
    )
    parser.add_argument(
        "--concurrency", 
        "-c", 
        type=int, 
        default=4,
        help="Worker并发数 (默认: 4)"
    )
    parser.add_argument(
        "--loglevel", 
        "-l", 
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="日志级别 (默认: info)"
    )
    parser.add_argument(
        "--queues", 
        "-q", 
        default="default,test_execution,report_generation,system_maintenance",
        help="监听的队列 (默认: 所有队列)"
    )
    
    args, unknown_args = parser.parse_known_args()
    
    # 创建Celery应用
    celery_app = create_celery_app()
    
    if args.mode == "worker":
        worker_args = [
            "worker",
            f"--loglevel={args.loglevel}",
            f"--concurrency={args.concurrency}",
            f"--queues={args.queues}"
        ]
        worker_args.extend(unknown_args)
        start_worker(celery_app, worker_args)
    elif args.mode == "beat":
        start_beat(celery_app)
    elif args.mode == "shell":
        print("🐚 启动Celery Shell...")
        celery_app.start(["shell"])

if __name__ == "__main__":
    main()
"""
日志配置模块

基于 loguru 的日志配置和管理
"""

import sys
from pathlib import Path
from loguru import logger as loguru_logger
from app.core.config import settings

_initialized = False


class Logging:
    @classmethod
    def setup_logger(cls):
        global _initialized
        if _initialized:
            return loguru_logger

        loguru_logger.remove()

        # 获取日志目录
        logs_dir = Path(settings.LOG_DIR)
        logs_dir.mkdir(parents=True, exist_ok=True)

        if settings.DEBUG:
            loguru_logger.add(sink=sys.stdout, level="DEBUG")

        loguru_logger.add(
            logs_dir / 'be_debug.log',
            rotation='20 MB',
            encoding='utf-8',
            level='DEBUG',
            enqueue=True,
            compression="zip",
            # serialize=True,
        )
        loguru_logger.add(
            logs_dir / 'be_info.log',
            rotation='10 MB',
            encoding='utf-8',
            level='INFO',
            enqueue=True,
            compression="zip",
            # serialize=True,
        )
        loguru_logger.add(
            logs_dir / 'be_error.log',
            rotation='5 MB',
            encoding='utf-8',
            level='ERROR',
            enqueue=True,
            compression="zip",
            backtrace=True,
            # serialize=True,
        )
        loguru_logger.add(
            logs_dir / 'be_buffer.log',
            retention='3 day',
            enqueue=True,
            catch=True,
            level='DEBUG',
            # serialize=True,
        )

        _initialized = True
        loguru_logger.info("日志系统初始化完成")
        return loguru_logger


logger = Logging.setup_logger()
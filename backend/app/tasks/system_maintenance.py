"""
系统维护异步任务

处理系统清理、备份、监控等维护任务
"""

import asyncio
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Task

from app.core.celery_app import celery_app, TaskStatus
from app.services.variable_service import VariableService
from app.utils.logger import logger


class AsyncSystemMaintenanceTask(Task):
    """异步系统维护任务基类"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功完成时的回调"""
        logger.info(f"系统维护任务完成: {task_id}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"系统维护任务失败: {task_id} - {str(exc)}")


@celery_app.task(bind=True, base=AsyncSystemMaintenanceTask, name="cleanup_system_data")
def cleanup_system_data(
    self,
    cleanup_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """系统数据清理任务
    
    Args:
        cleanup_config: 清理配置
    
    Returns:
        清理结果
    """
    
    async def cleanup():
        try:
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始系统数据清理"}
            )
            
            cleanup_results = {}
            
            # 清理过期临时变量
            temp_var_count = await VariableService.cleanup_temporary_variables(
                max_age_hours=cleanup_config.get("temp_var_max_age", 24)
            )
            cleanup_results["temporary_variables"] = temp_var_count
            
            # 清理过期测试报告
            report_count = await cleanup_expired_reports(
                max_age_days=cleanup_config.get("report_max_age", 30)
            )
            cleanup_results["test_reports"] = report_count
            
            # 清理日志文件
            log_count = await cleanup_log_files(
                max_age_days=cleanup_config.get("log_max_age", 7)
            )
            cleanup_results["log_files"] = log_count
            
            # 清理缓存数据
            cache_count = await cleanup_cache_data(
                max_age_hours=cleanup_config.get("cache_max_age", 48)
            )
            cleanup_results["cache_data"] = cache_count
            
            return {
                "status": "success",
                "cleanup_results": cleanup_results,
                "total_cleaned": sum(cleanup_results.values())
            }
            
        except Exception as e:
            logger.error(f"系统数据清理失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(cleanup())
    finally:
        loop.close()


@celery_app.task(bind=True, base=AsyncSystemMaintenanceTask, name="backup_system_data")
def backup_system_data(
    self,
    backup_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """系统数据备份任务
    
    Args:
        backup_config: 备份配置
    
    Returns:
        备份结果
    """
    
    async def backup():
        try:
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始系统数据备份"}
            )
            
            backup_results = {}
            backup_path = backup_config.get("backup_path", "/tmp/backups")
            
            # 创建备份目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(backup_path, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份数据库
            if backup_config.get("backup_database", True):
                db_backup_result = await backup_database(backup_dir)
                backup_results["database"] = db_backup_result
            
            # 备份配置文件
            if backup_config.get("backup_config", True):
                config_backup_result = await backup_config_files(backup_dir)
                backup_results["config_files"] = config_backup_result
            
            # 备份上传文件
            if backup_config.get("backup_uploads", True):
                upload_backup_result = await backup_upload_files(backup_dir)
                backup_results["upload_files"] = upload_backup_result
            
            # 压缩备份文件
            if backup_config.get("compress", True):
                compressed_file = await compress_backup(backup_dir)
                backup_results["compressed_file"] = compressed_file
                
                # 删除原始备份目录
                shutil.rmtree(backup_dir)
            
            return {
                "status": "success",
                "backup_path": backup_dir,
                "backup_results": backup_results
            }
            
        except Exception as e:
            logger.error(f"系统数据备份失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(backup())
    finally:
        loop.close()


@celery_app.task(bind=True, base=AsyncSystemMaintenanceTask, name="system_health_check")
def system_health_check(self) -> Dict[str, Any]:
    """系统健康检查任务
    
    Returns:
        健康检查结果
    """
    
    async def health_check():
        try:
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始系统健康检查"}
            )
            
            health_results = {}
            
            # 检查数据库连接
            db_health = await check_database_health()
            health_results["database"] = db_health
            
            # 检查Redis连接
            redis_health = await check_redis_health()
            health_results["redis"] = redis_health
            
            # 检查磁盘空间
            disk_health = await check_disk_space()
            health_results["disk_space"] = disk_health
            
            # 检查内存使用
            memory_health = await check_memory_usage()
            health_results["memory"] = memory_health
            
            # 检查API响应
            api_health = await check_api_health()
            health_results["api"] = api_health
            
            # 总体健康状态
            overall_status = "healthy"
            for component, status in health_results.items():
                if status.get("status") != "healthy":
                    overall_status = "unhealthy"
                    break
            
            return {
                "status": "success",
                "overall_status": overall_status,
                "components": health_results,
                "check_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"系统健康检查失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(health_check())
    finally:
        loop.close()


async def cleanup_expired_reports(max_age_days: int = 30) -> int:
    """清理过期测试报告"""
    try:
        # 这里应该从数据库删除过期报告
        # 为简化示例，返回模拟数据
        return 0
    except Exception as e:
        logger.error(f"清理过期报告失败: {str(e)}")
        return 0


async def cleanup_log_files(max_age_days: int = 7) -> int:
    """清理过期日志文件"""
    try:
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        for filename in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    cleaned_count += 1
        
        logger.info(f"清理了 {cleaned_count} 个过期日志文件")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"清理日志文件失败: {str(e)}")
        return 0


async def cleanup_cache_data(max_age_hours: int = 48) -> int:
    """清理过期缓存数据"""
    try:
        from app.core.redis import get_redis
        
        redis = get_redis()
        if not redis:
            return 0
        
        # 这里应该实现缓存清理逻辑
        # 为简化示例，返回模拟数据
        return 0
        
    except Exception as e:
        logger.error(f"清理缓存数据失败: {str(e)}")
        return 0


async def backup_database(backup_dir: str) -> Dict[str, Any]:
    """备份数据库"""
    try:
        # 这里应该实现数据库备份逻辑
        # 使用mysqldump或其他工具
        backup_file = os.path.join(backup_dir, "database.sql")
        
        # 模拟备份
        with open(backup_file, 'w') as f:
            f.write("-- Database backup placeholder\n")
        
        return {
            "status": "success",
            "file": backup_file,
            "size": os.path.getsize(backup_file)
        }
        
    except Exception as e:
        logger.error(f"数据库备份失败: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }


async def backup_config_files(backup_dir: str) -> Dict[str, Any]:
    """备份配置文件"""
    try:
        config_backup_dir = os.path.join(backup_dir, "config")
        os.makedirs(config_backup_dir, exist_ok=True)
        
        # 备份主要配置文件
        config_files = [
            "app/core/config.py",
            "requirements.txt",
            "docker-compose.yml"
        ]
        
        backed_up_files = []
        for config_file in config_files:
            if os.path.exists(config_file):
                shutil.copy2(config_file, config_backup_dir)
                backed_up_files.append(config_file)
        
        return {
            "status": "success",
            "files": backed_up_files,
            "count": len(backed_up_files)
        }
        
    except Exception as e:
        logger.error(f"配置文件备份失败: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }


async def backup_upload_files(backup_dir: str) -> Dict[str, Any]:
    """备份上传文件"""
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            return {
                "status": "success",
                "message": "无上传文件需要备份"
            }
        
        upload_backup_dir = os.path.join(backup_dir, "uploads")
        shutil.copytree(upload_dir, upload_backup_dir)
        
        # 计算文件数量和大小
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(upload_backup_dir):
            file_count += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        
        return {
            "status": "success",
            "file_count": file_count,
            "total_size": total_size
        }
        
    except Exception as e:
        logger.error(f"上传文件备份失败: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }


async def compress_backup(backup_dir: str) -> str:
    """压缩备份文件"""
    try:
        compressed_file = f"{backup_dir}.tar.gz"
        shutil.make_archive(backup_dir, 'gztar', backup_dir)
        return compressed_file
        
    except Exception as e:
        logger.error(f"备份压缩失败: {str(e)}")
        return ""


async def check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    try:
        from tortoise import Tortoise
        
        # 简单的数据库连接测试
        connections = Tortoise.get_connection("default")
        if connections:
            return {
                "status": "healthy",
                "message": "数据库连接正常"
            }
        else:
            return {
                "status": "unhealthy",
                "message": "数据库连接失败"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"数据库检查失败: {str(e)}"
        }


async def check_redis_health() -> Dict[str, Any]:
    """检查Redis健康状态"""
    try:
        from app.core.redis import get_redis
        
        redis = get_redis()
        if redis and await redis.ping():
            return {
                "status": "healthy",
                "message": "Redis连接正常"
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Redis连接失败"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Redis检查失败: {str(e)}"
        }


async def check_disk_space() -> Dict[str, Any]:
    """检查磁盘空间"""
    try:
        import psutil
        
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent > 20:
            status = "healthy"
        elif free_percent > 10:
            status = "warning"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "free_percent": round(free_percent, 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "total_gb": round(disk_usage.total / (1024**3), 2)
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "message": f"磁盘空间检查失败: {str(e)}"
        }


async def check_memory_usage() -> Dict[str, Any]:
    """检查内存使用情况"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        used_percent = memory.percent
        
        if used_percent < 80:
            status = "healthy"
        elif used_percent < 90:
            status = "warning"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "used_percent": used_percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2)
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "message": f"内存检查失败: {str(e)}"
        }


async def check_api_health() -> Dict[str, Any]:
    """检查API健康状态"""
    try:
        import httpx
        
        # 检查本地API健康端点
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "message": "API响应异常"
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"API检查失败: {str(e)}"
        }
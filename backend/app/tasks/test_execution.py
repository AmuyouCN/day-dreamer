"""
测试执行异步任务

处理单个和批量测试用例的异步执行
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from celery import Task

from app.core.celery_app import celery_app, TaskStatus
from app.models.test_case import TestCase
from app.models.environment import Environment
from app.services.test_execution_service import TestExecutionService
from app.services.variable_service import VariableService
from app.utils.logger import logger


class AsyncTestExecutionTask(Task):
    """异步测试执行任务基类"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功完成时的回调"""
        logger.info(f"测试执行任务完成: {task_id}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"测试执行任务失败: {task_id} - {str(exc)}")


@celery_app.task(bind=True, base=AsyncTestExecutionTask, name="execute_single_test")
def execute_single_test(
    self,
    test_case_id: int,
    environment_id: Optional[int] = None,
    variables: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """执行单个测试用例
    
    Args:
        test_case_id: 测试用例ID
        environment_id: 环境ID
        variables: 临时变量
        user_id: 执行用户ID
    
    Returns:
        测试执行结果
    """
    
    async def run_test():
        try:
            # 更新任务状态
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始执行测试用例", "test_case_id": test_case_id}
            )
            
            # 获取测试用例
            test_case = await TestCase.get(id=test_case_id, is_active=True)
            if not test_case:
                raise ValueError(f"测试用例 {test_case_id} 不存在")
            
            # 获取环境信息
            environment = None
            if environment_id:
                environment = await Environment.get(id=environment_id, is_active=True)
            
            # 生成会话ID用于临时变量
            session_id = f"task_{self.request.id}_{datetime.now().timestamp()}"
            
            # 创建临时变量
            if variables:
                for name, value in variables.items():
                    await VariableService.create_variable(
                        name=name,
                        value=str(value),
                        scope="temporary",
                        created_by=user_id or 0,
                        session_id=session_id
                    )
            
            # 执行测试
            result = await TestExecutionService.execute_test_case(
                test_case=test_case,
                environment=environment,
                user_id=user_id,
                session_id=session_id
            )
            
            # 清理临时变量
            if variables:
                await VariableService.cleanup_temporary_variables()
            
            return {
                "status": "success",
                "test_case_id": test_case_id,
                "environment_id": environment_id,
                "execution_time": result.get("execution_time"),
                "response_time": result.get("response_time"),
                "status_code": result.get("status_code"),
                "assertions_passed": result.get("assertions_passed"),
                "assertions_failed": result.get("assertions_failed"),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            return {
                "status": "failed",
                "test_case_id": test_case_id,
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_test())
    finally:
        loop.close()


@celery_app.task(bind=True, base=AsyncTestExecutionTask, name="execute_batch_tests")
def execute_batch_tests(
    self,
    test_case_ids: List[int],
    environment_id: Optional[int] = None,
    variables: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    parallel: bool = False
) -> Dict[str, Any]:
    """批量执行测试用例
    
    Args:
        test_case_ids: 测试用例ID列表
        environment_id: 环境ID
        variables: 全局临时变量
        user_id: 执行用户ID
        parallel: 是否并行执行
    
    Returns:
        批量测试执行结果
    """
    
    async def run_batch_tests():
        try:
            total_count = len(test_case_ids)
            self.update_state(
                state=TaskStatus.STARTED,
                meta={
                    "message": "开始批量执行测试用例",
                    "total_count": total_count,
                    "completed_count": 0
                }
            )
            
            results = []
            success_count = 0
            failed_count = 0
            
            # 生成会话ID
            session_id = f"batch_{self.request.id}_{datetime.now().timestamp()}"
            
            # 创建全局临时变量
            if variables:
                for name, value in variables.items():
                    await VariableService.create_variable(
                        name=name,
                        value=str(value),
                        scope="temporary",
                        created_by=user_id or 0,
                        session_id=session_id
                    )
            
            if parallel:
                # 并行执行
                tasks = []
                for test_case_id in test_case_ids:
                    task = execute_single_test_async(
                        test_case_id, environment_id, None, user_id, session_id
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        failed_count += 1
                    elif result.get("status") == "success":
                        success_count += 1
                    else:
                        failed_count += 1
            else:
                # 串行执行
                for i, test_case_id in enumerate(test_case_ids):
                    try:
                        result = await execute_single_test_async(
                            test_case_id, environment_id, None, user_id, session_id
                        )
                        results.append(result)
                        
                        if result.get("status") == "success":
                            success_count += 1
                        else:
                            failed_count += 1
                        
                        # 更新进度
                        self.update_state(
                            state=TaskStatus.STARTED,
                            meta={
                                "message": f"已完成 {i + 1}/{total_count} 个测试用例",
                                "total_count": total_count,
                                "completed_count": i + 1,
                                "success_count": success_count,
                                "failed_count": failed_count
                            }
                        )
                        
                    except Exception as e:
                        failed_count += 1
                        results.append({
                            "status": "failed",
                            "test_case_id": test_case_id,
                            "error": str(e)
                        })
            
            # 清理临时变量
            if variables:
                await VariableService.cleanup_temporary_variables()
            
            return {
                "status": "completed",
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "execution_mode": "parallel" if parallel else "sequential",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"批量测试执行失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_batch_tests())
    finally:
        loop.close()


async def execute_single_test_async(
    test_case_id: int,
    environment_id: Optional[int] = None,
    variables: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """异步执行单个测试用例（内部函数）"""
    
    try:
        test_case = await TestCase.get(id=test_case_id, is_active=True)
        if not test_case:
            raise ValueError(f"测试用例 {test_case_id} 不存在")
        
        environment = None
        if environment_id:
            environment = await Environment.get(id=environment_id, is_active=True)
        
        result = await TestExecutionService.execute_test_case(
            test_case=test_case,
            environment=environment,
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "status": "success",
            "test_case_id": test_case_id,
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "test_case_id": test_case_id,
            "error": str(e)
        }


@celery_app.task(bind=True, name="execute_test_suite")
def execute_test_suite(
    self,
    test_suite_id: int,
    environment_id: Optional[int] = None,
    variables: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """执行测试套件
    
    Args:
        test_suite_id: 测试套件ID
        environment_id: 环境ID
        variables: 临时变量
        user_id: 执行用户ID
    
    Returns:
        测试套件执行结果
    """
    
    async def run_test_suite():
        try:
            # 获取测试套件下的所有测试用例
            test_cases = await TestCase.filter(
                suite_id=test_suite_id,
                is_active=True
            ).order_by("sort_order")
            
            if not test_cases:
                return {
                    "status": "failed",
                    "error": "测试套件为空或不存在"
                }
            
            test_case_ids = [tc.id for tc in test_cases]
            
            # 调用批量执行
            return await execute_batch_tests.apply_async(
                args=[test_case_ids, environment_id, variables, user_id, False]
            ).get()
            
        except Exception as e:
            logger.error(f"测试套件执行失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_test_suite())
    finally:
        loop.close()


@celery_app.task(name="schedule_test_execution")
def schedule_test_execution(
    schedule_config: Dict[str, Any]
) -> Dict[str, Any]:
    """定时执行测试任务
    
    Args:
        schedule_config: 定时配置信息
    
    Returns:
        执行结果
    """
    
    try:
        test_case_ids = schedule_config.get("test_case_ids", [])
        environment_id = schedule_config.get("environment_id")
        variables = schedule_config.get("variables", {})
        user_id = schedule_config.get("user_id")
        parallel = schedule_config.get("parallel", False)
        
        if not test_case_ids:
            return {
                "status": "failed",
                "error": "未指定测试用例"
            }
        
        # 执行批量测试
        result = execute_batch_tests.delay(
            test_case_ids=test_case_ids,
            environment_id=environment_id,
            variables=variables,
            user_id=user_id,
            parallel=parallel
        )
        
        return {
            "status": "scheduled",
            "task_id": result.id,
            "message": "定时测试任务已提交"
        }
        
    except Exception as e:
        logger.error(f"定时测试执行失败: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }
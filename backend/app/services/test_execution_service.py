"""
测试执行服务

处理测试用例的执行逻辑
"""

import time
from typing import Dict, Any, Optional
from loguru import logger

from app.models.test_case import TestCase
from app.models.environment import Environment
from app.models.test_execution import TestExecution, TestResult, ExecutionType, ExecutionStatus, TestResultStatus
from app.utils.http_client import HttpClient
from app.utils.variable_resolver import VariableResolver
from app.utils.assertion_validator import AssertionValidator


class TestExecutionService:
    """测试执行服务类"""
    
    def __init__(self):
        self.variable_resolver = VariableResolver()
        self.assertion_validator = AssertionValidator()
    
    async def execute_single_test_case(
        self,
        test_case: TestCase,
        environment: Environment,
        variables: Optional[Dict[str, str]] = None,
        save_result: bool = True,
        executor_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行单个测试用例"""
        
        start_time = time.time()
        execution_id = None
        
        try:
            # 创建执行记录
            if save_result:
                execution = TestExecution(
                    execution_type=ExecutionType.SINGLE,
                    target_id=test_case.id,
                    executor_id=executor_id,
                    environment_id=environment.id,
                    status=ExecutionStatus.RUNNING,
                    started_at=time.time(),
                    execution_config={
                        "test_case_id": test_case.id,
                        "environment_id": environment.id,
                        "variables": variables or {}
                    }
                )
                await execution.save()
                execution_id = execution.id
            
            # 获取关联的接口定义
            api = await test_case.api
            
            # 解析变量
            resolved_request_data = await self.variable_resolver.resolve_variables(
                test_case.request_data,
                user_id=executor_id,
                environment_id=environment.id,
                temp_variables=variables
            )
            
            # 构建请求
            base_url = environment.get_base_url()
            full_url = api.get_full_url(base_url)
            
            # 合并请求头
            headers = {}
            headers.update(environment.get_headers())
            headers.update(api.headers)
            headers.update(resolved_request_data.get("headers", {}))
            
            # 合并查询参数
            query_params = {}
            query_params.update(api.query_params)
            query_params.update(resolved_request_data.get("query_params", {}))
            
            # 请求体
            body = resolved_request_data.get("body")
            
            # 执行HTTP请求
            http_client = HttpClient()
            
            logger.info(f"开始执行测试用例: {test_case.name} (ID: {test_case.id})")
            
            http_result = await http_client.request(
                method=api.method,
                url=full_url,
                headers=headers,
                params=query_params,
                json=body if body else None
            )
            
            # 执行断言验证
            assertion_results = await self.assertion_validator.validate_all_assertions(
                assertions=test_case.assertions,
                response_data=http_result,
                response_time=http_result["response_time"]
            )
            
            # 确定测试状态
            if assertion_results["all_passed"]:
                test_status = TestResultStatus.PASS
            else:
                test_status = TestResultStatus.FAIL
            
            duration = (time.time() - start_time) * 1000  # 毫秒
            
            # 构建结果
            result = {
                "status": test_status,
                "duration": round(duration, 2),
                "request_data": {
                    "url": full_url,
                    "method": api.method,
                    "headers": headers,
                    "params": query_params,
                    "body": body
                },
                "response_data": http_result,
                "assertion_results": assertion_results["results"],
                "assertion_summary": {
                    "total": assertion_results["total"],
                    "passed": assertion_results["passed"],
                    "failed": assertion_results["failed"],
                    "pass_rate": assertion_results["pass_rate"]
                }
            }
            
            # 保存测试结果
            if save_result and execution_id:
                test_result = TestResult(
                    execution_id=execution_id,
                    test_case_id=test_case.id,
                    status=test_status,
                    request_data=result["request_data"],
                    response_data=http_result,
                    assertion_results=assertion_results["results"],
                    duration=duration
                )
                await test_result.save()
                
                # 更新执行状态
                execution.status = ExecutionStatus.COMPLETED
                execution.finished_at = time.time()
                await execution.save(update_fields=["status", "finished_at"])
            
            logger.info(
                f"测试用例执行完成: {test_case.name} - 状态: {test_status} - "
                f"耗时: {duration:.2f}ms - 断言: {assertion_results['passed']}/{assertion_results['total']}"
            )
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_message = str(e)
            
            logger.error(f"测试用例执行失败: {test_case.name} - {error_message}")
            
            # 保存错误结果
            if save_result and execution_id:
                test_result = TestResult(
                    execution_id=execution_id,
                    test_case_id=test_case.id,
                    status=TestResultStatus.ERROR,
                    request_data={},
                    response_data={},
                    assertion_results=[],
                    duration=duration,
                    error_message=error_message
                )
                await test_result.save()
                
                # 更新执行状态
                execution.status = ExecutionStatus.FAILED
                execution.finished_at = time.time()
                await execution.save(update_fields=["status", "finished_at"])
            
            return {
                "status": TestResultStatus.ERROR,
                "duration": round(duration, 2),
                "request_data": {},
                "response_data": {},
                "assertion_results": [],
                "error_message": error_message
            }
    
    async def prepare_test_environment(
        self,
        test_case: TestCase,
        environment: Environment,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """准备测试环境（验证变量等）"""
        
        try:
            # 验证环境配置
            if not environment.is_active:
                raise ValueError(f"环境未激活: {environment.name}")
            
            base_url = environment.get_base_url()
            if not base_url:
                raise ValueError(f"环境未配置base_url: {environment.name}")
            
            # 获取可用变量
            available_variables = await self.variable_resolver._get_available_variables(
                user_id=test_case.creator_id,
                environment_id=environment.id,
                temp_variables=variables
            )
            
            # 验证测试数据中的变量
            variable_validation = self.variable_resolver.validate_variables(
                test_case.request_data,
                available_variables
            )
            
            # 获取关联的接口定义
            api = await test_case.api
            
            return {
                "environment": {
                    "id": environment.id,
                    "name": environment.name,
                    "base_url": base_url,
                    "is_active": environment.is_active
                },
                "api": {
                    "id": api.id,
                    "name": api.name,
                    "method": api.method,
                    "url": api.url
                },
                "variables": {
                    "available_count": len(available_variables),
                    "validation": variable_validation
                },
                "test_case": {
                    "id": test_case.id,
                    "name": test_case.name,
                    "assertions_count": len(test_case.assertions)
                },
                "ready": variable_validation["is_valid"]
            }
            
        except Exception as e:
            logger.error(f"测试环境准备失败: {e}")
            return {
                "ready": False,
                "error": str(e)
            }
    
    async def dry_run_test_case(
        self,
        test_case: TestCase,
        environment: Environment,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """测试用例试运行（不发送实际请求）"""
        
        try:
            # 准备环境
            env_result = await self.prepare_test_environment(test_case, environment, variables)
            
            if not env_result["ready"]:
                return {
                    "success": False,
                    "message": "环境准备失败",
                    "details": env_result
                }
            
            # 解析变量
            resolved_request_data = await self.variable_resolver.resolve_variables(
                test_case.request_data,
                user_id=test_case.creator_id,
                environment_id=environment.id,
                temp_variables=variables
            )
            
            # 构建完整请求信息
            api = await test_case.api
            base_url = environment.get_base_url()
            full_url = api.get_full_url(base_url)
            
            headers = {}
            headers.update(environment.get_headers())
            headers.update(api.headers)
            headers.update(resolved_request_data.get("headers", {}))
            
            query_params = {}
            query_params.update(api.query_params)
            query_params.update(resolved_request_data.get("query_params", {}))
            
            body = resolved_request_data.get("body")
            
            return {
                "success": True,
                "message": "试运行成功",
                "request_preview": {
                    "method": api.method,
                    "url": full_url,
                    "headers": headers,
                    "params": query_params,
                    "body": body
                },
                "environment_info": env_result,
                "assertions_count": len(test_case.assertions)
            }
            
        except Exception as e:
            logger.error(f"测试用例试运行失败: {e}")
            return {
                "success": False,
                "message": f"试运行失败: {str(e)}"
            }
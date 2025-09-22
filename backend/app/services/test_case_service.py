"""
测试用例业务服务

处理测试用例相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Q

from app.models.test_case import TestCase
from app.models.api_definition import ApiDefinition
from app.models.user import User
from app.models.environment import Environment
from app.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, RunTestCaseRequest, 
    TestCaseExecutionResult, AssertionRule
)
from app.utils.exceptions import NotFoundError, ConflictError
from loguru import logger


class TestCaseService:
    """测试用例服务类"""
    
    async def create_test_case(self, test_case_data: TestCaseCreate, creator_id: int) -> TestCase:
        """创建测试用例"""
        
        try:
            # 检查创建者是否存在
            creator = await User.get_or_none(id=creator_id, is_active=True)
            if not creator:
                raise NotFoundError(f"创建者不存在: ID={creator_id}")
            
            # 检查关联接口是否存在
            api = await ApiDefinition.get_or_none(id=test_case_data.api_id)
            if not api:
                raise NotFoundError(f"关联接口不存在: ID={test_case_data.api_id}")
            
            # 创建测试用例
            test_case = TestCase(
                name=test_case_data.name,
                description=test_case_data.description,
                api_id=test_case_data.api_id,
                request_data=test_case_data.request_data,
                expected_response=test_case_data.expected_response,
                assertions=[assertion.dict() for assertion in test_case_data.assertions],
                creator_id=creator_id,
                is_active=test_case_data.is_active
            )
            
            await test_case.save()
            
            logger.info(f"测试用例创建成功: {test_case.name} (ID: {test_case.id}) by {creator.username}")
            return test_case
            
        except Exception as e:
            logger.error(f"测试用例创建失败: {e}")
            raise
    
    async def get_test_case_by_id(self, test_case_id: int, user_id: int = None) -> TestCase:
        """根据ID获取测试用例"""
        
        test_case = await TestCase.get_or_none(id=test_case_id).select_related("api", "creator")
        if not test_case:
            raise NotFoundError(f"测试用例不存在: ID={test_case_id}")
        
        # 权限检查：只有创建者或公开接口的测试用例可以访问
        if user_id and test_case.creator_id != user_id and not test_case.api.is_public:
            raise ConflictError("没有权限访问该测试用例")
        
        return test_case
    
    async def update_test_case(
        self, 
        test_case_id: int, 
        test_case_data: TestCaseUpdate, 
        user_id: int
    ) -> TestCase:
        """更新测试用例"""
        
        test_case = await self.get_test_case_by_id(test_case_id, user_id)
        
        # 权限检查：只有创建者可以修改
        if test_case.creator_id != user_id:
            raise ConflictError("只有创建者可以修改测试用例")
        
        try:
            # 更新测试用例信息
            update_fields = []
            
            if test_case_data.name is not None:
                test_case.name = test_case_data.name
                update_fields.append("name")
            
            if test_case_data.description is not None:
                test_case.description = test_case_data.description
                update_fields.append("description")
            
            if test_case_data.request_data is not None:
                test_case.request_data = test_case_data.request_data
                update_fields.append("request_data")
            
            if test_case_data.expected_response is not None:
                test_case.expected_response = test_case_data.expected_response
                update_fields.append("expected_response")
            
            if test_case_data.assertions is not None:
                test_case.assertions = [assertion.dict() for assertion in test_case_data.assertions]
                update_fields.append("assertions")
            
            if test_case_data.is_active is not None:
                test_case.is_active = test_case_data.is_active
                update_fields.append("is_active")
            
            if update_fields:
                await test_case.save(update_fields=update_fields)
                logger.info(f"测试用例更新成功: {test_case.name} (ID: {test_case.id})")
            
            return test_case
            
        except Exception as e:
            logger.error(f"测试用例更新失败: {e}")
            raise
    
    async def delete_test_case(self, test_case_id: int, user_id: int) -> bool:
        """删除测试用例"""
        
        test_case = await self.get_test_case_by_id(test_case_id, user_id)
        
        # 权限检查：只有创建者可以删除
        if test_case.creator_id != user_id:
            raise ConflictError("只有创建者可以删除测试用例")
        
        # 软删除：设置为非激活状态
        test_case.is_active = False
        await test_case.save(update_fields=["is_active"])
        
        logger.info(f"测试用例删除成功: {test_case.name} (ID: {test_case.id})")
        return True
    
    async def list_test_cases(
        self,
        user_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        api_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取测试用例列表"""
        
        # 构建查询条件
        query = TestCase.all().select_related("api", "creator")
        
        # 权限过滤：只能看到公开接口的测试用例或自己创建的
        access_q = Q(creator_id=user_id) | Q(api__is_public=True)
        query = query.filter(access_q)
        
        if search:
            search_q = Q(name__icontains=search) | Q(description__icontains=search)
            query = query.filter(search_q)
        
        if api_id:
            query = query.filter(api_id=api_id)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 计算总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * size
        test_cases = await query.offset(offset).limit(size).order_by("-created_at")
        
        # 构建返回数据
        test_case_list = []
        for test_case in test_cases:
            test_case_dict = {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "api_id": test_case.api_id,
                "api_name": test_case.api.name if test_case.api else "Unknown",
                "request_data": test_case.request_data,
                "expected_response": test_case.expected_response,
                "assertions": test_case.assertions,
                "creator_id": test_case.creator_id,
                "creator_name": test_case.creator.username if test_case.creator else "Unknown",
                "is_active": test_case.is_active,
                "created_at": test_case.created_at.isoformat(),
                "updated_at": test_case.updated_at.isoformat(),
            }
            
            # 获取执行统计信息
            execution_count = await test_case.get_execution_count()
            success_rate = await test_case.get_success_rate()
            
            test_case_dict["execution_count"] = execution_count
            test_case_dict["success_rate"] = success_rate
            
            test_case_list.append(test_case_dict)
        
        return {
            "test_cases": test_case_list,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def copy_test_case(
        self, 
        test_case_id: int, 
        new_name: str, 
        user_id: int,
        copy_to_api_id: Optional[int] = None
    ) -> TestCase:
        """复制测试用例"""
        
        # 获取原测试用例
        original_test_case = await self.get_test_case_by_id(test_case_id, user_id)
        
        # 确定目标接口ID
        target_api_id = copy_to_api_id or original_test_case.api_id
        
        # 检查目标接口是否存在
        target_api = await ApiDefinition.get_or_none(id=target_api_id)
        if not target_api:
            raise NotFoundError(f"目标接口不存在: ID={target_api_id}")
        
        # 创建复制的测试用例
        copied_test_case = TestCase(
            name=new_name,
            description=f"复制自: {original_test_case.name}",
            api_id=target_api_id,
            request_data=original_test_case.request_data,
            expected_response=original_test_case.expected_response,
            assertions=original_test_case.assertions,
            creator_id=user_id,
            is_active=True
        )
        
        await copied_test_case.save()
        
        logger.info(f"测试用例复制成功: {new_name} (ID: {copied_test_case.id})")
        return copied_test_case
    
    async def run_test_case(
        self, 
        test_case_id: int, 
        run_data: RunTestCaseRequest, 
        user_id: int
    ) -> TestCaseExecutionResult:
        """运行单个测试用例"""
        
        from app.services.test_execution_service import TestExecutionService
        
        # 获取测试用例
        test_case = await self.get_test_case_by_id(test_case_id, user_id)
        
        # 检查环境是否存在
        environment = await Environment.get_or_none(
            id=run_data.environment_id, 
            is_active=True
        )
        if not environment:
            raise NotFoundError(f"环境不存在: ID={run_data.environment_id}")
        
        # 使用测试执行服务执行测试
        execution_service = TestExecutionService()
        result = await execution_service.execute_single_test_case(
            test_case=test_case,
            environment=environment,
            variables=run_data.variables,
            save_result=run_data.save_result,
            executor_id=user_id
        )
        
        return TestCaseExecutionResult(
            test_case_id=test_case_id,
            status=result["status"],
            duration=result["duration"],
            request_data=result["request_data"],
            response_data=result["response_data"],
            assertion_results=result["assertion_results"],
            error_message=result.get("error_message")
        )
    
    async def validate_assertions(
        self, 
        response_data: Dict[str, Any], 
        response_time: float, 
        assertions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """验证断言"""
        
        from app.utils.assertion_validator import AssertionValidator
        
        validator = AssertionValidator()
        results = []
        
        for assertion in assertions:
            try:
                result = await validator.validate_assertion(
                    assertion=assertion,
                    response_data=response_data,
                    response_time=response_time
                )
                results.append(result)
            except Exception as e:
                logger.error(f"断言验证失败: {assertion} - {e}")
                results.append({
                    "assertion": assertion,
                    "passed": False,
                    "message": f"断言验证异常: {str(e)}"
                })
        
        return results
    
    async def get_test_case_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取测试用例统计信息"""
        
        # 用户创建的测试用例数量
        user_test_cases = await TestCase.filter(creator_id=user_id, is_active=True).count()
        
        # 用户可访问的测试用例数量
        accessible_test_cases = await TestCase.filter(
            Q(creator_id=user_id) | Q(api__is_public=True),
            is_active=True
        ).count()
        
        # 按接口分组统计
        api_stats = {}
        user_cases = await TestCase.filter(
            creator_id=user_id, 
            is_active=True
        ).select_related("api").values("api__name")
        
        for case in user_cases:
            api_name = case["api__name"]
            api_stats[api_name] = api_stats.get(api_name, 0) + 1
        
        return {
            "user_test_cases": user_test_cases,
            "accessible_test_cases": accessible_test_cases,
            "api_stats": api_stats
        }
"""
接口管理业务服务

处理接口定义相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Q

from app.models.api_definition import ApiDefinition
from app.models.user import User
from app.models.environment import Environment
from app.schemas.api import ApiDefinitionCreate, ApiDefinitionUpdate, TestApiRequest
from app.utils.exceptions import NotFoundError, ConflictError
from loguru import logger


class ApiService:
    """接口服务类"""
    
    async def create_api(self, api_data: ApiDefinitionCreate, creator_id: int) -> ApiDefinition:
        """创建接口定义"""
        
        try:
            # 检查创建者是否存在
            creator = await User.get_or_none(id=creator_id, is_active=True)
            if not creator:
                raise NotFoundError(f"创建者不存在: ID={creator_id}")
            
            # 创建接口定义
            api = ApiDefinition(
                name=api_data.name,
                description=api_data.description,
                method=api_data.method,
                url=api_data.url,
                headers=api_data.headers,
                query_params=api_data.query_params,
                body_schema=api_data.body_schema,
                response_schema=api_data.response_schema,
                creator_id=creator_id,
                is_public=api_data.is_public
            )
            
            await api.save()
            
            logger.info(f"接口创建成功: {api.name} (ID: {api.id}) by {creator.username}")
            return api
            
        except Exception as e:
            logger.error(f"接口创建失败: {e}")
            raise
    
    async def get_api_by_id(self, api_id: int, user_id: int = None) -> ApiDefinition:
        """根据ID获取接口定义"""
        
        api = await ApiDefinition.get_or_none(id=api_id)
        if not api:
            raise NotFoundError(f"接口不存在: ID={api_id}")
        
        # 权限检查：只有创建者或公开接口可以访问
        if not api.is_public and user_id and api.creator_id != user_id:
            # 这里可以添加更复杂的权限逻辑
            pass
        
        return api
    
    async def update_api(self, api_id: int, api_data: ApiDefinitionUpdate, user_id: int) -> ApiDefinition:
        """更新接口定义"""
        
        api = await self.get_api_by_id(api_id, user_id)
        
        # 权限检查：只有创建者可以修改
        if api.creator_id != user_id:
            raise ConflictError("只有创建者可以修改接口")
        
        try:
            # 更新接口信息
            update_fields = []
            
            if api_data.name is not None:
                api.name = api_data.name
                update_fields.append("name")
            
            if api_data.description is not None:
                api.description = api_data.description
                update_fields.append("description")
            
            if api_data.method is not None:
                api.method = api_data.method
                update_fields.append("method")
            
            if api_data.url is not None:
                api.url = api_data.url
                update_fields.append("url")
            
            if api_data.headers is not None:
                api.headers = api_data.headers
                update_fields.append("headers")
            
            if api_data.query_params is not None:
                api.query_params = api_data.query_params
                update_fields.append("query_params")
            
            if api_data.body_schema is not None:
                api.body_schema = api_data.body_schema
                update_fields.append("body_schema")
            
            if api_data.response_schema is not None:
                api.response_schema = api_data.response_schema
                update_fields.append("response_schema")
            
            if api_data.is_public is not None:
                api.is_public = api_data.is_public
                update_fields.append("is_public")
            
            if update_fields:
                await api.save(update_fields=update_fields)
                logger.info(f"接口更新成功: {api.name} (ID: {api.id})")
            
            return api
            
        except Exception as e:
            logger.error(f"接口更新失败: {e}")
            raise
    
    async def delete_api(self, api_id: int, user_id: int) -> bool:
        """删除接口定义"""
        
        api = await self.get_api_by_id(api_id, user_id)
        
        # 权限检查：只有创建者可以删除
        if api.creator_id != user_id:
            raise ConflictError("只有创建者可以删除接口")
        
        # 检查是否有关联的测试用例
        test_case_count = await api.test_cases.filter(is_active=True).count()
        if test_case_count > 0:
            raise ConflictError(f"接口有 {test_case_count} 个关联的测试用例，无法删除")
        
        await api.delete()
        
        logger.info(f"接口删除成功: {api.name} (ID: {api.id})")
        return True
    
    async def list_apis(
        self,
        user_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        method: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取接口列表"""
        
        # 构建查询条件
        query = ApiDefinition.all()
        
        # 权限过滤：只能看到公开的或自己创建的接口
        access_q = Q(is_public=True) | Q(creator_id=user_id)
        query = query.filter(access_q)
        
        if search:
            search_q = Q(name__icontains=search) | Q(description__icontains=search) | Q(url__icontains=search)
            query = query.filter(search_q)
        
        if method:
            query = query.filter(method=method)
        
        if is_public is not None:
            query = query.filter(is_public=is_public)
        
        # 计算总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * size
        apis = await query.select_related("creator").offset(offset).limit(size).order_by("-created_at")
        
        # 构建返回数据
        api_list = []
        for api in apis:
            api_dict = {
                "id": api.id,
                "name": api.name,
                "description": api.description,
                "method": api.method,
                "url": api.url,
                "headers": api.headers,
                "query_params": api.query_params,
                "body_schema": api.body_schema,
                "response_schema": api.response_schema,
                "creator_id": api.creator_id,
                "is_public": api.is_public,
                "created_at": api.created_at.isoformat(),
                "updated_at": api.updated_at.isoformat(),
                "creator_name": api.creator.username if api.creator else "Unknown"
            }
            
            # 获取测试用例数量
            test_case_count = await api.get_test_case_count()
            api_dict["test_case_count"] = test_case_count
            
            api_list.append(api_dict)
        
        return {
            "apis": api_list,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def test_api(
        self, 
        api_id: int, 
        test_data: TestApiRequest, 
        user_id: int
    ) -> Dict[str, Any]:
        """测试接口"""
        
        from app.utils.http_client import HttpClient
        from app.utils.variable_resolver import VariableResolver
        
        # 获取接口定义
        api = await self.get_api_by_id(api_id, user_id)
        
        # 获取环境配置
        environment = None
        if test_data.environment_id:
            environment = await Environment.get_or_none(
                id=test_data.environment_id, 
                is_active=True
            )
            if not environment:
                raise NotFoundError(f"环境不存在: ID={test_data.environment_id}")
        
        try:
            # 解析变量
            variable_resolver = VariableResolver()
            resolved_data = await variable_resolver.resolve_variables(
                test_data.request_data,
                user_id=user_id,
                environment_id=test_data.environment_id,
                temp_variables=test_data.variables
            )
            
            # 构建请求URL
            base_url = environment.get_base_url() if environment else ""
            full_url = api.get_full_url(base_url)
            
            # 合并请求头
            headers = {}
            if environment:
                headers.update(environment.get_headers())
            headers.update(api.headers)
            headers.update(resolved_data.get("headers", {}))
            
            # 合并查询参数
            query_params = {}
            query_params.update(api.query_params)
            query_params.update(resolved_data.get("query_params", {}))
            
            # 请求体
            body = resolved_data.get("body")
            
            # 执行HTTP请求
            http_client = HttpClient()
            result = await http_client.request(
                method=api.method,
                url=full_url,
                headers=headers,
                params=query_params,
                json=body if body else None
            )
            
            logger.info(f"接口测试成功: {api.name} (ID: {api.id}) - 状态码: {result['status_code']}")
            
            return {
                "success": True,
                "status_code": result["status_code"],
                "response_time": result["response_time"],
                "response_data": result["response_data"],
                "headers": result["headers"],
                "request_data": {
                    "url": full_url,
                    "method": api.method,
                    "headers": headers,
                    "params": query_params,
                    "body": body
                }
            }
            
        except Exception as e:
            logger.error(f"接口测试失败: {api.name} (ID: {api.id}) - {e}")
            return {
                "success": False,
                "status_code": 0,
                "response_time": 0,
                "response_data": {},
                "headers": {},
                "error_message": str(e)
            }
    
    async def get_api_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取接口统计信息"""
        
        # 用户创建的接口数量
        user_apis = await ApiDefinition.filter(creator_id=user_id).count()
        
        # 公开接口数量
        public_apis = await ApiDefinition.filter(is_public=True).count()
        
        # 按方法分组统计
        methods_stats = {}
        all_apis = await ApiDefinition.filter(
            Q(creator_id=user_id) | Q(is_public=True)
        ).values_list("method", flat=True)
        
        for method in all_apis:
            methods_stats[method] = methods_stats.get(method, 0) + 1
        
        return {
            "user_apis": user_apis,
            "public_apis": public_apis,
            "total_accessible": user_apis + public_apis,
            "methods_stats": methods_stats
        }
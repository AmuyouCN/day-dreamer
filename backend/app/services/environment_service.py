"""
环境管理业务服务

处理环境配置相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Q

from app.models.environment import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate
from app.utils.exceptions import NotFoundError, ConflictError
from loguru import logger


class EnvironmentService:
    """环境服务类"""
    
    async def create_environment(self, env_data: EnvironmentCreate) -> Environment:
        """创建环境"""
        
        try:
            # 检查环境名称是否已存在
            existing_env = await Environment.get_or_none(name=env_data.name)
            if existing_env:
                raise ConflictError(f"环境名称已存在: {env_data.name}")
            
            # 创建环境
            environment = Environment(
                name=env_data.name,
                description=env_data.description,
                config=env_data.config,
                is_active=env_data.is_active
            )
            
            await environment.save()
            
            logger.info(f"环境创建成功: {environment.name} (ID: {environment.id})")
            return environment
            
        except ConflictError:
            raise
        except Exception as e:
            logger.error(f"环境创建失败: {e}")
            raise
    
    async def get_environment_by_id(self, env_id: int) -> Environment:
        """根据ID获取环境"""
        
        environment = await Environment.get_or_none(id=env_id)
        if not environment:
            raise NotFoundError(f"环境不存在: ID={env_id}")
        
        return environment
    
    async def update_environment(self, env_id: int, env_data: EnvironmentUpdate) -> Environment:
        """更新环境"""
        
        environment = await self.get_environment_by_id(env_id)
        
        try:
            # 更新环境信息
            update_fields = []
            
            if env_data.name is not None:
                # 检查新名称是否已存在
                if env_data.name != environment.name:
                    existing_env = await Environment.get_or_none(name=env_data.name)
                    if existing_env:
                        raise ConflictError(f"环境名称已存在: {env_data.name}")
                environment.name = env_data.name
                update_fields.append("name")
            
            if env_data.description is not None:
                environment.description = env_data.description
                update_fields.append("description")
            
            if env_data.config is not None:
                environment.config = env_data.config
                update_fields.append("config")
            
            if env_data.is_active is not None:
                environment.is_active = env_data.is_active
                update_fields.append("is_active")
            
            if update_fields:
                await environment.save(update_fields=update_fields)
                logger.info(f"环境更新成功: {environment.name} (ID: {environment.id})")
            
            return environment
            
        except ConflictError:
            raise
        except Exception as e:
            logger.error(f"环境更新失败: {e}")
            raise
    
    async def delete_environment(self, env_id: int) -> bool:
        """删除环境"""
        
        environment = await self.get_environment_by_id(env_id)
        
        # 检查是否有关联的测试执行
        execution_count = await environment.test_executions.all().count()
        if execution_count > 0:
            raise ConflictError(f"环境有 {execution_count} 个关联的测试执行记录，无法删除")
        
        # 检查是否有关联的环境变量
        variable_count = await environment.variables.all().count()
        if variable_count > 0:
            raise ConflictError(f"环境有 {variable_count} 个关联的环境变量，无法删除")
        
        await environment.delete()
        
        logger.info(f"环境删除成功: {environment.name} (ID: {environment.id})")
        return True
    
    async def list_environments(
        self,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取环境列表"""
        
        # 构建查询条件
        query = Environment.all()
        
        if search:
            search_q = Q(name__icontains=search) | Q(description__icontains=search)
            query = query.filter(search_q)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 计算总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * size
        environments = await query.offset(offset).limit(size).order_by("-created_at")
        
        # 构建返回数据
        env_list = []
        for env in environments:
            env_dict = {
                "id": env.id,
                "name": env.name,
                "description": env.description,
                "config": env.config,
                "is_active": env.is_active,
                "created_at": env.created_at.isoformat(),
                "updated_at": env.updated_at.isoformat(),
            }
            
            # 获取关联统计信息
            variable_count = await env.variables.all().count()
            execution_count = await env.test_executions.all().count()
            
            env_dict["variable_count"] = variable_count
            env_dict["execution_count"] = execution_count
            
            env_list.append(env_dict)
        
        return {
            "environments": env_list,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def get_environment_variables(self, env_id: int) -> List[Dict[str, Any]]:
        """获取环境的变量列表"""
        
        environment = await self.get_environment_by_id(env_id)
        variables = await environment.variables.all()
        
        return [
            {
                "id": var.id,
                "name": var.name,
                "value": var.value,
                "type": var.type,
                "description": var.description,
                "created_at": var.created_at.isoformat(),
                "updated_at": var.updated_at.isoformat()
            }
            for var in variables
        ]
    
    async def test_environment_connectivity(self, env_id: int) -> Dict[str, Any]:
        """测试环境连通性"""
        
        environment = await self.get_environment_by_id(env_id)
        base_url = environment.get_base_url()
        
        if not base_url:
            return {
                "success": False,
                "message": "环境未配置base_url"
            }
        
        try:
            from app.utils.http_client import HttpClient
            
            # 发送健康检查请求
            http_client = HttpClient()
            result = await http_client.request(
                method="GET",
                url=f"{base_url}/health",
                timeout=10
            )
            
            return {
                "success": True,
                "status_code": result["status_code"],
                "response_time": result["response_time"],
                "message": "环境连通性测试成功"
            }
            
        except Exception as e:
            logger.warning(f"环境连通性测试失败: {environment.name} - {e}")
            return {
                "success": False,
                "message": f"环境连通性测试失败: {str(e)}"
            }
    
    async def copy_environment(self, env_id: int, new_name: str) -> Environment:
        """复制环境"""
        
        # 获取原环境
        original_env = await self.get_environment_by_id(env_id)
        
        # 检查新名称是否已存在
        existing_env = await Environment.get_or_none(name=new_name)
        if existing_env:
            raise ConflictError(f"环境名称已存在: {new_name}")
        
        # 创建复制的环境
        copied_env = Environment(
            name=new_name,
            description=f"复制自: {original_env.name}",
            config=original_env.config.copy(),
            is_active=True
        )
        
        await copied_env.save()
        
        logger.info(f"环境复制成功: {new_name} (ID: {copied_env.id})")
        return copied_env
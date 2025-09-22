"""
变量管理服务

提供变量的CRUD操作和解析功能
"""

import json
import re
from typing import Optional, List, Dict, Any, Union
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet

from app.models.variable import Variable, VariableScope, VariableType
from app.models.environment import Environment
from app.utils.logger import logger


class VariableService:
    """变量管理服务"""
    
    @staticmethod
    async def create_variable(
        name: str,
        value: str,
        scope: VariableScope,
        created_by: int,
        type: VariableType = VariableType.STRING,
        description: Optional[str] = None,
        environment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        is_sensitive: bool = False
    ) -> Variable:
        """创建变量"""
        
        # 验证变量名唯一性（同作用域内）
        existing = await Variable.filter(
            name=name,
            scope=scope,
            environment_id=environment_id,
            user_id=user_id,
            session_id=session_id,
            is_active=True
        ).first()
        
        if existing:
            raise ValueError(f"变量 '{name}' 在当前作用域内已存在")
        
        # 验证环境ID（如果是环境变量）
        if scope == VariableScope.ENVIRONMENT and environment_id:
            env = await Environment.filter(id=environment_id, is_active=True).first()
            if not env:
                raise ValueError(f"环境 ID {environment_id} 不存在")
        
        variable = await Variable.create(
            name=name,
            value=value,
            type=type,
            scope=scope,
            description=description,
            environment_id=environment_id,
            user_id=user_id,
            session_id=session_id,
            created_by=created_by,
            is_sensitive=is_sensitive
        )
        
        logger.info(f"创建变量: {name}({scope}) by user {created_by}")
        return variable
    
    @staticmethod
    async def get_variable(variable_id: int) -> Variable:
        """根据ID获取变量"""
        try:
            return await Variable.get(id=variable_id, is_active=True)
        except DoesNotExist:
            raise ValueError(f"变量 ID {variable_id} 不存在")
    
    @staticmethod
    async def get_variable_by_name(
        name: str,
        scope: VariableScope,
        environment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[Variable]:
        """根据名称获取变量"""
        return await Variable.filter(
            name=name,
            scope=scope,
            environment_id=environment_id,
            user_id=user_id,
            session_id=session_id,
            is_active=True
        ).first()
    
    @staticmethod
    async def list_variables(
        scope: Optional[VariableScope] = None,
        environment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        keyword: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> tuple[List[Variable], int]:
        """列出变量"""
        
        query = Variable.filter(is_active=True)
        
        if scope:
            query = query.filter(scope=scope)
        
        if environment_id:
            query = query.filter(environment_id=environment_id)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        if session_id:
            query = query.filter(session_id=session_id)
        
        if keyword:
            query = query.filter(
                name__icontains=keyword
            ) | query.filter(
                description__icontains=keyword
            )
        
        total = await query.count()
        variables = await query.offset(offset).limit(limit).order_by('-created_at')
        
        return variables, total
    
    @staticmethod
    async def update_variable(
        variable_id: int,
        name: Optional[str] = None,
        value: Optional[str] = None,
        type: Optional[VariableType] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_sensitive: Optional[bool] = None
    ) -> Variable:
        """更新变量"""
        
        variable = await VariableService.get_variable(variable_id)
        
        if name and name != variable.name:
            # 检查新名称的唯一性
            existing = await Variable.filter(
                name=name,
                scope=variable.scope,
                environment_id=variable.environment_id,
                user_id=variable.user_id,
                session_id=variable.session_id,
                is_active=True
            ).exclude(id=variable_id).first()
            
            if existing:
                raise ValueError(f"变量名 '{name}' 在当前作用域内已存在")
            
            variable.name = name
        
        if value is not None:
            variable.value = value
        
        if type:
            variable.type = type
        
        if description is not None:
            variable.description = description
        
        if is_active is not None:
            variable.is_active = is_active
        
        if is_sensitive is not None:
            variable.is_sensitive = is_sensitive
        
        await variable.save()
        logger.info(f"更新变量: {variable.name}({variable.scope})")
        
        return variable
    
    @staticmethod
    async def delete_variable(variable_id: int) -> bool:
        """删除变量（软删除）"""
        variable = await VariableService.get_variable(variable_id)
        variable.is_active = False
        await variable.save()
        
        logger.info(f"删除变量: {variable.name}({variable.scope})")
        return True
    
    @staticmethod
    async def batch_create_variables(
        variables_data: List[Dict[str, Any]],
        created_by: int
    ) -> List[Variable]:
        """批量创建变量"""
        variables = []
        
        for data in variables_data:
            try:
                variable = await VariableService.create_variable(
                    name=data['name'],
                    value=data['value'],
                    scope=data['scope'],
                    created_by=created_by,
                    type=data.get('type', VariableType.STRING),
                    description=data.get('description'),
                    environment_id=data.get('environment_id'),
                    user_id=data.get('user_id'),
                    session_id=data.get('session_id'),
                    is_sensitive=data.get('is_sensitive', False)
                )
                variables.append(variable)
            except Exception as e:
                logger.error(f"批量创建变量失败: {data.get('name')} - {str(e)}")
                continue
        
        return variables
    
    @staticmethod
    async def resolve_variables(
        text: str,
        environment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> str:
        """解析文本中的变量引用
        
        支持的变量引用格式:
        - {{variable_name}} - 自动按优先级查找
        - {{global.variable_name}} - 全局变量
        - {{env.variable_name}} - 环境变量
        - {{user.variable_name}} - 个人变量
        - {{temp.variable_name}} - 临时变量
        """
        
        if not text:
            return text
        
        # 匹配变量引用模式
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, text)
        
        if not matches:
            return text
        
        result = text
        
        for match in matches:
            variable_ref = match.strip()
            
            # 解析变量引用
            if '.' in variable_ref:
                scope_prefix, var_name = variable_ref.split('.', 1)
                scope_mapping = {
                    'global': VariableScope.GLOBAL,
                    'env': VariableScope.ENVIRONMENT,
                    'user': VariableScope.PERSONAL,
                    'temp': VariableScope.TEMPORARY
                }
                scope = scope_mapping.get(scope_prefix)
                if not scope:
                    logger.warning(f"未知的变量作用域前缀: {scope_prefix}")
                    continue
            else:
                var_name = variable_ref
                scope = None
            
            # 获取变量值
            value = await VariableService._get_variable_value(
                var_name, scope, environment_id, user_id, session_id
            )
            
            if value is not None:
                # 替换变量引用
                placeholder = f"{{{{{match}}}}}"
                result = result.replace(placeholder, str(value))
            else:
                logger.warning(f"变量未找到: {variable_ref}")
        
        return result
    
    @staticmethod
    async def _get_variable_value(
        name: str,
        scope: Optional[VariableScope] = None,
        environment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[Any]:
        """获取变量值（按优先级查找）"""
        
        if scope:
            # 指定作用域查找
            variable = await VariableService.get_variable_by_name(
                name, scope, environment_id, user_id, session_id
            )
            return variable.get_typed_value() if variable else None
        
        # 按优先级查找: 临时 > 个人 > 环境 > 全局
        scopes = [
            (VariableScope.TEMPORARY, {'session_id': session_id}),
            (VariableScope.PERSONAL, {'user_id': user_id}),
            (VariableScope.ENVIRONMENT, {'environment_id': environment_id}),
            (VariableScope.GLOBAL, {})
        ]
        
        for scope_type, params in scopes:
            if scope_type == VariableScope.TEMPORARY and not session_id:
                continue
            if scope_type == VariableScope.PERSONAL and not user_id:
                continue
            if scope_type == VariableScope.ENVIRONMENT and not environment_id:
                continue
            
            variable = await VariableService.get_variable_by_name(
                name, scope_type, **params
            )
            if variable:
                return variable.get_typed_value()
        
        return None
    
    @staticmethod
    async def export_variables(
        format: str = "json",
        scope: Optional[VariableScope] = None,
        environment_id: Optional[int] = None,
        include_sensitive: bool = False
    ) -> str:
        """导出变量"""
        
        variables, _ = await VariableService.list_variables(
            scope=scope,
            environment_id=environment_id,
            limit=1000
        )
        
        export_data = []
        for var in variables:
            data = {
                'name': var.name,
                'value': var.value if not var.is_sensitive or include_sensitive else '***',
                'type': var.type,
                'scope': var.scope,
                'description': var.description
            }
            export_data.append(data)
        
        if format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if export_data:
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            return output.getvalue()
        elif format == "env":
            lines = []
            for data in export_data:
                if data['type'] == VariableType.STRING:
                    lines.append(f"{data['name']}={data['value']}")
            return '\n'.join(lines)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    @staticmethod
    async def cleanup_temporary_variables(max_age_hours: int = 24) -> int:
        """清理过期的临时变量"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        count = await Variable.filter(
            scope=VariableScope.TEMPORARY,
            created_at__lt=cutoff_time,
            is_active=True
        ).update(is_active=False)
        
        logger.info(f"清理了 {count} 个过期临时变量")
        return count
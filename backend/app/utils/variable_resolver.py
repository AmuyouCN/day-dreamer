"""
变量解析器

用于解析测试数据中的变量引用
"""

import re
import json
from typing import Dict, Any, Optional, Union
from loguru import logger

from app.models.variable import Variable, VariableScope


class VariableResolver:
    """变量解析器类"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    async def resolve_variables(
        self,
        data: Any,
        user_id: Optional[int] = None,
        environment_id: Optional[int] = None,
        temp_variables: Optional[Dict[str, str]] = None
    ) -> Any:
        """解析数据中的变量"""
        
        # 获取所有可用变量
        variables = await self._get_available_variables(
            user_id=user_id,
            environment_id=environment_id,
            temp_variables=temp_variables or {}
        )
        
        # 递归解析数据
        return self._resolve_data(data, variables)
    
    async def _get_available_variables(
        self,
        user_id: Optional[int] = None,
        environment_id: Optional[int] = None,
        temp_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """获取所有可用变量"""
        
        variables = {}
        
        # 1. 全局变量（优先级最低）
        global_vars = await Variable.filter(scope=VariableScope.GLOBAL).all()
        for var in global_vars:
            variables[var.name] = str(var.get_typed_value())
        
        # 2. 环境变量
        if environment_id:
            env_vars = await Variable.filter(
                scope=VariableScope.ENVIRONMENT,
                environment_id=environment_id
            ).all()
            for var in env_vars:
                variables[var.name] = str(var.get_typed_value())
        
        # 3. 个人变量
        if user_id:
            personal_vars = await Variable.filter(
                scope=VariableScope.PERSONAL,
                user_id=user_id
            ).all()
            for var in personal_vars:
                variables[var.name] = str(var.get_typed_value())
        
        # 4. 临时变量（优先级最高）
        if temp_variables:
            variables.update(temp_variables)
        
        return variables
    
    def _resolve_data(self, data: Any, variables: Dict[str, str]) -> Any:
        """递归解析数据中的变量"""
        
        if isinstance(data, str):
            return self._resolve_string(data, variables)
        elif isinstance(data, dict):
            return {key: self._resolve_data(value, variables) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._resolve_data(item, variables) for item in data]
        else:
            return data
    
    def _resolve_string(self, text: str, variables: Dict[str, str]) -> str:
        """解析字符串中的变量"""
        
        def replace_variable(match):
            var_name = match.group(1).strip()
            
            # 支持函数调用，如 {{randomString(10)}}
            if '(' in var_name and ')' in var_name:
                return self._execute_function(var_name)
            
            # 普通变量替换
            return variables.get(var_name, match.group(0))
        
        return self.variable_pattern.sub(replace_variable, text)
    
    def _execute_function(self, function_call: str) -> str:
        """执行变量函数"""
        
        try:
            # 解析函数名和参数
            func_match = re.match(r'(\w+)\((.*)\)', function_call)
            if not func_match:
                return f"{{{{{function_call}}}}}"
            
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            
            # 解析参数
            args = []
            if args_str.strip():
                # 简单的参数解析，支持数字和字符串
                for arg in args_str.split(','):
                    arg = arg.strip()
                    if arg.startswith('"') and arg.endswith('"'):
                        args.append(arg[1:-1])  # 字符串
                    elif arg.startswith("'") and arg.endswith("'"):
                        args.append(arg[1:-1])  # 字符串
                    else:
                        try:
                            args.append(int(arg))  # 整数
                        except ValueError:
                            try:
                                args.append(float(arg))  # 浮点数
                            except ValueError:
                                args.append(arg)  # 其他
            
            # 执行函数
            return self._call_builtin_function(func_name, args)
            
        except Exception as e:
            logger.warning(f"函数执行失败: {function_call} - {e}")
            return f"{{{{{function_call}}}}}"
    
    def _call_builtin_function(self, func_name: str, args: list) -> str:
        """调用内置函数"""
        
        import random
        import string
        import time
        import uuid
        from datetime import datetime
        
        try:
            if func_name == 'randomString':
                length = args[0] if args else 10
                return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            
            elif func_name == 'randomInt':
                min_val = args[0] if len(args) > 0 else 1
                max_val = args[1] if len(args) > 1 else 100
                return str(random.randint(min_val, max_val))
            
            elif func_name == 'timestamp':
                return str(int(time.time()))
            
            elif func_name == 'datetime':
                format_str = args[0] if args else '%Y-%m-%d %H:%M:%S'
                return datetime.now().strftime(format_str)
            
            elif func_name == 'uuid':
                return str(uuid.uuid4())
            
            elif func_name == 'randomEmail':
                domain = args[0] if args else 'example.com'
                username = ''.join(random.choices(string.ascii_lowercase, k=8))
                return f"{username}@{domain}"
            
            elif func_name == 'randomPhone':
                return ''.join(['1'] + [str(random.randint(0, 9)) for _ in range(10)])
            
            elif func_name == 'base64':
                import base64
                text = args[0] if args else 'test'
                return base64.b64encode(text.encode()).decode()
            
            else:
                logger.warning(f"未知函数: {func_name}")
                return f"{{{{unknown_function:{func_name}}}}}"
                
        except Exception as e:
            logger.error(f"函数执行异常: {func_name} - {e}")
            return f"{{{{error:{func_name}}}}}"
    
    def extract_variables(self, data: Any) -> set:
        """提取数据中使用的变量名"""
        
        variables = set()
        
        def extract_from_text(text: str):
            matches = self.variable_pattern.findall(text)
            for match in matches:
                var_name = match.strip()
                # 排除函数调用
                if '(' not in var_name:
                    variables.add(var_name)
        
        def extract_recursive(obj):
            if isinstance(obj, str):
                extract_from_text(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(data)
        return variables
    
    def validate_variables(
        self,
        data: Any,
        available_variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """验证数据中的变量是否都可用"""
        
        used_variables = self.extract_variables(data)
        missing_variables = []
        available_vars = []
        
        for var_name in used_variables:
            if var_name in available_variables:
                available_vars.append(var_name)
            else:
                missing_variables.append(var_name)
        
        return {
            "used_variables": list(used_variables),
            "available_variables": available_vars,
            "missing_variables": missing_variables,
            "is_valid": len(missing_variables) == 0
        }
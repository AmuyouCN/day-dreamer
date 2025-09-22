"""
断言验证器

用于验证测试响应是否符合预期
"""

import re
import json
from typing import Dict, Any, Union
from jsonpath_ng import parse as jsonpath_parse
from loguru import logger


class AssertionValidator:
    """断言验证器类"""
    
    async def validate_assertion(
        self,
        assertion: Dict[str, Any],
        response_data: Dict[str, Any],
        response_time: float
    ) -> Dict[str, Any]:
        """验证单个断言"""
        
        assertion_type = assertion.get("type")
        field = assertion.get("field")
        operator = assertion.get("operator")
        expected = assertion.get("expected")
        description = assertion.get("description", f"{assertion_type} {operator} {expected}")
        
        try:
            # 获取实际值
            actual_value = self._get_actual_value(
                assertion_type, field, response_data, response_time
            )
            
            # 执行断言
            passed = self._compare_values(actual_value, expected, operator)
            
            result = {
                "assertion": assertion,
                "actual_value": actual_value,
                "expected_value": expected,
                "passed": passed,
                "message": self._get_assertion_message(
                    description, actual_value, expected, passed
                )
            }
            
            if passed:
                logger.debug(f"断言通过: {description}")
            else:
                logger.warning(f"断言失败: {description} - 实际值: {actual_value}, 期望值: {expected}")
            
            return result
            
        except Exception as e:
            logger.error(f"断言验证异常: {assertion} - {e}")
            return {
                "assertion": assertion,
                "actual_value": None,
                "expected_value": expected,
                "passed": False,
                "message": f"断言验证异常: {str(e)}"
            }
    
    def _get_actual_value(
        self,
        assertion_type: str,
        field: str,
        response_data: Dict[str, Any],
        response_time: float
    ) -> Any:
        """获取实际值"""
        
        if assertion_type == "status_code":
            return response_data.get("status_code")
        
        elif assertion_type == "response_time":
            return response_time
        
        elif assertion_type == "json_path":
            if not field:
                raise ValueError("json_path断言需要指定field")
            return self._extract_json_path_value(response_data, field)
        
        elif assertion_type == "contains":
            response_body = response_data.get("response_data", {})
            if isinstance(response_body, dict):
                return json.dumps(response_body, ensure_ascii=False)
            return str(response_body)
        
        elif assertion_type == "equals":
            if field:
                return self._extract_json_path_value(response_data, field)
            else:
                return response_data.get("response_data")
        
        elif assertion_type == "regex":
            response_body = response_data.get("response_data", {})
            if isinstance(response_body, dict):
                return json.dumps(response_body, ensure_ascii=False)
            return str(response_body)
        
        else:
            raise ValueError(f"不支持的断言类型: {assertion_type}")
    
    def _extract_json_path_value(self, data: Dict[str, Any], json_path: str) -> Any:
        """使用JSONPath提取值"""
        
        try:
            # 从响应数据中提取
            response_data = data.get("response_data", {})
            
            # 解析JSONPath
            jsonpath_expr = jsonpath_parse(json_path)
            matches = jsonpath_expr.find(response_data)
            
            if not matches:
                return None
            
            # 如果有多个匹配，返回第一个
            return matches[0].value
            
        except Exception as e:
            logger.error(f"JSONPath提取失败: {json_path} - {e}")
            return None
    
    def _compare_values(self, actual: Any, expected: Any, operator: str) -> bool:
        """比较值"""
        
        try:
            if operator == "eq":
                return self._safe_compare(actual, expected, lambda a, e: a == e)
            
            elif operator == "ne":
                return self._safe_compare(actual, expected, lambda a, e: a != e)
            
            elif operator == "gt":
                return self._safe_compare(actual, expected, lambda a, e: float(a) > float(e))
            
            elif operator == "lt":
                return self._safe_compare(actual, expected, lambda a, e: float(a) < float(e))
            
            elif operator == "gte":
                return self._safe_compare(actual, expected, lambda a, e: float(a) >= float(e))
            
            elif operator == "lte":
                return self._safe_compare(actual, expected, lambda a, e: float(a) <= float(e))
            
            elif operator == "contains":
                actual_str = str(actual) if actual is not None else ""
                expected_str = str(expected)
                return expected_str in actual_str
            
            elif operator == "not_contains":
                actual_str = str(actual) if actual is not None else ""
                expected_str = str(expected)
                return expected_str not in actual_str
            
            elif operator == "regex":
                actual_str = str(actual) if actual is not None else ""
                pattern = str(expected)
                return bool(re.search(pattern, actual_str))
            
            else:
                raise ValueError(f"不支持的操作符: {operator}")
                
        except Exception as e:
            logger.error(f"值比较异常: {actual} {operator} {expected} - {e}")
            return False
    
    def _safe_compare(self, actual: Any, expected: Any, compare_func) -> bool:
        """安全比较（处理类型转换）"""
        
        try:
            return compare_func(actual, expected)
        except (TypeError, ValueError):
            # 尝试字符串比较
            try:
                return compare_func(str(actual), str(expected))
            except Exception:
                return False
    
    def _get_assertion_message(
        self,
        description: str,
        actual_value: Any,
        expected_value: Any,
        passed: bool
    ) -> str:
        """生成断言消息"""
        
        if passed:
            return f"✓ {description}"
        else:
            return f"✗ {description} - 实际: {actual_value}, 期望: {expected_value}"
    
    async def validate_all_assertions(
        self,
        assertions: list,
        response_data: Dict[str, Any],
        response_time: float
    ) -> Dict[str, Any]:
        """验证所有断言"""
        
        if not assertions:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "results": [],
                "all_passed": True
            }
        
        results = []
        passed_count = 0
        
        for assertion in assertions:
            result = await self.validate_assertion(assertion, response_data, response_time)
            results.append(result)
            
            if result["passed"]:
                passed_count += 1
        
        total_count = len(assertions)
        failed_count = total_count - passed_count
        all_passed = failed_count == 0
        
        return {
            "total": total_count,
            "passed": passed_count,
            "failed": failed_count,
            "results": results,
            "all_passed": all_passed,
            "pass_rate": round(passed_count / total_count * 100, 2) if total_count > 0 else 0
        }
"""
HTTP客户端工具

用于发送HTTP请求和处理响应
"""

import asyncio
import time
from typing import Dict, Any, Optional, Union
import httpx
from loguru import logger
from app.core.config import settings


class HttpClient:
    """HTTP客户端类"""
    
    def __init__(self, timeout: int = None):
        self.timeout = timeout or settings.test_timeout
        self.client = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            verify=False,  # 在测试环境中可能需要忽略SSL验证
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.client:
            await self.client.aclose()
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, Dict[str, Any]]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        
        start_time = time.time()
        request_timeout = timeout or self.timeout
        
        # 准备请求参数
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "timeout": request_timeout
        }
        
        if headers:
            request_kwargs["headers"] = headers
        
        if params:
            request_kwargs["params"] = params
        
        if json:
            request_kwargs["json"] = json
        elif data:
            if isinstance(data, dict):
                request_kwargs["data"] = data
            else:
                request_kwargs["content"] = data
        
        try:
            # 如果没有活动的客户端，创建一个临时的
            if not self.client:
                async with httpx.AsyncClient(
                    timeout=request_timeout,
                    verify=False,
                    follow_redirects=True
                ) as temp_client:
                    response = await temp_client.request(**request_kwargs)
                    return await self._process_response(response, start_time)
            else:
                response = await self.client.request(**request_kwargs)
                return await self._process_response(response, start_time)
                
        except httpx.TimeoutException:
            duration = (time.time() - start_time) * 1000
            logger.error(f"HTTP请求超时: {method} {url} - {duration:.2f}ms")
            raise Exception(f"请求超时: {request_timeout}秒")
        
        except httpx.ConnectError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"HTTP连接错误: {method} {url} - {e}")
            raise Exception(f"连接错误: {str(e)}")
        
        except httpx.HTTPStatusError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"HTTP状态错误: {method} {url} - {e.response.status_code}")
            # 对于HTTP状态错误，我们仍然返回响应数据
            return await self._process_response(e.response, start_time)
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"HTTP请求异常: {method} {url} - {e}")
            raise Exception(f"请求异常: {str(e)}")
    
    async def _process_response(self, response: httpx.Response, start_time: float) -> Dict[str, Any]:
        """处理HTTP响应"""
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 获取响应头
        response_headers = dict(response.headers)
        
        # 获取响应体
        try:
            # 尝试解析为JSON
            response_data = response.json()
        except Exception:
            # 如果不是JSON，获取文本内容
            response_data = {"text": response.text, "content_type": response_headers.get("content-type", "")}
        
        result = {
            "status_code": response.status_code,
            "response_time": round(duration, 2),
            "response_data": response_data,
            "headers": response_headers,
            "url": str(response.url),
            "request_method": response.request.method
        }
        
        logger.info(
            f"HTTP请求完成: {response.request.method} {response.url} - "
            f"状态码: {response.status_code} - 响应时间: {duration:.2f}ms"
        )
        
        return result
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return await self.request("DELETE", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> Dict[str, Any]:
        """PATCH请求"""
        return await self.request("PATCH", url, **kwargs)


class HttpClientPool:
    """HTTP客户端池"""
    
    def __init__(self, max_clients: int = 10):
        self.max_clients = max_clients
        self.clients = []
        self.semaphore = asyncio.Semaphore(max_clients)
    
    async def get_client(self) -> HttpClient:
        """获取HTTP客户端"""
        async with self.semaphore:
            if self.clients:
                return self.clients.pop()
            else:
                return HttpClient()
    
    async def return_client(self, client: HttpClient):
        """归还HTTP客户端"""
        if len(self.clients) < self.max_clients:
            self.clients.append(client)
        else:
            # 如果池已满，关闭客户端
            if client.client:
                await client.client.aclose()


# 全局HTTP客户端池
http_client_pool = HttpClientPool(max_clients=settings.max_concurrent_tests)
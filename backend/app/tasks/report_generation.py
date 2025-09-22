"""
测试报告生成异步任务

处理测试结果分析和报告生成
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Task

from app.core.celery_app import celery_app, TaskStatus
from app.utils.logger import logger


class AsyncReportGenerationTask(Task):
    """异步报告生成任务基类"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功完成时的回调"""
        logger.info(f"报告生成任务完成: {task_id}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"报告生成任务失败: {task_id} - {str(exc)}")


@celery_app.task(bind=True, base=AsyncReportGenerationTask, name="generate_test_report")
def generate_test_report(
    self,
    execution_results: List[Dict[str, Any]],
    report_type: str = "html",
    report_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """生成测试报告
    
    Args:
        execution_results: 测试执行结果列表
        report_type: 报告类型 (html, json, pdf, excel)
        report_config: 报告配置
    
    Returns:
        报告生成结果
    """
    
    async def generate_report():
        try:
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始生成测试报告", "report_type": report_type}
            )
            
            # 分析测试结果
            analysis = analyze_test_results(execution_results)
            
            # 根据类型生成报告
            if report_type == "html":
                report_content = generate_html_report(analysis, execution_results, report_config)
            elif report_type == "json":
                report_content = generate_json_report(analysis, execution_results)
            elif report_type == "pdf":
                report_content = generate_pdf_report(analysis, execution_results, report_config)
            elif report_type == "excel":
                report_content = generate_excel_report(analysis, execution_results, report_config)
            else:
                raise ValueError(f"不支持的报告类型: {report_type}")
            
            # 保存报告
            report_id = await save_report(
                report_type=report_type,
                content=report_content,
                analysis=analysis,
                config=report_config
            )
            
            return {
                "status": "success",
                "report_id": report_id,
                "report_type": report_type,
                "analysis": analysis,
                "file_size": len(report_content) if isinstance(report_content, str) else len(str(report_content))
            }
            
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(generate_report())
    finally:
        loop.close()


def analyze_test_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析测试结果"""
    
    total_count = len(results)
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = total_count - success_count
    
    # 计算成功率
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    # 统计响应时间
    response_times = []
    status_codes = {}
    error_types = {}
    
    for result in results:
        if result.get("status") == "success" and "result" in result:
            test_result = result["result"]
            
            # 响应时间统计
            if "response_time" in test_result:
                response_times.append(test_result["response_time"])
            
            # 状态码统计
            if "status_code" in test_result:
                code = test_result["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1
        
        elif result.get("status") == "failed":
            # 错误类型统计
            error = result.get("error", "Unknown error")
            error_type = type(error).__name__ if isinstance(error, Exception) else "Error"
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # 响应时间分析
    response_time_analysis = {}
    if response_times:
        response_time_analysis = {
            "min": min(response_times),
            "max": max(response_times),
            "avg": sum(response_times) / len(response_times),
            "median": sorted(response_times)[len(response_times) // 2]
        }
    
    return {
        "summary": {
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": round(success_rate, 2)
        },
        "response_time": response_time_analysis,
        "status_codes": status_codes,
        "error_types": error_types,
        "execution_time": datetime.now().isoformat()
    }


def generate_html_report(
    analysis: Dict[str, Any],
    results: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> str:
    """生成HTML报告"""
    
    template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API自动化测试报告</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .summary { display: flex; gap: 20px; margin-bottom: 20px; }
            .metric { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }
            .metric h3 { margin: 0 0 10px 0; color: #333; }
            .metric .value { font-size: 24px; font-weight: bold; }
            .success { color: #28a745; }
            .failed { color: #dc3545; }
            .total { color: #007bff; }
            .details { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; }
            .status-success { color: #28a745; font-weight: bold; }
            .status-failed { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>API自动化测试报告</h1>
            <p>生成时间: {execution_time}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>总用例数</h3>
                <div class="value total">{total_count}</div>
            </div>
            <div class="metric">
                <h3>成功用例</h3>
                <div class="value success">{success_count}</div>
            </div>
            <div class="metric">
                <h3>失败用例</h3>
                <div class="value failed">{failed_count}</div>
            </div>
            <div class="metric">
                <h3>成功率</h3>
                <div class="value">{success_rate}%</div>
            </div>
        </div>
        
        {response_time_section}
        
        <div class="details">
            <h2>测试用例详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>用例ID</th>
                        <th>状态</th>
                        <th>响应时间(ms)</th>
                        <th>状态码</th>
                        <th>错误信息</th>
                    </tr>
                </thead>
                <tbody>
                    {test_details}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    # 生成响应时间部分
    response_time_section = ""
    if analysis.get("response_time"):
        rt = analysis["response_time"]
        response_time_section = f"""
        <div class="details">
            <h2>响应时间分析</h2>
            <div class="summary">
                <div class="metric">
                    <h3>最小值</h3>
                    <div class="value">{rt['min']:.2f}ms</div>
                </div>
                <div class="metric">
                    <h3>最大值</h3>
                    <div class="value">{rt['max']:.2f}ms</div>
                </div>
                <div class="metric">
                    <h3>平均值</h3>
                    <div class="value">{rt['avg']:.2f}ms</div>
                </div>
                <div class="metric">
                    <h3>中位数</h3>
                    <div class="value">{rt['median']:.2f}ms</div>
                </div>
            </div>
        </div>
        """
    
    # 生成测试详情
    test_details = ""
    for result in results:
        test_case_id = result.get("test_case_id", "N/A")
        status = result.get("status", "unknown")
        status_class = "status-success" if status == "success" else "status-failed"
        
        response_time = "N/A"
        status_code = "N/A"
        error_message = ""
        
        if status == "success" and "result" in result:
            test_result = result["result"]
            response_time = f"{test_result.get('response_time', 'N/A'):.2f}" if test_result.get('response_time') else "N/A"
            status_code = test_result.get("status_code", "N/A")
        elif status == "failed":
            error_message = result.get("error", "Unknown error")
        
        test_details += f"""
        <tr>
            <td>{test_case_id}</td>
            <td class="{status_class}">{status}</td>
            <td>{response_time}</td>
            <td>{status_code}</td>
            <td>{error_message}</td>
        </tr>
        """
    
    return template.format(
        execution_time=analysis["execution_time"],
        total_count=analysis["summary"]["total_count"],
        success_count=analysis["summary"]["success_count"],
        failed_count=analysis["summary"]["failed_count"],
        success_rate=analysis["summary"]["success_rate"],
        response_time_section=response_time_section,
        test_details=test_details
    )


def generate_json_report(analysis: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
    """生成JSON报告"""
    report = {
        "report_info": {
            "type": "json",
            "generated_at": analysis["execution_time"],
            "version": "1.0"
        },
        "analysis": analysis,
        "results": results
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def generate_pdf_report(
    analysis: Dict[str, Any],
    results: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> bytes:
    """生成PDF报告"""
    # 这里应该使用PDF生成库如ReportLab
    # 为简化示例，这里返回HTML转PDF的占位符
    html_content = generate_html_report(analysis, results, config)
    
    # 在实际实现中，这里会使用库如weasyprint或reportlab生成PDF
    # import weasyprint
    # pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
    # return pdf_bytes
    
    return html_content.encode('utf-8')  # 临时返回HTML的字节


def generate_excel_report(
    analysis: Dict[str, Any],
    results: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> bytes:
    """生成Excel报告"""
    import io
    import json
    
    # 在实际实现中，这里会使用openpyxl或xlsxwriter生成Excel
    # 为简化示例，返回JSON字节
    report_data = {
        "analysis": analysis,
        "results": results
    }
    
    json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
    return json_str.encode('utf-8')


async def save_report(
    report_type: str,
    content: Any,
    analysis: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> str:
    """保存报告到数据库或文件系统"""
    
    # 生成报告ID
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{report_type}"
    
    # 这里应该保存到数据库或文件系统
    # 为简化示例，只返回报告ID
    logger.info(f"报告已保存: {report_id}")
    
    return report_id


@celery_app.task(bind=True, base=AsyncReportGenerationTask, name="generate_trend_report")
def generate_trend_report(
    self,
    date_range: Dict[str, str],
    test_case_ids: Optional[List[int]] = None,
    environment_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """生成趋势报告
    
    Args:
        date_range: 日期范围 {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        test_case_ids: 测试用例ID列表
        environment_ids: 环境ID列表
    
    Returns:
        趋势报告结果
    """
    
    async def generate_trend():
        try:
            self.update_state(
                state=TaskStatus.STARTED,
                meta={"message": "开始生成趋势报告"}
            )
            
            # 这里应该从数据库查询历史测试数据
            # 为简化示例，返回模拟数据
            trend_data = {
                "date_range": date_range,
                "daily_stats": [
                    {
                        "date": "2024-01-01",
                        "total_tests": 100,
                        "success_rate": 85.0,
                        "avg_response_time": 245.5
                    }
                    # ... 更多日期数据
                ],
                "summary": {
                    "total_executions": 1000,
                    "avg_success_rate": 87.5,
                    "trend": "improving"  # improving, declining, stable
                }
            }
            
            return {
                "status": "success",
                "report_type": "trend",
                "data": trend_data
            }
            
        except Exception as e:
            logger.error(f"趋势报告生成失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(generate_trend())
    finally:
        loop.close()
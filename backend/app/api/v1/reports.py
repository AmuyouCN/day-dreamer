"""
报告管理API路由

提供测试报告的查询、下载、管理接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List
from datetime import datetime
import io
import os

from app.models.user import User
from app.services.report_service import ReportService, TestReport
from app.utils.auth import get_current_user, require_permission
from app.utils.response import success_response, error_response
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()


# 响应模型
class ReportResponse(BaseModel):
    id: int
    report_id: str
    name: str
    type: str
    status: str
    total_tests: int
    success_tests: int
    failed_tests: int
    success_rate: float
    file_size: Optional[int]
    created_by: int
    created_at: str
    expires_at: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
async def list_reports(
    report_type: Optional[str] = Query(None, description="报告类型"),
    status: Optional[str] = Query(None, description="报告状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user)
):
    """获取报告列表"""
    try:
        # 普通用户只能查看自己的报告
        created_by = None if current_user.is_admin else current_user.id
        
        offset = (page - 1) * page_size
        reports, total = await ReportService.list_reports(
            report_type=report_type,
            created_by=created_by,
            status=status,
            offset=offset,
            limit=page_size
        )
        
        # 转换为响应模型
        report_list = []
        for report in reports:
            response_data = ReportResponse(
                id=report.id,
                report_id=report.report_id,
                name=report.name,
                type=report.type,
                status=report.status,
                total_tests=report.total_tests,
                success_tests=report.success_tests,
                failed_tests=report.failed_tests,
                success_rate=report.success_rate,
                file_size=report.file_size,
                created_by=report.created_by,
                created_at=report.created_at.isoformat(),
                expires_at=report.expires_at.isoformat() if report.expires_at else None
            )
            report_list.append(response_data)
        
        return success_response({
            "reports": report_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取报告列表失败: {str(e)}")
        return error_response("获取报告列表失败")


@router.get("/{report_id}", response_model=dict)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取单个报告信息"""
    try:
        report = await ReportService.get_report(report_id)
        
        # 权限检查：普通用户只能查看自己的报告
        if not current_user.is_admin and report.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        
        response_data = ReportResponse(
            id=report.id,
            report_id=report.report_id,
            name=report.name,
            type=report.type,
            status=report.status,
            total_tests=report.total_tests,
            success_tests=report.success_tests,
            failed_tests=report.failed_tests,
            success_rate=report.success_rate,
            file_size=report.file_size,
            created_by=report.created_by,
            created_at=report.created_at.isoformat(),
            expires_at=report.expires_at.isoformat() if report.expires_at else None
        )
        
        # 包含分析数据
        result = {
            "report": response_data,
            "analysis_data": report.analysis_data,
            "config_data": report.config_data
        }
        
        return success_response(result)
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return error_response("获取报告失败")


@router.get("/{report_id}/content")
async def get_report_content(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取报告内容"""
    try:
        report = await ReportService.get_report(report_id)
        
        # 权限检查
        if not current_user.is_admin and report.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        
        content = await ReportService.get_report_content(report_id)
        
        # 根据报告类型设置响应类型
        media_types = {
            "html": "text/html",
            "json": "application/json",
            "pdf": "application/pdf",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        media_type = media_types.get(report.type, "text/plain")
        
        if report.type in ["pdf", "excel"]:
            # 二进制内容
            return Response(
                content=content.encode('utf-8') if isinstance(content, str) else content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.{report.type}"
                }
            )
        else:
            # 文本内容
            return Response(content=content, media_type=media_type)
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"获取报告内容失败: {str(e)}")
        return error_response("获取报告内容失败")


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """下载报告文件"""
    try:
        report = await ReportService.get_report(report_id)
        
        # 权限检查
        if not current_user.is_admin and report.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 如果有文件路径，直接返回文件
        if report.file_path and os.path.exists(report.file_path):
            return FileResponse(
                report.file_path,
                filename=f"{report_id}.{report.type}",
                media_type="application/octet-stream"
            )
        
        # 否则从内容生成文件
        content = await ReportService.get_report_content(report_id)
        
        # 创建内存文件流
        file_like = io.BytesIO()
        if isinstance(content, str):
            file_like.write(content.encode('utf-8'))
        else:
            file_like.write(content)
        file_like.seek(0)
        
        return StreamingResponse(
            io.BytesIO(file_like.getvalue()),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={report_id}.{report.type}"
            }
        )
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}")
        return error_response("下载报告失败")


@router.delete("/{report_id}", response_model=dict)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除报告"""
    try:
        report = await ReportService.get_report(report_id)
        
        # 权限检查：只能删除自己的报告或管理员可以删除所有报告
        if not current_user.is_admin and report.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        
        await ReportService.delete_report(report_id)
        
        return success_response(None, "报告删除成功")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"删除报告失败: {str(e)}")
        return error_response("删除报告失败")


@router.get("/statistics/summary", response_model=dict)
async def get_report_statistics(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """获取报告统计信息"""
    try:
        # 普通用户只能查看自己的统计
        created_by = None if current_user.is_admin else current_user.id
        
        # 解析日期
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        statistics = await ReportService.get_report_statistics(
            start_date=start_dt,
            end_date=end_dt,
            created_by=created_by
        )
        
        return success_response(statistics)
        
    except ValueError as e:
        return error_response(f"日期格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"获取报告统计失败: {str(e)}")
        return error_response("获取报告统计失败")


@router.post("/cleanup", response_model=dict)
async def cleanup_expired_reports(
    max_age_days: int = Query(30, description="最大保留天数"),
    current_user: User = Depends(require_permission("system:maintenance"))
):
    """清理过期报告"""
    try:
        count = await ReportService.cleanup_expired_reports(max_age_days)
        
        return success_response({
            "cleaned_count": count
        }, f"清理了 {count} 个过期报告")
        
    except Exception as e:
        logger.error(f"清理过期报告失败: {str(e)}")
        return error_response("清理过期报告失败")


@router.get("/export/list", response_model=dict)
async def export_report_list(
    report_type: Optional[str] = Query(None, description="报告类型"),
    format: str = Query("json", description="导出格式 (json, csv)"),
    current_user: User = Depends(require_permission("report:export"))
):
    """导出报告列表"""
    try:
        if format not in ["json", "csv"]:
            return error_response("不支持的导出格式")
        
        export_data = await ReportService.export_report_list(
            report_type=report_type,
            format=format
        )
        
        # 设置响应类型
        media_type = "application/json" if format == "json" else "text/csv"
        filename = f"reports.{format}"
        
        return Response(
            content=export_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"导出报告列表失败: {str(e)}")
        return error_response("导出报告列表失败")


@router.get("/types", response_model=dict)
async def get_report_types(
    current_user: User = Depends(get_current_user)
):
    """获取支持的报告类型"""
    try:
        report_types = [
            {
                "type": "html",
                "name": "HTML报告",
                "description": "网页格式的测试报告，支持交互式查看"
            },
            {
                "type": "json",
                "name": "JSON报告",
                "description": "结构化数据格式，便于程序处理"
            },
            {
                "type": "pdf",
                "name": "PDF报告",
                "description": "便携式文档格式，适合打印和分享"
            },
            {
                "type": "excel",
                "name": "Excel报告",
                "description": "电子表格格式，支持数据分析"
            },
            {
                "type": "trend",
                "name": "趋势报告",
                "description": "测试结果趋势分析报告"
            }
        ]
        
        return success_response({
            "report_types": report_types
        })
        
    except Exception as e:
        logger.error(f"获取报告类型失败: {str(e)}")
        return error_response("获取报告类型失败")
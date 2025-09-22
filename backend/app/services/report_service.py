"""
测试报告服务

处理测试报告的存储、查询和管理
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from tortoise.models import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.utils.logger import logger


class TestReport(Model):
    """测试报告模型"""
    
    id = fields.IntField(pk=True, description="主键ID")
    report_id = fields.CharField(max_length=100, unique=True, description="报告ID")
    name = fields.CharField(max_length=200, description="报告名称")
    type = fields.CharField(max_length=50, description="报告类型")
    status = fields.CharField(max_length=20, default="generating", description="报告状态")
    
    # 报告内容
    file_path = fields.CharField(max_length=500, null=True, description="文件路径")
    file_size = fields.IntField(null=True, description="文件大小")
    content = fields.TextField(null=True, description="报告内容")
    
    # 分析数据
    analysis_data = fields.JSONField(null=True, description="分析数据")
    config_data = fields.JSONField(null=True, description="配置数据")
    
    # 统计信息
    total_tests = fields.IntField(default=0, description="总测试数")
    success_tests = fields.IntField(default=0, description="成功测试数")
    failed_tests = fields.IntField(default=0, description="失败测试数")
    success_rate = fields.FloatField(default=0.0, description="成功率")
    
    # 元数据
    created_by = fields.IntField(description="创建者ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    expires_at = fields.DatetimeField(null=True, description="过期时间")
    is_active = fields.BooleanField(default=True, description="是否启用")
    
    class Meta:
        table = "test_reports"
        table_description = "测试报告表"
        indexes = [
            ("report_id",),
            ("type",),
            ("status",),
            ("created_by",),
            ("created_at",),
        ]
    
    def __str__(self):
        return f"{self.name}({self.type})"


class ReportService:
    """报告服务"""
    
    @staticmethod
    async def create_report(
        report_id: str,
        name: str,
        report_type: str,
        created_by: int,
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        analysis_data: Optional[Dict[str, Any]] = None,
        config_data: Optional[Dict[str, Any]] = None,
        expires_hours: int = 72
    ) -> TestReport:
        """创建测试报告"""
        
        # 计算过期时间
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        # 从分析数据中提取统计信息
        total_tests = 0
        success_tests = 0
        failed_tests = 0
        success_rate = 0.0
        
        if analysis_data and "summary" in analysis_data:
            summary = analysis_data["summary"]
            total_tests = summary.get("total_count", 0)
            success_tests = summary.get("success_count", 0)
            failed_tests = summary.get("failed_count", 0)
            success_rate = summary.get("success_rate", 0.0)
        
        # 计算文件大小
        file_size = None
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        elif content:
            file_size = len(content.encode('utf-8'))
        
        report = await TestReport.create(
            report_id=report_id,
            name=name,
            type=report_type,
            content=content,
            file_path=file_path,
            file_size=file_size,
            analysis_data=analysis_data,
            config_data=config_data,
            total_tests=total_tests,
            success_tests=success_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            created_by=created_by,
            expires_at=expires_at,
            status="completed"
        )
        
        logger.info(f"创建测试报告: {report_id} by user {created_by}")
        return report
    
    @staticmethod
    async def get_report(report_id: str) -> TestReport:
        """根据ID获取报告"""
        try:
            return await TestReport.get(report_id=report_id, is_active=True)
        except DoesNotExist:
            raise ValueError(f"报告 {report_id} 不存在")
    
    @staticmethod
    async def get_report_content(report_id: str) -> str:
        """获取报告内容"""
        report = await ReportService.get_report(report_id)
        
        if report.content:
            return report.content
        elif report.file_path and os.path.exists(report.file_path):
            with open(report.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"报告 {report_id} 内容不存在")
    
    @staticmethod
    async def list_reports(
        report_type: Optional[str] = None,
        created_by: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> tuple[List[TestReport], int]:
        """列出报告"""
        
        query = TestReport.filter(is_active=True)
        
        if report_type:
            query = query.filter(type=report_type)
        
        if created_by:
            query = query.filter(created_by=created_by)
        
        if status:
            query = query.filter(status=status)
        
        total = await query.count()
        reports = await query.offset(offset).limit(limit).order_by('-created_at')
        
        return reports, total
    
    @staticmethod
    async def update_report_status(
        report_id: str,
        status: str,
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> TestReport:
        """更新报告状态"""
        
        report = await ReportService.get_report(report_id)
        
        report.status = status
        
        if content:
            report.content = content
            report.file_size = len(content.encode('utf-8'))
        
        if file_path:
            report.file_path = file_path
            if os.path.exists(file_path):
                report.file_size = os.path.getsize(file_path)
        
        if analysis_data:
            report.analysis_data = analysis_data
            
            # 更新统计信息
            if "summary" in analysis_data:
                summary = analysis_data["summary"]
                report.total_tests = summary.get("total_count", 0)
                report.success_tests = summary.get("success_count", 0)
                report.failed_tests = summary.get("failed_count", 0)
                report.success_rate = summary.get("success_rate", 0.0)
        
        await report.save()
        logger.info(f"更新报告状态: {report_id} -> {status}")
        
        return report
    
    @staticmethod
    async def delete_report(report_id: str) -> bool:
        """删除报告（软删除）"""
        report = await ReportService.get_report(report_id)
        
        # 删除文件
        if report.file_path and os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
                logger.info(f"删除报告文件: {report.file_path}")
            except Exception as e:
                logger.error(f"删除报告文件失败: {e}")
        
        # 软删除记录
        report.is_active = False
        await report.save()
        
        logger.info(f"删除报告: {report_id}")
        return True
    
    @staticmethod
    async def cleanup_expired_reports(max_age_days: int = 30) -> int:
        """清理过期报告"""
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        # 查找过期报告
        expired_reports = await TestReport.filter(
            created_at__lt=cutoff_time,
            is_active=True
        )
        
        cleaned_count = 0
        for report in expired_reports:
            try:
                # 删除文件
                if report.file_path and os.path.exists(report.file_path):
                    os.remove(report.file_path)
                
                # 标记为删除
                report.is_active = False
                await report.save()
                
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"清理报告失败 {report.report_id}: {e}")
        
        logger.info(f"清理了 {cleaned_count} 个过期报告")
        return cleaned_count
    
    @staticmethod
    async def get_report_statistics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        created_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取报告统计信息"""
        
        query = TestReport.filter(is_active=True)
        
        if start_date:
            query = query.filter(created_at__gte=start_date)
        
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        if created_by:
            query = query.filter(created_by=created_by)
        
        reports = await query.all()
        
        if not reports:
            return {
                "total_reports": 0,
                "reports_by_type": {},
                "reports_by_status": {},
                "total_tests": 0,
                "total_success_tests": 0,
                "total_failed_tests": 0,
                "average_success_rate": 0.0
            }
        
        # 统计报告类型
        reports_by_type = {}
        reports_by_status = {}
        total_tests = 0
        total_success_tests = 0
        total_failed_tests = 0
        
        for report in reports:
            # 按类型统计
            reports_by_type[report.type] = reports_by_type.get(report.type, 0) + 1
            
            # 按状态统计
            reports_by_status[report.status] = reports_by_status.get(report.status, 0) + 1
            
            # 测试统计
            total_tests += report.total_tests
            total_success_tests += report.success_tests
            total_failed_tests += report.failed_tests
        
        # 计算平均成功率
        average_success_rate = 0.0
        if total_tests > 0:
            average_success_rate = (total_success_tests / total_tests) * 100
        
        return {
            "total_reports": len(reports),
            "reports_by_type": reports_by_type,
            "reports_by_status": reports_by_status,
            "total_tests": total_tests,
            "total_success_tests": total_success_tests,
            "total_failed_tests": total_failed_tests,
            "average_success_rate": round(average_success_rate, 2)
        }
    
    @staticmethod
    async def export_report_list(
        report_type: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """导出报告列表"""
        
        reports, _ = await ReportService.list_reports(
            report_type=report_type,
            limit=1000
        )
        
        export_data = []
        for report in reports:
            data = {
                "report_id": report.report_id,
                "name": report.name,
                "type": report.type,
                "status": report.status,
                "total_tests": report.total_tests,
                "success_tests": report.success_tests,
                "failed_tests": report.failed_tests,
                "success_rate": report.success_rate,
                "created_at": report.created_at.isoformat(),
                "file_size": report.file_size
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
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    @staticmethod
    def get_report_file_path(report_id: str, report_type: str) -> str:
        """生成报告文件路径"""
        
        # 创建报告目录
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # 按日期创建子目录
        date_dir = datetime.now().strftime("%Y%m%d")
        full_dir = os.path.join(reports_dir, date_dir)
        os.makedirs(full_dir, exist_ok=True)
        
        # 文件扩展名
        extensions = {
            "html": ".html",
            "json": ".json",
            "pdf": ".pdf",
            "excel": ".xlsx"
        }
        
        ext = extensions.get(report_type, ".txt")
        filename = f"{report_id}{ext}"
        
        return os.path.join(full_dir, filename)
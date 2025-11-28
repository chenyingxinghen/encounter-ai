"""成长报告API"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.models.growth_report import GrowthReport
from src.services.report_service import ReportService
from src.utils.exceptions import ValidationError, NotFoundError
from src.api.auth_api import verify_token

router = APIRouter(prefix="/api/reports", tags=["reports"])

# 导入共享服务实例
from src.api.dependencies import get_report_service

# 服务实例
report_service = get_report_service()


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    report_type: str  # "weekly", "monthly", "annual"
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


@router.post("/generate", response_model=GrowthReport, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: GenerateReportRequest,
    user_id: str = Depends(verify_token)
):
    """
    生成成长报告
    
    根据指定类型和时间段生成用户成长报告
    """
    try:
        if request.report_type == "weekly":
            report = report_service.generate_weekly_report(user_id)
        elif request.report_type == "monthly":
            report = report_service.generate_monthly_report(user_id)
        elif request.report_type == "annual":
            report = report_service.generate_annual_report(user_id)
        else:
            raise ValidationError(f"不支持的报告类型: {request.report_type}")
        
        return report
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[GrowthReport])
async def list_reports(
    report_type: Optional[str] = Query(None, description="报告类型过滤"),
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(verify_token)
):
    """
    获取报告列表
    
    查询用户的历史报告
    """
    try:
        reports = report_service.get_user_reports(
            user_id=user_id,
            report_type=report_type,
            limit=limit
        )
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{report_id}", response_model=GrowthReport)
async def get_report(
    report_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取报告详情
    
    查询指定报告的详细信息
    """
    try:
        report = report_service.get_report(report_id)
        
        # 验证用户权限
        if report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此报告"
            )
        
        return report
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("pdf", description="下载格式: pdf, json"),
    user_id: str = Depends(verify_token)
):
    """
    下载报告
    
    以指定格式下载报告文件
    """
    try:
        report = report_service.get_report(report_id)
        
        # 验证用户权限
        if report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权下载此报告"
            )
        
        # 生成下载文件
        file_path = report_service.export_report(report_id, format)
        
        return FileResponse(
            path=file_path,
            filename=f"report_{report_id}.{format}",
            media_type="application/octet-stream"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{report_id}/share")
async def share_report(
    report_id: str,
    user_id: str = Depends(verify_token)
):
    """
    分享报告
    
    生成报告分享链接
    """
    try:
        report = report_service.get_report(report_id)
        
        # 验证用户权限
        if report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权分享此报告"
            )
        
        share_link = report_service.create_share_link(report_id)
        
        return {
            "message": "分享链接已生成",
            "report_id": report_id,
            "share_link": share_link,
            "expires_in": "7天"
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/latest/{report_type}", response_model=GrowthReport)
async def get_latest_report(
    report_type: str,
    user_id: str = Depends(verify_token)
):
    """
    获取最新报告
    
    查询指定类型的最新报告
    """
    try:
        report = report_service.get_latest_report(user_id, report_type)
        return report
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

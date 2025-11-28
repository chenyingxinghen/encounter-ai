"""内容审查与举报API"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.models.moderation import ModerationResult, Violation, UserReport, Penalty
from src.services.content_moderation_service import ContentModerationService
from src.utils.exceptions import ValidationError, NotFoundError
from src.api.auth_api import verify_token

router = APIRouter(prefix="/api/moderation", tags=["moderation"])

# 导入共享服务实例
from src.api.dependencies import get_content_moderation_service

# 服务实例
moderation_service = get_content_moderation_service()


class ReportUserRequest(BaseModel):
    """举报用户请求"""
    reported_id: str
    report_type: str  # "harassment", "inappropriate_content", "fake_profile", "other"
    reason: str
    evidence: Optional[List[str]] = []


class AppealRequest(BaseModel):
    """申诉请求"""
    violation_id: str
    appeal_reason: str


class ReviewDecisionRequest(BaseModel):
    """审核决定请求"""
    decision: str  # "confirmed", "dismissed"
    notes: Optional[str] = None


@router.post("/report", response_model=UserReport, status_code=status.HTTP_201_CREATED)
async def report_user(
    request: ReportUserRequest,
    user_id: str = Depends(verify_token)
):
    """
    举报用户
    
    用户举报其他用户的违规行为
    """
    try:
        report = moderation_service.handle_user_report(
            reporter_id=user_id,
            reported_id=request.reported_id,
            report_type=request.report_type,
            reason=request.reason,
            evidence=request.evidence
        )
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


@router.get("/reports", response_model=List[UserReport])
async def get_my_reports(
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token)
):
    """
    获取我的举报记录
    
    查询用户提交的举报记录
    """
    try:
        reports = moderation_service.get_user_reports(
            user_id=user_id,
            status_filter=status_filter,
            limit=limit
        )
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reports/{report_id}", response_model=UserReport)
async def get_report_detail(
    report_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取举报详情
    
    查询指定举报的详细信息
    """
    try:
        report = moderation_service.get_report(report_id)
        
        # 验证用户权限（只有举报人或被举报人可以查看）
        if user_id not in [report.reporter_id, report.reported_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此举报"
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


@router.get("/violations", response_model=List[Violation])
async def get_my_violations(
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token)
):
    """
    获取我的违规记录
    
    查询用户的违规历史
    """
    try:
        violations = moderation_service.get_user_violation_history(user_id)
        return violations[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/violations/{violation_id}", response_model=Violation)
async def get_violation_detail(
    violation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取违规详情
    
    查询指定违规记录的详细信息
    """
    try:
        violation = moderation_service.get_violation(violation_id)
        
        # 验证用户权限
        if violation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此违规记录"
            )
        
        return violation
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


@router.post("/appeal", response_model=dict)
async def submit_appeal(
    request: AppealRequest,
    user_id: str = Depends(verify_token)
):
    """
    提交申诉
    
    用户对违规处罚提出申诉
    """
    try:
        # 验证违规记录属于当前用户
        violation = moderation_service.get_violation(request.violation_id)
        if violation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权对此违规记录申诉"
            )
        
        result = moderation_service.submit_appeal(
            violation_id=request.violation_id,
            user_id=user_id,
            appeal_reason=request.appeal_reason
        )
        
        return {
            "message": "申诉已提交",
            "violation_id": request.violation_id,
            "status": "pending_review",
            "result": result
        }
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


@router.get("/penalties", response_model=List[Penalty])
async def get_my_penalties(
    status_filter: Optional[str] = Query(None, description="状态过滤: active, expired, revoked"),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token)
):
    """
    获取我的处罚记录
    
    查询用户的处罚历史
    """
    try:
        penalties = moderation_service.get_user_penalties(
            user_id=user_id,
            status_filter=status_filter,
            limit=limit
        )
        return penalties
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/penalties/{penalty_id}", response_model=Penalty)
async def get_penalty_detail(
    penalty_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取处罚详情
    
    查询指定处罚的详细信息
    """
    try:
        penalty = moderation_service.get_penalty(penalty_id)
        
        # 验证用户权限
        if penalty.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此处罚记录"
            )
        
        return penalty
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


@router.get("/status", response_model=dict)
async def get_moderation_status(
    user_id: str = Depends(verify_token)
):
    """
    获取审查状态
    
    查询用户当前的审查状态（是否被禁言、封号等）
    """
    try:
        status_info = moderation_service.get_user_moderation_status(user_id)
        return status_info
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

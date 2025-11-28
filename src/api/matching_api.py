"""匹配系统API"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from src.models.matching import Match
from src.services.matching_service import MatchingService
from src.utils.exceptions import ValidationError, NotFoundError
from src.api.auth_api import verify_token

router = APIRouter(prefix="/api/matching", tags=["matching"])

# 导入共享服务实例
from src.api.dependencies import get_matching_service

# 服务实例
matching_service = get_matching_service()


class MatchRequest(BaseModel):
    """匹配请求"""
    scene: str
    limit: Optional[int] = 10


class MatchResponse(BaseModel):
    """匹配响应"""
    matches: List[Match]
    total: int


@router.post("/find", response_model=MatchResponse)
async def find_matches(
    request: MatchRequest,
    user_id: str = Depends(verify_token)
):
    """
    查找匹配对象
    
    根据用户画像和场景查找合适的匹配对象
    """
    try:
        matches = matching_service.find_matches(
            user_id=user_id,
            scene=request.scene,
            limit=request.limit
        )
        
        return MatchResponse(
            matches=matches,
            total=len(matches)
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


@router.get("/score/{target_user_id}", response_model=dict)
async def calculate_match_score(
    target_user_id: str,
    scene: str = Query(..., description="匹配场景"),
    user_id: str = Depends(verify_token)
):
    """
    计算匹配度
    
    计算当前用户与目标用户的匹配度
    """
    try:
        score = matching_service.calculate_match_score(
            user_a=user_id,
            user_b=target_user_id,
            scene=scene
        )
        
        reason = matching_service.get_match_reason(user_id, target_user_id)
        
        return {
            "user_a": user_id,
            "user_b": target_user_id,
            "scene": scene,
            "match_score": score,
            "match_reason": reason
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


@router.get("/history", response_model=List[Match])
async def get_match_history(
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token)
):
    """
    获取匹配历史
    
    查询用户的历史匹配记录
    """
    try:
        matches = matching_service.get_match_history(user_id, limit)
        return matches
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


@router.post("/accept/{match_id}")
async def accept_match(
    match_id: str,
    user_id: str = Depends(verify_token)
):
    """
    接受匹配
    
    用户接受一个匹配请求
    """
    try:
        result = matching_service.accept_match(match_id, user_id)
        return {
            "message": "匹配已接受",
            "match_id": match_id,
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


@router.post("/reject/{match_id}")
async def reject_match(
    match_id: str,
    user_id: str = Depends(verify_token)
):
    """
    拒绝匹配
    
    用户拒绝一个匹配请求
    """
    try:
        result = matching_service.reject_match(match_id, user_id)
        return {
            "message": "匹配已拒绝",
            "match_id": match_id,
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

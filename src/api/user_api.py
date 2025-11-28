"""用户注册与画像构建API"""
from fastapi import APIRouter, HTTPException, status
from src.models.user import (
    User, UserProfile, BigFiveScores,
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.services.user_profile_service import UserProfileService
from src.utils.exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/users", tags=["users"])

# 导入共享服务实例
from src.api.dependencies import get_user_profile_service

# 服务实例
user_service = get_user_profile_service()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegistrationRequest):
    """
    用户注册接口
    
    完成基本信息填写并创建用户账号
    """
    try:
        user = user_service.register_user(request)
        return user
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mbti-test", response_model=dict)
async def submit_mbti_test(request: MBTITestRequest):
    """
    提交MBTI测试问卷
    
    处理用户的MBTI测试答案并返回人格类型
    """
    try:
        mbti_type = user_service.process_mbti_test(request)
        return {
            "user_id": request.user_id,
            "mbti_type": mbti_type,
            "message": "MBTI测试完成"
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/big-five-test", response_model=dict)
async def submit_big_five_test(request: BigFiveTestRequest):
    """
    提交大五人格评估问卷
    
    处理用户的大五人格测试答案并返回各维度得分
    """
    try:
        scores = user_service.process_big_five_test(request)
        return {
            "user_id": request.user_id,
            "scores": scores.dict(),
            "message": "大五人格评估完成"
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/interests", response_model=UserProfile)
async def update_interests(request: InterestSelectionRequest):
    """
    更新用户兴趣标签
    
    用户选择学业、职业和兴趣爱好标签
    """
    try:
        profile = user_service.update_interests(request)
        return profile
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/scenes", response_model=UserProfile)
async def update_scenes(request: SceneSelectionRequest):
    """
    更新用户场景选择
    
    用户选择当前关注的社交场景
    """
    try:
        profile = user_service.update_scenes(request)
        return profile
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/profile/generate", response_model=UserProfile)
async def generate_profile(user_id: str):
    """
    生成初始用户画像
    
    完成所有初始设置后，生成完整的用户画像
    """
    try:
        profile = user_service.generate_initial_profile(user_id)
        return profile
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str):
    """
    获取用户画像
    
    查询指定用户的画像信息
    """
    try:
        profile = user_service.get_profile(user_id)
        return profile
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    获取用户信息
    
    查询指定用户的基本信息和画像
    """
    try:
        user = user_service.get_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/profile/{user_id}/analyze", response_model=dict)
async def analyze_profile_from_conversation(
    user_id: str,
    conversation_id: str
):
    """
    从对话分析并更新画像
    
    分析指定对话的内容，提取关键信息并更新用户画像
    """
    try:
        # 获取对话消息
        from src.api.dependencies import get_conversation_service, get_profile_update_service
        conversation_service = get_conversation_service()
        profile_update_service = get_profile_update_service()
        
        messages = conversation_service.get_messages(conversation_id, limit=100)
        
        # 分析对话
        conversation_data = profile_update_service.analyze_conversation(
            conversation_id=conversation_id,
            messages=messages
        )
        
        # 更新画像
        update_result = profile_update_service.update_profile_from_conversation(
            user_id=user_id,
            conversation_data=conversation_data
        )
        
        # 生成通知
        notification = None
        if update_result.get('should_notify'):
            notification = profile_update_service.generate_profile_update_notification(
                user_id=user_id,
                update_result=update_result
            )
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "analysis": conversation_data,
            "update_result": update_result,
            "notification": notification
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/profile/{user_id}/updates", response_model=list)
async def get_profile_updates(
    user_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    获取画像更新通知
    
    查询用户的画像更新历史和通知
    """
    try:
        # 这里应该从数据库查询更新历史
        # 目前返回示例数据
        from src.api.dependencies import get_profile_update_service
        profile_update_service = get_profile_update_service()
        
        # 实际应用中应该有一个更新历史存储
        # 这里返回空列表作为占位
        updates = []
        
        return updates
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/profile/{user_id}/changes", response_model=dict)
async def get_profile_changes(
    user_id: str,
    since: Optional[datetime] = Query(None, description="查询此时间之后的变化")
):
    """
    获取画像变化详情
    
    查询用户画像在指定时间段内的变化情况
    """
    try:
        profile = user_service.get_profile(user_id)
        
        # 返回当前画像状态
        # 实际应用中应该对比历史快照
        return {
            "user_id": user_id,
            "current_profile": {
                "mbti_type": profile.mbti_type,
                "big_five": profile.big_five.dict() if profile.big_five else None,
                "emotion_stability": profile.emotion_stability,
                "social_energy": profile.social_energy,
                "interests": {
                    "academic": profile.academic_interests,
                    "career": profile.career_interests,
                    "hobby": profile.hobby_interests
                },
                "scenes": profile.current_scenes
            },
            "changes": [],  # 实际应该包含变化历史
            "last_updated": profile.updated_at
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

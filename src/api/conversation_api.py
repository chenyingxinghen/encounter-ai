"""对话管理API"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.models.conversation import Conversation, Message
from src.services.conversation_service import ConversationService
from src.utils.exceptions import ValidationError, NotFoundError
from src.api.auth_api import verify_token

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# 导入共享服务实例
from src.api.dependencies import get_conversation_service

# 服务实例
conversation_service = get_conversation_service()


class CreateConversationRequest(BaseModel):
    """创建对话请求"""
    partner_id: str
    scene: str


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: str
    message_type: Optional[str] = "text"


class ConversationResponse(BaseModel):
    """对话响应"""
    conversation: Conversation
    messages: List[Message]


@router.post("/create", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    user_id: str = Depends(verify_token)
):
    """
    创建对话
    
    在两个用户之间创建新的对话
    """
    try:
        conversation = conversation_service.create_conversation(
            user_a_id=user_id,
            user_b_id=request.partner_id,
            scene=request.scene
        )
        return conversation
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


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200, description="消息数量限制"),
    user_id: str = Depends(verify_token)
):
    """
    获取对话详情
    
    查询对话信息和历史消息
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        # 验证用户权限
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
        
        messages = conversation_service.get_messages(conversation_id, limit)
        
        return ConversationResponse(
            conversation=conversation,
            messages=messages
        )
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


@router.get("/", response_model=List[Conversation])
async def list_conversations(
    status_filter: Optional[str] = Query(None, description="状态过滤: active, paused, ended"),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token)
):
    """
    获取对话列表
    
    查询用户的所有对话
    """
    try:
        conversations = conversation_service.get_user_conversations(
            user_id=user_id,
            status_filter=status_filter,
            limit=limit
        )
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{conversation_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(verify_token)
):
    """
    发送消息
    
    在对话中发送新消息
    """
    try:
        # 验证对话存在且用户有权限
        conversation = conversation_service.get_conversation(conversation_id)
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权在此对话中发送消息"
            )
        
        message = conversation_service.send_message(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=request.content,
            message_type=request.message_type
        )
        return message
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


@router.get("/{conversation_id}/messages", response_model=List[Message])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[datetime] = Query(None, description="获取此时间之前的消息"),
    user_id: str = Depends(verify_token)
):
    """
    获取消息列表
    
    查询对话的历史消息
    """
    try:
        # 验证用户权限
        conversation = conversation_service.get_conversation(conversation_id)
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话的消息"
            )
        
        messages = conversation_service.get_messages(
            conversation_id=conversation_id,
            limit=limit,
            before=before
        )
        return messages
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


@router.post("/{conversation_id}/pause")
async def pause_conversation(
    conversation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    暂停对话
    
    暂停当前对话
    """
    try:
        conversation = conversation_service.pause_conversation(conversation_id, user_id)
        return {
            "message": "对话已暂停",
            "conversation": conversation
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


@router.post("/{conversation_id}/end")
async def end_conversation(
    conversation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    结束对话
    
    结束当前对话
    """
    try:
        conversation = conversation_service.end_conversation(conversation_id, user_id)
        return {
            "message": "对话已结束",
            "conversation": conversation
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


@router.get("/{conversation_id}/ai-suggestions", response_model=dict)
async def get_ai_suggestions(
    conversation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取AI话题建议
    
    当对话出现沉默时，AI助手提供话题建议
    """
    try:
        # 验证用户权限
        conversation = conversation_service.get_conversation(conversation_id)
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
        
        # 获取最近消息
        messages = conversation_service.get_messages(conversation_id, limit=20)
        
        # 检测沉默
        from src.api.dependencies import get_dialogue_assistant_service
        assistant_service = get_dialogue_assistant_service()
        
        is_silent, silence_type = assistant_service.detect_silence(
            conversation_id=conversation_id,
            recent_messages=messages
        )
        
        if not is_silent:
            return {
                "has_suggestion": False,
                "message": "对话进行顺畅，暂无建议"
            }
        
        # 检查是否应该介入
        should_intervene = assistant_service.should_intervene(conversation_id, user_id)
        
        if not should_intervene:
            return {
                "has_suggestion": False,
                "message": "AI助手暂时不介入"
            }
        
        # 生成话题建议
        suggestion = assistant_service.generate_topic_suggestion(
            conversation_id=conversation_id,
            scene=conversation.scene,
            recent_messages=messages,
            silence_type=silence_type
        )
        
        # 记录介入
        intervention = assistant_service.record_intervention(
            conversation_id=conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content=suggestion
        )
        
        return {
            "has_suggestion": True,
            "intervention_id": intervention.intervention_id,
            "suggestion": suggestion,
            "silence_type": silence_type.type if silence_type else None,
            "silence_duration": assistant_service.get_silence_duration(conversation_id)
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


class AIInterventionResponse(BaseModel):
    """AI介入响应"""
    response: str  # accepted, rejected, ignored


@router.post("/{conversation_id}/ai-intervention/{intervention_id}/respond")
async def respond_to_ai_intervention(
    conversation_id: str,
    intervention_id: str,
    request: AIInterventionResponse,
    user_id: str = Depends(verify_token)
):
    """
    响应AI介入
    
    用户对AI助手的建议做出响应（接受/拒绝/忽略）
    """
    try:
        # 验证用户权限
        conversation = conversation_service.get_conversation(conversation_id)
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
        
        # 更新用户响应
        from src.api.dependencies import get_dialogue_assistant_service
        assistant_service = get_dialogue_assistant_service()
        
        intervention = assistant_service.update_user_response(
            intervention_id=intervention_id,
            conversation_id=conversation_id,
            response=request.response
        )
        
        # 如果用户拒绝，记录偏好
        if request.response == "rejected":
            assistant_service.record_user_preference(
                user_id=user_id,
                ai_intervention_enabled=False
            )
        
        return {
            "message": "响应已记录",
            "intervention_id": intervention_id,
            "response": request.response
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{conversation_id}/ai-history", response_model=list)
async def get_ai_intervention_history(
    conversation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    获取AI介入历史
    
    查询对话中AI助手的所有介入记录
    """
    try:
        # 验证用户权限
        conversation = conversation_service.get_conversation(conversation_id)
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
        
        # 获取介入历史
        from src.api.dependencies import get_dialogue_assistant_service
        assistant_service = get_dialogue_assistant_service()
        
        interventions = assistant_service.get_intervention_history(conversation_id)
        
        return interventions
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

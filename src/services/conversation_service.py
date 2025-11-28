"""对话系统服务"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from src.models.conversation import (
    Conversation,
    Message,
    ConversationCreateRequest,
    MessageSendRequest,
    ConversationHistoryRequest,
    ConversationStatusUpdateRequest
)
from src.utils.logger import get_logger
from src.utils.exceptions import (
    ConversationNotFoundError,
    InvalidConversationStateError,
    UnauthorizedAccessError
)

logger = get_logger(__name__)


class ConversationService:
    """对话系统服务类"""
    
    def __init__(self):
        """初始化对话服务"""
        # 使用内存存储（实际应用中应使用数据库）
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, List[Message]] = {}
        logger.info("ConversationService initialized")
    
    def create_conversation(self, request: ConversationCreateRequest) -> Conversation:
        """
        创建新对话
        
        Args:
            request: 创建对话请求
            
        Returns:
            Conversation: 创建的对话对象
        """
        conversation_id = str(uuid.uuid4())
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_a_id=request.user_a_id,
            user_b_id=request.user_b_id,
            scene=request.scene,
            status="active",
            started_at=datetime.now(),
            message_count=0,
            silence_count=0,
            ai_intervention_count=0
        )
        
        self.conversations[conversation_id] = conversation
        self.messages[conversation_id] = []
        
        logger.info(
            f"Created conversation {conversation_id} between "
            f"{request.user_a_id} and {request.user_b_id} in scene {request.scene}"
        )
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Conversation:
        """
        获取对话信息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Conversation: 对话对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        if conversation_id not in self.conversations:
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        
        return self.conversations[conversation_id]
    
    def send_message(self, request: MessageSendRequest) -> Message:
        """
        发送消息
        
        Args:
            request: 发送消息请求
            
        Returns:
            Message: 发送的消息对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
            InvalidConversationStateError: 对话状态不允许发送消息
            UnauthorizedAccessError: 发送者不是对话参与者
        """
        # 验证对话存在
        conversation = self.get_conversation(request.conversation_id)
        
        # 验证对话状态
        if conversation.status != "active":
            raise InvalidConversationStateError(
                f"Cannot send message in {conversation.status} conversation"
            )
        
        # 验证发送者是对话参与者
        if request.sender_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise UnauthorizedAccessError(
                f"User {request.sender_id} is not a participant in conversation {request.conversation_id}"
            )
        
        # 创建消息
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            conversation_id=request.conversation_id,
            sender_id=request.sender_id,
            content=request.content,
            message_type=request.message_type,
            timestamp=datetime.now()
        )
        
        # 存储消息
        if request.conversation_id not in self.messages:
            self.messages[request.conversation_id] = []
        self.messages[request.conversation_id].append(message)
        
        # 更新对话统计
        conversation.message_count += 1
        
        logger.info(
            f"Message {message_id} sent by {request.sender_id} "
            f"in conversation {request.conversation_id}"
        )
        
        return message
    
    def get_conversation_history(
        self,
        request: ConversationHistoryRequest
    ) -> List[Message]:
        """
        获取对话历史记录
        
        Args:
            request: 对话历史查询请求
            
        Returns:
            List[Message]: 消息列表
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        # 验证对话存在
        self.get_conversation(request.conversation_id)
        
        # 获取消息列表
        messages = self.messages.get(request.conversation_id, [])
        
        # 按时间戳过滤
        if request.before_timestamp:
            messages = [
                msg for msg in messages
                if msg.timestamp < request.before_timestamp
            ]
        
        # 按时间倒序排序（最新的在前）
        messages = sorted(messages, key=lambda m: m.timestamp, reverse=True)
        
        # 应用分页
        start = request.offset
        end = start + request.limit
        messages = messages[start:end]
        
        logger.info(
            f"Retrieved {len(messages)} messages for conversation {request.conversation_id}"
        )
        
        return messages
    
    def update_conversation_status(
        self,
        request: ConversationStatusUpdateRequest
    ) -> Conversation:
        """
        更新对话状态
        
        Args:
            request: 对话状态更新请求
            
        Returns:
            Conversation: 更新后的对话对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        conversation = self.get_conversation(request.conversation_id)
        
        old_status = conversation.status
        conversation.status = request.status
        
        # 如果状态变为ended，记录结束时间
        if request.status == "ended" and old_status != "ended":
            conversation.ended_at = datetime.now()
        
        logger.info(
            f"Conversation {request.conversation_id} status updated "
            f"from {old_status} to {request.status}"
        )
        
        return conversation
    
    def get_user_conversations(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Conversation]:
        """
        获取用户的所有对话
        
        Args:
            user_id: 用户ID
            status: 可选的状态过滤（active, paused, ended）
            
        Returns:
            List[Conversation]: 对话列表
        """
        conversations = [
            conv for conv in self.conversations.values()
            if user_id in [conv.user_a_id, conv.user_b_id]
        ]
        
        # 按状态过滤
        if status:
            conversations = [
                conv for conv in conversations
                if conv.status == status
            ]
        
        # 按开始时间倒序排序
        conversations = sorted(
            conversations,
            key=lambda c: c.started_at,
            reverse=True
        )
        
        logger.info(
            f"Retrieved {len(conversations)} conversations for user {user_id}"
        )
        
        return conversations
    
    def increment_silence_count(self, conversation_id: str) -> Conversation:
        """
        增加对话的沉默计数
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Conversation: 更新后的对话对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        conversation.silence_count += 1
        
        logger.info(
            f"Silence count incremented for conversation {conversation_id}: "
            f"{conversation.silence_count}"
        )
        
        return conversation
    
    def increment_ai_intervention_count(self, conversation_id: str) -> Conversation:
        """
        增加对话的AI介入计数
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Conversation: 更新后的对话对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        conversation.ai_intervention_count += 1
        
        logger.info(
            f"AI intervention count incremented for conversation {conversation_id}: "
            f"{conversation.ai_intervention_count}"
        )
        
        return conversation
    
    def update_quality_metrics(
        self,
        conversation_id: str,
        topic_depth_score: Optional[float] = None,
        emotion_sync_score: Optional[float] = None,
        satisfaction_score: Optional[float] = None
    ) -> Conversation:
        """
        更新对话质量指标
        
        Args:
            conversation_id: 对话ID
            topic_depth_score: 话题深度得分
            emotion_sync_score: 情感同步性得分
            satisfaction_score: 满意度得分
            
        Returns:
            Conversation: 更新后的对话对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        
        if topic_depth_score is not None:
            conversation.topic_depth_score = topic_depth_score
        if emotion_sync_score is not None:
            conversation.emotion_sync_score = emotion_sync_score
        if satisfaction_score is not None:
            conversation.satisfaction_score = satisfaction_score
        
        logger.info(
            f"Quality metrics updated for conversation {conversation_id}"
        )
        
        return conversation

    def get_user_conversations(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[Conversation]:
        """
        获取用户的对话列表
        
        Args:
            user_id: 用户ID
            status_filter: 状态过滤
            limit: 返回数量限制
            
        Returns:
            List[Conversation]: 对话列表
        """
        user_conversations = [
            conv for conv in self._conversations.values()
            if conv.user_a_id == user_id or conv.user_b_id == user_id
        ]
        
        # 状态过滤
        if status_filter:
            user_conversations = [
                conv for conv in user_conversations
                if conv.status == status_filter
            ]
        
        # 按开始时间倒序排序
        user_conversations.sort(key=lambda x: x.started_at, reverse=True)
        
        return user_conversations[:limit]
    
    def pause_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        """
        暂停对话
        
        Args:
            conversation_id: 对话ID
            user_id: 用户ID
            
        Returns:
            Conversation: 更新后的对话
        """
        conversation = self.get_conversation(conversation_id)
        
        # 验证用户权限
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise ValidationError("User not authorized to pause this conversation")
        
        # 更新状态
        conversation.status = "paused"
        
        self.logger.info(f"Conversation {conversation_id} paused by user {user_id}")
        
        return conversation
    
    def end_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        """
        结束对话
        
        Args:
            conversation_id: 对话ID
            user_id: 用户ID
            
        Returns:
            Conversation: 更新后的对话
        """
        conversation = self.get_conversation(conversation_id)
        
        # 验证用户权限
        if user_id not in [conversation.user_a_id, conversation.user_b_id]:
            raise ValidationError("User not authorized to end this conversation")
        
        # 更新状态
        conversation.status = "ended"
        conversation.ended_at = datetime.now()
        
        self.logger.info(f"Conversation {conversation_id} ended by user {user_id}")
        
        return conversation

"""对话系统测试"""
import pytest
from datetime import datetime, timedelta
from src.models.conversation import (
    Conversation,
    Message,
    ConversationCreateRequest,
    MessageSendRequest,
    ConversationHistoryRequest,
    ConversationStatusUpdateRequest
)
from src.services.conversation_service import ConversationService
from src.utils.exceptions import (
    ConversationNotFoundError,
    InvalidConversationStateError,
    UnauthorizedAccessError
)


class TestConversationModels:
    """测试对话数据模型"""
    
    def test_message_creation(self):
        """测试消息创建"""
        message = Message(
            message_id="msg_001",
            conversation_id="conv_001",
            sender_id="user_001",
            content="Hello, how are you?",
            message_type="text",
            timestamp=datetime.now()
        )
        
        assert message.message_id == "msg_001"
        assert message.conversation_id == "conv_001"
        assert message.sender_id == "user_001"
        assert message.content == "Hello, how are you?"
        assert message.message_type == "text"
        assert message.emotion is None
        assert message.emotion_intensity is None
    
    def test_message_with_emotion(self):
        """测试带情绪的消息"""
        message = Message(
            message_id="msg_002",
            conversation_id="conv_001",
            sender_id="user_001",
            content="I'm feeling great!",
            message_type="text",
            emotion="positive",
            emotion_intensity=0.8,
            timestamp=datetime.now()
        )
        
        assert message.emotion == "positive"
        assert message.emotion_intensity == 0.8
    
    def test_message_invalid_type(self):
        """测试无效的消息类型"""
        with pytest.raises(ValueError, match="Invalid message type"):
            Message(
                message_id="msg_003",
                conversation_id="conv_001",
                sender_id="user_001",
                content="Test",
                message_type="invalid",
                timestamp=datetime.now()
            )
    
    def test_message_invalid_emotion(self):
        """测试无效的情绪类型"""
        with pytest.raises(ValueError, match="Invalid emotion"):
            Message(
                message_id="msg_004",
                conversation_id="conv_001",
                sender_id="user_001",
                content="Test",
                message_type="text",
                emotion="invalid",
                timestamp=datetime.now()
            )
    
    def test_conversation_creation(self):
        """测试对话创建"""
        conversation = Conversation(
            conversation_id="conv_001",
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室",
            status="active",
            started_at=datetime.now()
        )
        
        assert conversation.conversation_id == "conv_001"
        assert conversation.user_a_id == "user_001"
        assert conversation.user_b_id == "user_002"
        assert conversation.scene == "考研自习室"
        assert conversation.status == "active"
        assert conversation.message_count == 0
        assert conversation.silence_count == 0
        assert conversation.ai_intervention_count == 0
    
    def test_conversation_invalid_status(self):
        """测试无效的对话状态"""
        with pytest.raises(ValueError, match="Invalid status"):
            Conversation(
                conversation_id="conv_002",
                user_a_id="user_001",
                user_b_id="user_002",
                scene="考研自习室",
                status="invalid",
                started_at=datetime.now()
            )
    
    def test_conversation_invalid_scene(self):
        """测试无效的场景"""
        with pytest.raises(ValueError, match="Invalid scene"):
            Conversation(
                conversation_id="conv_003",
                user_a_id="user_001",
                user_b_id="user_002",
                scene="invalid_scene",
                status="active",
                started_at=datetime.now()
            )
    
    def test_conversation_create_request(self):
        """测试创建对话请求"""
        request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="职业咨询室"
        )
        
        assert request.user_a_id == "user_001"
        assert request.user_b_id == "user_002"
        assert request.scene == "职业咨询室"
    
    def test_conversation_create_request_same_users(self):
        """测试创建对话请求时用户相同"""
        with pytest.raises(ValueError, match="must be different"):
            ConversationCreateRequest(
                user_a_id="user_001",
                user_b_id="user_001",
                scene="心理树洞"
            )


class TestConversationService:
    """测试对话服务"""
    
    @pytest.fixture
    def service(self):
        """创建对话服务实例"""
        return ConversationService()
    
    @pytest.fixture
    def sample_conversation(self, service):
        """创建示例对话"""
        request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室"
        )
        return service.create_conversation(request)
    
    def test_create_conversation(self, service):
        """测试创建对话"""
        request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室"
        )
        
        conversation = service.create_conversation(request)
        
        assert conversation.conversation_id is not None
        assert conversation.user_a_id == "user_001"
        assert conversation.user_b_id == "user_002"
        assert conversation.scene == "考研自习室"
        assert conversation.status == "active"
        assert conversation.message_count == 0
    
    def test_get_conversation(self, service, sample_conversation):
        """测试获取对话"""
        conversation = service.get_conversation(sample_conversation.conversation_id)
        
        assert conversation.conversation_id == sample_conversation.conversation_id
        assert conversation.user_a_id == "user_001"
        assert conversation.user_b_id == "user_002"
    
    def test_get_nonexistent_conversation(self, service):
        """测试获取不存在的对话"""
        with pytest.raises(ConversationNotFoundError):
            service.get_conversation("nonexistent_id")
    
    def test_send_message(self, service, sample_conversation):
        """测试发送消息"""
        request = MessageSendRequest(
            conversation_id=sample_conversation.conversation_id,
            sender_id="user_001",
            content="Hello, how are you?",
            message_type="text"
        )
        
        message = service.send_message(request)
        
        assert message.message_id is not None
        assert message.conversation_id == sample_conversation.conversation_id
        assert message.sender_id == "user_001"
        assert message.content == "Hello, how are you?"
        assert message.message_type == "text"
        
        # 验证对话消息计数增加
        conversation = service.get_conversation(sample_conversation.conversation_id)
        assert conversation.message_count == 1
    
    def test_send_message_to_nonexistent_conversation(self, service):
        """测试向不存在的对话发送消息"""
        request = MessageSendRequest(
            conversation_id="nonexistent_id",
            sender_id="user_001",
            content="Test",
            message_type="text"
        )
        
        with pytest.raises(ConversationNotFoundError):
            service.send_message(request)
    
    def test_send_message_to_ended_conversation(self, service, sample_conversation):
        """测试向已结束的对话发送消息"""
        # 结束对话
        update_request = ConversationStatusUpdateRequest(
            conversation_id=sample_conversation.conversation_id,
            status="ended"
        )
        service.update_conversation_status(update_request)
        
        # 尝试发送消息
        message_request = MessageSendRequest(
            conversation_id=sample_conversation.conversation_id,
            sender_id="user_001",
            content="Test",
            message_type="text"
        )
        
        with pytest.raises(InvalidConversationStateError):
            service.send_message(message_request)
    
    def test_send_message_unauthorized_user(self, service, sample_conversation):
        """测试非参与者发送消息"""
        request = MessageSendRequest(
            conversation_id=sample_conversation.conversation_id,
            sender_id="user_003",  # 不是对话参与者
            content="Test",
            message_type="text"
        )
        
        with pytest.raises(UnauthorizedAccessError):
            service.send_message(request)
    
    def test_get_conversation_history(self, service, sample_conversation):
        """测试获取对话历史"""
        # 发送几条消息
        for i in range(5):
            request = MessageSendRequest(
                conversation_id=sample_conversation.conversation_id,
                sender_id="user_001" if i % 2 == 0 else "user_002",
                content=f"Message {i}",
                message_type="text"
            )
            service.send_message(request)
        
        # 获取历史记录
        history_request = ConversationHistoryRequest(
            conversation_id=sample_conversation.conversation_id,
            limit=10,
            offset=0
        )
        
        messages = service.get_conversation_history(history_request)
        
        assert len(messages) == 5
        # 验证按时间倒序排序（最新的在前）
        for i in range(len(messages) - 1):
            assert messages[i].timestamp >= messages[i + 1].timestamp
    
    def test_get_conversation_history_with_pagination(self, service, sample_conversation):
        """测试分页获取对话历史"""
        # 发送10条消息
        for i in range(10):
            request = MessageSendRequest(
                conversation_id=sample_conversation.conversation_id,
                sender_id="user_001",
                content=f"Message {i}",
                message_type="text"
            )
            service.send_message(request)
        
        # 获取第一页
        history_request = ConversationHistoryRequest(
            conversation_id=sample_conversation.conversation_id,
            limit=5,
            offset=0
        )
        messages_page1 = service.get_conversation_history(history_request)
        assert len(messages_page1) == 5
        
        # 获取第二页
        history_request.offset = 5
        messages_page2 = service.get_conversation_history(history_request)
        assert len(messages_page2) == 5
        
        # 验证没有重复
        page1_ids = {msg.message_id for msg in messages_page1}
        page2_ids = {msg.message_id for msg in messages_page2}
        assert len(page1_ids & page2_ids) == 0
    
    def test_update_conversation_status(self, service, sample_conversation):
        """测试更新对话状态"""
        request = ConversationStatusUpdateRequest(
            conversation_id=sample_conversation.conversation_id,
            status="paused"
        )
        
        conversation = service.update_conversation_status(request)
        
        assert conversation.status == "paused"
    
    def test_update_conversation_status_to_ended(self, service, sample_conversation):
        """测试将对话状态更新为已结束"""
        request = ConversationStatusUpdateRequest(
            conversation_id=sample_conversation.conversation_id,
            status="ended"
        )
        
        conversation = service.update_conversation_status(request)
        
        assert conversation.status == "ended"
        assert conversation.ended_at is not None
    
    def test_get_user_conversations(self, service):
        """测试获取用户的所有对话"""
        # 创建多个对话
        for i in range(3):
            request = ConversationCreateRequest(
                user_a_id="user_001",
                user_b_id=f"user_{i+2:03d}",
                scene="考研自习室"
            )
            service.create_conversation(request)
        
        # 获取用户的对话
        conversations = service.get_user_conversations("user_001")
        
        assert len(conversations) == 3
        # 验证所有对话都包含该用户
        for conv in conversations:
            assert "user_001" in [conv.user_a_id, conv.user_b_id]
    
    def test_get_user_conversations_with_status_filter(self, service):
        """测试按状态过滤用户对话"""
        # 创建对话并设置不同状态
        conv1_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室"
        )
        conv1 = service.create_conversation(conv1_request)
        
        conv2_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_003",
            scene="职业咨询室"
        )
        conv2 = service.create_conversation(conv2_request)
        
        # 结束第二个对话
        update_request = ConversationStatusUpdateRequest(
            conversation_id=conv2.conversation_id,
            status="ended"
        )
        service.update_conversation_status(update_request)
        
        # 获取活跃对话
        active_conversations = service.get_user_conversations("user_001", status="active")
        assert len(active_conversations) == 1
        assert active_conversations[0].conversation_id == conv1.conversation_id
        
        # 获取已结束对话
        ended_conversations = service.get_user_conversations("user_001", status="ended")
        assert len(ended_conversations) == 1
        assert ended_conversations[0].conversation_id == conv2.conversation_id
    
    def test_increment_silence_count(self, service, sample_conversation):
        """测试增加沉默计数"""
        initial_count = sample_conversation.silence_count
        
        conversation = service.increment_silence_count(sample_conversation.conversation_id)
        
        assert conversation.silence_count == initial_count + 1
    
    def test_increment_ai_intervention_count(self, service, sample_conversation):
        """测试增加AI介入计数"""
        initial_count = sample_conversation.ai_intervention_count
        
        conversation = service.increment_ai_intervention_count(sample_conversation.conversation_id)
        
        assert conversation.ai_intervention_count == initial_count + 1
    
    def test_update_quality_metrics(self, service, sample_conversation):
        """测试更新质量指标"""
        conversation = service.update_quality_metrics(
            conversation_id=sample_conversation.conversation_id,
            topic_depth_score=7.5,
            emotion_sync_score=0.85,
            satisfaction_score=4.2
        )
        
        assert conversation.topic_depth_score == 7.5
        assert conversation.emotion_sync_score == 0.85
        assert conversation.satisfaction_score == 4.2
    
    def test_update_partial_quality_metrics(self, service, sample_conversation):
        """测试部分更新质量指标"""
        # 先设置所有指标
        service.update_quality_metrics(
            conversation_id=sample_conversation.conversation_id,
            topic_depth_score=5.0,
            emotion_sync_score=0.5,
            satisfaction_score=3.0
        )
        
        # 只更新部分指标
        conversation = service.update_quality_metrics(
            conversation_id=sample_conversation.conversation_id,
            topic_depth_score=8.0
        )
        
        assert conversation.topic_depth_score == 8.0
        assert conversation.emotion_sync_score == 0.5  # 保持不变
        assert conversation.satisfaction_score == 3.0  # 保持不变


class TestConversationIntegration:
    """测试对话系统集成场景"""
    
    @pytest.fixture
    def service(self):
        """创建对话服务实例"""
        return ConversationService()
    
    def test_complete_conversation_flow(self, service):
        """测试完整的对话流程"""
        # 1. 创建对话
        create_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室"
        )
        conversation = service.create_conversation(create_request)
        assert conversation.status == "active"
        
        # 2. 用户A发送消息
        msg1_request = MessageSendRequest(
            conversation_id=conversation.conversation_id,
            sender_id="user_001",
            content="你好，你也在准备考研吗？",
            message_type="text"
        )
        msg1 = service.send_message(msg1_request)
        assert msg1.sender_id == "user_001"
        
        # 3. 用户B回复
        msg2_request = MessageSendRequest(
            conversation_id=conversation.conversation_id,
            sender_id="user_002",
            content="是的，我在准备计算机专业的考研",
            message_type="text"
        )
        msg2 = service.send_message(msg2_request)
        assert msg2.sender_id == "user_002"
        
        # 4. 检查对话统计
        conversation = service.get_conversation(conversation.conversation_id)
        assert conversation.message_count == 2
        
        # 5. 获取对话历史
        history_request = ConversationHistoryRequest(
            conversation_id=conversation.conversation_id,
            limit=10,
            offset=0
        )
        messages = service.get_conversation_history(history_request)
        assert len(messages) == 2
        
        # 6. 更新质量指标
        service.update_quality_metrics(
            conversation_id=conversation.conversation_id,
            topic_depth_score=8.0,
            emotion_sync_score=0.9
        )
        
        # 7. 结束对话
        end_request = ConversationStatusUpdateRequest(
            conversation_id=conversation.conversation_id,
            status="ended"
        )
        conversation = service.update_conversation_status(end_request)
        assert conversation.status == "ended"
        assert conversation.ended_at is not None

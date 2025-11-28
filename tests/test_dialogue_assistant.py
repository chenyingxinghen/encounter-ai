"""AI对话助手服务测试"""
import pytest
from datetime import datetime, timedelta
from src.services.dialogue_assistant_service import DialogueAssistantService
from src.models.conversation import Message, AIIntervention, SilenceType, UserPreference


class TestDialogueAssistantService:
    """测试AI对话助手服务"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return DialogueAssistantService()
    
    @pytest.fixture
    def sample_messages(self):
        """创建示例消息列表"""
        base_time = datetime.now() - timedelta(minutes=5)
        messages = []
        
        for i in range(5):
            msg = Message(
                message_id=f"msg_{i}",
                conversation_id="conv_1",
                sender_id=f"user_{i % 2}",
                content=f"这是第{i+1}条消息，内容比较长，超过30个字符",
                timestamp=base_time + timedelta(seconds=i * 30)
            )
            messages.append(msg)
        
        return messages
    
    def test_detect_silence_time_based(self, service):
        """测试基于时间的沉默检测"""
        conversation_id = "conv_1"
        
        # 设置最后消息时间为20秒前（超过15秒阈值）
        service.last_message_time[conversation_id] = datetime.now() - timedelta(seconds=20)
        
        is_silent, silence_type = service.detect_silence(conversation_id, [])
        
        assert is_silent is True
        assert silence_type is not None
        assert silence_type.type in ["introverted", "anxious", "none"]
    
    def test_detect_silence_short_messages(self, service):
        """测试基于短消息的沉默检测"""
        conversation_id = "conv_2"
        
        # 创建3条短消息
        short_messages = []
        for i in range(3):
            msg = Message(
                message_id=f"msg_{i}",
                conversation_id=conversation_id,
                sender_id=f"user_{i % 2}",
                content="短消息",  # 少于30字符
                timestamp=datetime.now()
            )
            short_messages.append(msg)
        
        is_silent, silence_type = service.detect_silence(conversation_id, short_messages)
        
        assert is_silent is True
        assert silence_type is not None
    
    def test_detect_no_silence(self, service):
        """测试无沉默情况"""
        conversation_id = "conv_3"
        
        # 创建长消息（超过30字符）
        long_messages = []
        for i in range(5):
            msg = Message(
                message_id=f"msg_{i}",
                conversation_id=conversation_id,
                sender_id=f"user_{i % 2}",
                content=f"这是第{i+1}条消息，内容比较长，超过30个字符，所以不会触发短消息沉默",
                timestamp=datetime.now()
            )
            long_messages.append(msg)
        
        # 设置最后消息时间为5秒前（未超过阈值）
        service.last_message_time[conversation_id] = datetime.now() - timedelta(seconds=5)
        
        is_silent, silence_type = service.detect_silence(conversation_id, long_messages)
        
        assert is_silent is False
        assert silence_type is None
    
    def test_identify_silence_type_anxious(self, service):
        """测试识别焦虑型沉默"""
        # 创建带有焦虑情绪的消息
        anxious_messages = []
        for i in range(5):
            msg = Message(
                message_id=f"msg_{i}",
                conversation_id="conv_1",
                sender_id="user_1",
                content="我有点紧张",
                emotion="anxious",
                emotion_intensity=0.8,
                timestamp=datetime.now()
            )
            anxious_messages.append(msg)
        
        silence_type = service._identify_silence_type(anxious_messages)
        
        assert silence_type.type == "anxious"
        assert silence_type.confidence > 0.5
    
    def test_identify_silence_type_introverted(self, service):
        """测试识别内向型沉默"""
        # 创建中性情绪的消息
        neutral_messages = []
        for i in range(5):
            msg = Message(
                message_id=f"msg_{i}",
                conversation_id="conv_1",
                sender_id="user_1",
                content="嗯，好的",
                emotion="neutral",
                emotion_intensity=0.5,
                timestamp=datetime.now()
            )
            neutral_messages.append(msg)
        
        silence_type = service._identify_silence_type(neutral_messages)
        
        assert silence_type.type == "introverted"
    
    def test_should_intervene_enabled(self, service):
        """测试应该介入的情况"""
        conversation_id = "conv_1"
        user_id = "user_1"
        
        # 用户启用AI介入
        service.user_preferences[user_id] = UserPreference(
            user_id=user_id,
            ai_intervention_enabled=True
        )
        
        should = service.should_intervene(conversation_id, user_id)
        
        assert should is True
    
    def test_should_intervene_disabled(self, service):
        """测试用户禁用AI介入"""
        conversation_id = "conv_1"
        user_id = "user_1"
        
        # 用户禁用AI介入
        service.user_preferences[user_id] = UserPreference(
            user_id=user_id,
            ai_intervention_enabled=False
        )
        
        should = service.should_intervene(conversation_id, user_id)
        
        assert should is False
    
    def test_should_intervene_cooldown(self, service):
        """测试介入冷却期"""
        conversation_id = "conv_1"
        user_id = "user_1"
        
        # 记录一次最近的介入（5分钟前）
        recent_intervention = AIIntervention(
            intervention_id="int_1",
            conversation_id=conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content="建议话题",
            timestamp=datetime.now() - timedelta(minutes=5)
        )
        service.interventions[conversation_id] = [recent_intervention]
        
        should = service.should_intervene(conversation_id, user_id)
        
        # 5分钟 < 20分钟冷却期，不应该介入
        assert should is False
    
    def test_should_intervene_after_cooldown(self, service):
        """测试冷却期后可以介入"""
        conversation_id = "conv_1"
        user_id = "user_1"
        
        # 记录一次较早的介入（25分钟前）
        old_intervention = AIIntervention(
            intervention_id="int_1",
            conversation_id=conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content="建议话题",
            timestamp=datetime.now() - timedelta(minutes=25)
        )
        service.interventions[conversation_id] = [old_intervention]
        
        should = service.should_intervene(conversation_id, user_id)
        
        # 25分钟 > 20分钟冷却期，应该可以介入
        assert should is True
    
    def test_generate_topic_suggestion_exam_scene(self, service):
        """测试生成考研场景的话题建议"""
        conversation_id = "conv_1"
        scene = "考研自习室"
        
        suggestion = service.generate_topic_suggestion(
            conversation_id,
            scene,
            [],
            None
        )
        
        assert isinstance(suggestion, str)
        assert len(suggestion) > 0
    
    def test_generate_topic_suggestion_with_anxious_type(self, service):
        """测试为焦虑型沉默生成话题建议"""
        conversation_id = "conv_1"
        scene = "心理树洞"
        silence_type = SilenceType(type="anxious", confidence=0.8)
        
        suggestion = service.generate_topic_suggestion(
            conversation_id,
            scene,
            [],
            silence_type
        )
        
        assert isinstance(suggestion, str)
        assert len(suggestion) > 0
        # 焦虑型应该有安慰性前缀
        assert "紧张" in suggestion or "慢慢来" in suggestion or len(suggestion) > 10
    
    def test_provide_emotional_support_anxious(self, service):
        """测试提供焦虑情绪支持"""
        user_id = "user_1"
        emotion = "anxious"
        
        support = service.provide_emotional_support(user_id, emotion, [])
        
        assert isinstance(support, str)
        assert len(support) > 0
    
    def test_provide_emotional_support_negative(self, service):
        """测试提供负面情绪支持"""
        user_id = "user_1"
        emotion = "negative"
        
        support = service.provide_emotional_support(user_id, emotion, [])
        
        assert isinstance(support, str)
        assert len(support) > 0
    
    def test_record_intervention(self, service):
        """测试记录AI介入"""
        conversation_id = "conv_1"
        
        intervention = service.record_intervention(
            conversation_id=conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content="建议聊聊考研进度"
        )
        
        assert intervention.intervention_id is not None
        assert intervention.conversation_id == conversation_id
        assert intervention.trigger_type == "silence"
        assert intervention.intervention_type == "topic_suggestion"
        assert intervention.user_response is None
        
        # 验证已存储
        assert conversation_id in service.interventions
        assert len(service.interventions[conversation_id]) == 1
    
    def test_update_user_response(self, service):
        """测试更新用户响应"""
        conversation_id = "conv_1"
        
        # 先记录一次介入
        intervention = service.record_intervention(
            conversation_id=conversation_id,
            trigger_type="silence",
            intervention_type="topic_suggestion",
            content="建议话题"
        )
        
        # 更新用户响应
        updated = service.update_user_response(
            intervention.intervention_id,
            conversation_id,
            "accepted"
        )
        
        assert updated.user_response == "accepted"
    
    def test_record_user_preference_disable(self, service):
        """测试记录用户禁用AI介入偏好"""
        user_id = "user_1"
        
        preference = service.record_user_preference(user_id, False)
        
        assert preference.user_id == user_id
        assert preference.ai_intervention_enabled is False
        assert preference.rejection_count == 1
        assert preference.last_rejection_time is not None
    
    def test_record_user_preference_enable(self, service):
        """测试记录用户启用AI介入偏好"""
        user_id = "user_1"
        
        preference = service.record_user_preference(user_id, True)
        
        assert preference.user_id == user_id
        assert preference.ai_intervention_enabled is True
        assert preference.rejection_count == 0
    
    def test_record_user_preference_multiple_rejections(self, service):
        """测试多次拒绝记录"""
        user_id = "user_1"
        
        # 第一次拒绝
        service.record_user_preference(user_id, False)
        # 第二次拒绝
        preference = service.record_user_preference(user_id, False)
        
        assert preference.rejection_count == 2
    
    def test_get_user_preference(self, service):
        """测试获取用户偏好"""
        user_id = "user_1"
        
        # 先记录偏好
        service.record_user_preference(user_id, False)
        
        # 获取偏好
        preference = service.get_user_preference(user_id)
        
        assert preference is not None
        assert preference.user_id == user_id
        assert preference.ai_intervention_enabled is False
    
    def test_get_user_preference_not_exists(self, service):
        """测试获取不存在的用户偏好"""
        user_id = "user_999"
        
        preference = service.get_user_preference(user_id)
        
        assert preference is None
    
    def test_get_intervention_history(self, service):
        """测试获取介入历史"""
        conversation_id = "conv_1"
        
        # 记录多次介入
        service.record_intervention(
            conversation_id, "silence", "topic_suggestion", "话题1"
        )
        service.record_intervention(
            conversation_id, "emotion_conflict", "emotional_support", "支持1"
        )
        
        history = service.get_intervention_history(conversation_id)
        
        assert len(history) == 2
        assert all(isinstance(i, AIIntervention) for i in history)
    
    def test_update_last_message_time(self, service):
        """测试更新最后消息时间"""
        conversation_id = "conv_1"
        timestamp = datetime.now()
        
        service.update_last_message_time(conversation_id, timestamp)
        
        assert conversation_id in service.last_message_time
        assert service.last_message_time[conversation_id] == timestamp
    
    def test_get_silence_duration(self, service):
        """测试获取沉默时长"""
        conversation_id = "conv_1"
        
        # 设置10秒前的消息时间
        service.last_message_time[conversation_id] = datetime.now() - timedelta(seconds=10)
        
        duration = service.get_silence_duration(conversation_id)
        
        # 应该接近10秒（允许一些误差）
        assert 9 <= duration <= 11
    
    def test_get_silence_duration_no_messages(self, service):
        """测试无消息时的沉默时长"""
        conversation_id = "conv_999"
        
        duration = service.get_silence_duration(conversation_id)
        
        assert duration == 0.0
    
    def test_integration_silence_detection_and_intervention(self, service):
        """集成测试：沉默检测和介入流程"""
        conversation_id = "conv_1"
        user_id = "user_1"
        scene = "考研自习室"
        
        # 1. 设置沉默状态
        service.last_message_time[conversation_id] = datetime.now() - timedelta(seconds=20)
        
        # 2. 检测沉默
        is_silent, silence_type = service.detect_silence(conversation_id, [])
        assert is_silent is True
        
        # 3. 检查是否应该介入
        should = service.should_intervene(conversation_id, user_id)
        assert should is True
        
        # 4. 生成话题建议
        suggestion = service.generate_topic_suggestion(
            conversation_id, scene, [], silence_type
        )
        assert len(suggestion) > 0
        
        # 5. 记录介入
        intervention = service.record_intervention(
            conversation_id, "silence", "topic_suggestion", suggestion
        )
        assert intervention is not None
        
        # 6. 验证冷却期生效
        should_again = service.should_intervene(conversation_id, user_id)
        assert should_again is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

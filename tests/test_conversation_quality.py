"""对话质量监测服务测试"""
import pytest
from datetime import datetime, timedelta
from src.services.conversation_service import ConversationService
from src.services.conversation_quality_service import ConversationQualityService
from src.models.conversation import (
    ConversationCreateRequest,
    MessageSendRequest,
    ConversationStatusUpdateRequest
)
from src.models.quality import (
    QualityMonitoringRequest,
    SatisfactionFeedbackRequest
)
from src.utils.exceptions import (
    ConversationNotFoundError,
    UnauthorizedAccessError
)


@pytest.fixture
def conversation_service():
    """创建对话服务实例"""
    return ConversationService()


@pytest.fixture
def quality_service(conversation_service):
    """创建对话质量监测服务实例"""
    return ConversationQualityService(conversation_service)


@pytest.fixture
def sample_conversation(conversation_service):
    """创建示例对话"""
    request = ConversationCreateRequest(
        user_a_id="user_001",
        user_b_id="user_002",
        scene="考研自习室"
    )
    return conversation_service.create_conversation(request)


@pytest.fixture
def conversation_with_messages(conversation_service, sample_conversation):
    """创建包含消息的对话"""
    messages_data = [
        ("user_001", "你好！我也在准备考研，你考哪个学校？"),
        ("user_002", "你好！我准备考清华大学计算机系，你呢？"),
        ("user_001", "我也是考计算机！不过我目标是北大。你复习到哪里了？"),
        ("user_002", "数据结构刚复习完，现在在看操作系统。感觉内容好多啊。"),
        ("user_001", "是啊，我也觉得操作系统很难。你用的什么教材？"),
        ("user_002", "我用的是王道的操作系统，配合视频课程一起看。"),
        ("user_001", "王道的书确实不错！我也在用。你每天学习多长时间？"),
        ("user_002", "我一般早上8点到图书馆，晚上10点回去，中间休息2小时左右。"),
        ("user_001", "你的学习时间好规律！我也想养成这样的习惯。"),
        ("user_002", "坚持下来就好了。对了，你有没有找研友一起学习？"),
        ("user_001", "还没有呢，一直是自己学。有研友的话确实会更有动力。"),
        ("user_002", "那我们可以互相监督啊！每天打卡分享进度。"),
    ]
    
    for sender_id, content in messages_data:
        send_request = MessageSendRequest(
            conversation_id=sample_conversation.conversation_id,
            sender_id=sender_id,
            content=content
        )
        conversation_service.send_message(send_request)
    
    return sample_conversation


class TestConversationQualityService:
    """对话质量监测服务测试类"""
    
    def test_service_initialization(self, quality_service):
        """测试服务初始化"""
        assert quality_service is not None
        assert quality_service.conversation_service is not None
        assert quality_service.feedback_storage == {}
        assert quality_service.reports_storage == {}
    
    def test_monitor_conversation_quality_basic(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试基本的对话质量监测"""
        request = QualityMonitoringRequest(
            conversation_id=conversation_with_messages.conversation_id
        )
        
        metrics = quality_service.monitor_conversation_quality(request)
        
        # 验证返回的指标
        assert metrics.conversation_id == conversation_with_messages.conversation_id
        assert 0 <= metrics.topic_depth_score <= 10
        assert metrics.topic_count >= 0
        assert metrics.average_topic_duration >= 0
        assert 0 <= metrics.response_consistency_score <= 1
        assert metrics.average_response_time >= 0
        assert metrics.response_length_variance >= 0
        assert 0 <= metrics.emotion_sync_score <= 1
        assert 0 <= metrics.emotion_alignment_rate <= 1
        assert 0 <= metrics.overall_quality_score <= 10
    
    def test_monitor_conversation_quality_insufficient_messages(
        self,
        quality_service,
        sample_conversation
    ):
        """测试消息不足时的质量监测"""
        # 只发送少量消息
        conversation_service = quality_service.conversation_service
        for i in range(3):
            send_request = MessageSendRequest(
                conversation_id=sample_conversation.conversation_id,
                sender_id="user_001" if i % 2 == 0 else "user_002",
                content=f"消息 {i}"
            )
            conversation_service.send_message(send_request)
        
        request = QualityMonitoringRequest(
            conversation_id=sample_conversation.conversation_id
        )
        
        metrics = quality_service.monitor_conversation_quality(request)
        
        # 消息太少，应该返回默认值
        assert metrics.overall_quality_score == 0.0
        assert metrics.topic_depth_score == 0.0
    
    def test_monitor_nonexistent_conversation(self, quality_service):
        """测试监测不存在的对话"""
        request = QualityMonitoringRequest(
            conversation_id="nonexistent_id"
        )
        
        with pytest.raises(ConversationNotFoundError):
            quality_service.monitor_conversation_quality(request)
    
    def test_analyze_topic_depth(self, quality_service, conversation_service):
        """测试话题深度分析"""
        # 创建对话
        conv_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="兴趣社群"
        )
        conversation = conversation_service.create_conversation(conv_request)
        
        # 发送深度对话消息
        deep_messages = [
            "我最近在学习机器学习，发现深度学习特别有意思",
            "是的！深度学习确实很强大。你在学习哪个方向？",
            "我主要在学习计算机视觉，特别是图像分类和目标检测",
            "计算机视觉很有前景！你用的什么框架？PyTorch还是TensorFlow？",
            "我用PyTorch，感觉比较灵活。你有推荐的学习资源吗？",
            "我推荐斯坦福的CS231n课程，讲得非常详细",
            "好的，我去看看。你学习的时候遇到过什么困难吗？",
            "主要是数学基础，线性代数和概率论需要比较扎实",
            "确实，我也在补数学。你有什么好的学习方法吗？",
            "我建议多做习题，理论结合实践效果最好",
        ]
        
        messages = []
        for i, content in enumerate(deep_messages):
            send_request = MessageSendRequest(
                conversation_id=conversation.conversation_id,
                sender_id="user_001" if i % 2 == 0 else "user_002",
                content=content
            )
            msg = conversation_service.send_message(send_request)
            messages.append(msg)
        
        # 分析话题深度
        depth_score, topic_count, avg_duration = quality_service.analyze_topic_depth(messages)
        
        assert depth_score > 0
        assert topic_count > 0
        assert avg_duration > 0
    
    def test_analyze_response_consistency(
        self,
        quality_service,
        conversation_service,
        conversation_with_messages
    ):
        """测试回应一致性分析"""
        from src.models.conversation import ConversationHistoryRequest
        
        # 获取消息
        history_request = ConversationHistoryRequest(
            conversation_id=conversation_with_messages.conversation_id,
            limit=500
        )
        messages = conversation_service.get_conversation_history(history_request)
        messages = list(reversed(messages))
        
        # 分析回应一致性
        consistency_score, avg_response_time, variance = \
            quality_service.analyze_response_consistency(
                messages,
                conversation_with_messages
            )
        
        assert 0 <= consistency_score <= 1
        assert avg_response_time >= 0
        assert variance >= 0
    
    def test_analyze_emotion_sync(
        self,
        quality_service,
        conversation_service
    ):
        """测试情感同步性分析"""
        # 创建对话
        conv_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="心理树洞"
        )
        conversation = conversation_service.create_conversation(conv_request)
        
        # 发送带有情感的消息
        emotional_messages = [
            "我最近压力好大，感觉很焦虑",
            "我理解你的感受，我之前也经历过类似的情况",
            "真的吗？你是怎么度过的？",
            "我当时找朋友倾诉，还去看了心理咨询",
            "听起来很有帮助。我也想试试",
            "加油！相信你能度过这个难关",
        ]
        
        messages = []
        for i, content in enumerate(emotional_messages):
            send_request = MessageSendRequest(
                conversation_id=conversation.conversation_id,
                sender_id="user_001" if i % 2 == 0 else "user_002",
                content=content
            )
            msg = conversation_service.send_message(send_request)
            messages.append(msg)
        
        # 分析情感同步性
        emotion_sync_score, alignment_rate = quality_service.analyze_emotion_sync(messages)
        
        assert 0 <= emotion_sync_score <= 1
        assert 0 <= alignment_rate <= 1
    
    def test_generate_conversation_report(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试生成对话质量报告"""
        # 结束对话
        update_request = ConversationStatusUpdateRequest(
            conversation_id=conversation_with_messages.conversation_id,
            status="ended"
        )
        quality_service.conversation_service.update_conversation_status(update_request)
        
        # 生成报告
        report = quality_service.generate_conversation_report(
            conversation_with_messages.conversation_id
        )
        
        # 验证报告内容
        assert report.conversation_id == conversation_with_messages.conversation_id
        assert report.user_a_id == conversation_with_messages.user_a_id
        assert report.user_b_id == conversation_with_messages.user_b_id
        assert report.scene == conversation_with_messages.scene
        assert report.message_count > 0
        assert report.duration_seconds >= 0
        assert report.metrics is not None
        assert isinstance(report.suggestions, list)
        assert isinstance(report.is_low_quality, bool)
    
    def test_collect_satisfaction_feedback(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试收集满意度反馈"""
        request = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="user_001",
            satisfaction_score=4.5,
            feedback_text="聊得很开心！",
            feedback_tags=["话题有趣", "聊得投机"]
        )
        
        feedback = quality_service.collect_satisfaction_feedback(request)
        
        # 验证反馈
        assert feedback.conversation_id == conversation_with_messages.conversation_id
        assert feedback.user_id == "user_001"
        assert feedback.satisfaction_score == 4.5
        assert feedback.feedback_text == "聊得很开心！"
        assert "话题有趣" in feedback.feedback_tags
        assert "聊得投机" in feedback.feedback_tags
    
    def test_collect_feedback_unauthorized_user(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试未授权用户提交反馈"""
        request = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="unauthorized_user",
            satisfaction_score=4.0
        )
        
        with pytest.raises(UnauthorizedAccessError):
            quality_service.collect_satisfaction_feedback(request)
    
    def test_detect_low_quality_conversation(
        self,
        quality_service,
        conversation_service
    ):
        """测试检测低质量对话"""
        # 创建低质量对话
        conv_request = ConversationCreateRequest(
            user_a_id="user_003",
            user_b_id="user_004",
            scene="兴趣社群"
        )
        conversation = conversation_service.create_conversation(conv_request)
        
        # 发送简短、无深度的消息
        short_messages = [
            "嗨", "你好", "在吗", "在", "干嘛呢",
            "没事", "哦", "嗯", "好吧", "嗯嗯"
        ]
        
        for i, content in enumerate(short_messages):
            send_request = MessageSendRequest(
                conversation_id=conversation.conversation_id,
                sender_id="user_003" if i % 2 == 0 else "user_004",
                content=content
            )
            conversation_service.send_message(send_request)
        
        # 检测低质量
        is_low_quality, suggestions = quality_service.detect_low_quality_conversation(
            conversation.conversation_id
        )
        
        # 验证结果
        assert isinstance(is_low_quality, bool)
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_report_includes_feedback(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试报告包含满意度反馈"""
        # 收集反馈
        feedback_request_a = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="user_001",
            satisfaction_score=4.5,
            feedback_tags=["话题有趣"]
        )
        quality_service.collect_satisfaction_feedback(feedback_request_a)
        
        feedback_request_b = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="user_002",
            satisfaction_score=4.8,
            feedback_tags=["对方友善"]
        )
        quality_service.collect_satisfaction_feedback(feedback_request_b)
        
        # 生成报告
        report = quality_service.generate_conversation_report(
            conversation_with_messages.conversation_id
        )
        
        # 验证报告包含反馈
        assert report.user_a_satisfaction == 4.5
        assert report.user_b_satisfaction == 4.8
    
    def test_get_conversation_report(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试获取对话质量报告"""
        # 生成报告
        report = quality_service.generate_conversation_report(
            conversation_with_messages.conversation_id
        )
        
        # 获取报告
        retrieved_report = quality_service.get_conversation_report(
            conversation_with_messages.conversation_id
        )
        
        assert retrieved_report is not None
        assert retrieved_report.report_id == report.report_id
    
    def test_get_nonexistent_report(self, quality_service):
        """测试获取不存在的报告"""
        report = quality_service.get_conversation_report("nonexistent_id")
        assert report is None
    
    def test_get_user_feedbacks(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试获取用户反馈"""
        # 收集多个反馈
        feedback_request_1 = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="user_001",
            satisfaction_score=4.5
        )
        quality_service.collect_satisfaction_feedback(feedback_request_1)
        
        feedback_request_2 = SatisfactionFeedbackRequest(
            conversation_id=conversation_with_messages.conversation_id,
            user_id="user_002",
            satisfaction_score=4.8
        )
        quality_service.collect_satisfaction_feedback(feedback_request_2)
        
        # 获取反馈
        feedbacks = quality_service.get_user_feedbacks(
            conversation_with_messages.conversation_id
        )
        
        assert len(feedbacks) == 2
        assert feedbacks[0].user_id == "user_001"
        assert feedbacks[1].user_id == "user_002"
    
    def test_quality_metrics_update_conversation(
        self,
        quality_service,
        conversation_with_messages
    ):
        """测试质量指标更新对话对象"""
        # 监测质量
        request = QualityMonitoringRequest(
            conversation_id=conversation_with_messages.conversation_id
        )
        metrics = quality_service.monitor_conversation_quality(request)
        
        # 获取更新后的对话
        conversation = quality_service.conversation_service.get_conversation(
            conversation_with_messages.conversation_id
        )
        
        # 验证对话的质量指标已更新
        assert conversation.topic_depth_score is not None
        assert conversation.emotion_sync_score is not None
    
    def test_suggestions_generation(
        self,
        quality_service,
        conversation_service
    ):
        """测试建议生成"""
        # 创建对话
        conv_request = ConversationCreateRequest(
            user_a_id="user_001",
            user_b_id="user_002",
            scene="考研自习室"
        )
        conversation = conversation_service.create_conversation(conv_request)
        
        # 发送消息
        for i in range(15):
            send_request = MessageSendRequest(
                conversation_id=conversation.conversation_id,
                sender_id="user_001" if i % 2 == 0 else "user_002",
                content=f"消息内容 {i}"
            )
            conversation_service.send_message(send_request)
        
        # 生成报告
        report = quality_service.generate_conversation_report(conversation.conversation_id)
        
        # 验证建议
        assert isinstance(report.suggestions, list)
        # 低质量对话应该有建议
        if report.is_low_quality:
            assert len(report.suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

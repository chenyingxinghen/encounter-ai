"""心理健康监测服务测试"""
import pytest
from datetime import datetime, timedelta

from src.services.mental_health_service import MentalHealthService
from src.models.mental_health import (
    EmotionAnalysisRequest,
    MentalHealthCheckRequest
)


class TestMentalHealthService:
    """心理健康监测服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return MentalHealthService()
    
    def test_analyze_emotion_positive(self, service):
        """测试正面情绪分析"""
        request = EmotionAnalysisRequest(
            text="今天真开心，学习进展很顺利！",
            user_id="user_001"
        )
        
        emotion = service.analyze_emotion(request)
        
        assert emotion.user_id == "user_001"
        assert emotion.emotion_type == "positive"
        assert 0.0 <= emotion.intensity <= 1.0
    
    def test_analyze_emotion_anxious(self, service):
        """测试焦虑情绪分析"""
        request = EmotionAnalysisRequest(
            text="我很焦虑，考试压力太大了，担心考不好",
            user_id="user_002"
        )
        
        emotion = service.analyze_emotion(request)
        
        assert emotion.user_id == "user_002"
        assert emotion.emotion_type == "anxious"
        assert emotion.intensity > 0.5
        assert len(emotion.detected_keywords) > 0
        assert any(kw in ['焦虑', '担心', '压力大'] for kw in emotion.detected_keywords)
    
    def test_analyze_emotion_depressed(self, service):
        """测试抑郁情绪分析"""
        request = EmotionAnalysisRequest(
            text="感觉很抑郁，什么都不想做，觉得很无助",
            user_id="user_003"
        )
        
        emotion = service.analyze_emotion(request)
        
        assert emotion.user_id == "user_003"
        assert emotion.emotion_type == "depressed"
        assert emotion.intensity > 0.5
        assert len(emotion.detected_keywords) > 0
    
    def test_detect_suicide_risk(self, service):
        """测试自杀风险检测"""
        request = EmotionAnalysisRequest(
            text="我真的不想活了，活着太痛苦了",
            user_id="user_004"
        )
        
        emotion = service.analyze_emotion(request)
        
        assert emotion.emotion_type == "depressed"
        assert emotion.intensity >= 0.8
        assert any(kw in service.NEGATIVE_KEYWORDS['suicide_risk'] 
                  for kw in emotion.detected_keywords)
    
    def test_check_mental_health_low_risk(self, service):
        """测试低风险心理健康检查"""
        user_id = "user_005"
        
        # 添加一些正面情绪
        for i in range(3):
            request = EmotionAnalysisRequest(
                text="今天心情不错",
                user_id=user_id
            )
            service.analyze_emotion(request)
        
        check_request = MentalHealthCheckRequest(user_id=user_id)
        status = service.check_mental_health(check_request)
        
        assert status.user_id == user_id
        assert status.risk_level == "low"
        assert status.negative_emotion_days == 0
    
    def test_check_mental_health_medium_risk(self, service):
        """测试中等风险心理健康检查"""
        user_id = "user_006"
        
        # 模拟3天负面情绪
        base_time = datetime.now()
        for day in range(3):
            # 修改时间戳
            emotion_request = EmotionAnalysisRequest(
                text="感觉很焦虑，压力很大",
                user_id=user_id
            )
            emotion = service.analyze_emotion(emotion_request)
            # 手动调整时间戳
            emotion.timestamp = base_time - timedelta(days=2-day)
            service.emotion_states[user_id][-1] = emotion
        
        check_request = MentalHealthCheckRequest(user_id=user_id)
        status = service.check_mental_health(check_request)
        
        assert status.user_id == user_id
        assert status.risk_level in ["medium", "high"]
        assert status.negative_emotion_days >= 3
    
    def test_push_mental_health_resources(self, service):
        """测试心理健康资源推送"""
        user_id = "user_007"
        
        resources = service.push_mental_health_resources(user_id, "anxious")
        
        assert len(resources) > 0
        assert len(resources) <= 3
        assert all(r.resource_id in service.resources for r in resources)
        
        # 检查推送记录
        push_records = service.get_user_push_records(user_id)
        assert len(push_records) == len(resources)
    
    def test_create_risk_alert(self, service):
        """测试创建风险预警"""
        user_id = "user_008"
        
        alert = service.create_risk_alert(
            user_id=user_id,
            alert_type="suicide_risk",
            detected_content="测试内容",
            confidence=0.9
        )
        
        assert alert.user_id == user_id
        assert alert.risk_level == "critical"
        assert alert.alert_type == "suicide_risk"
        assert alert.status == "pending"
        assert alert.notified_staff == True  # 严重风险应该立即通知
    
    def test_create_anonymous_session(self, service):
        """测试创建匿名会话"""
        user_id = "user_009"
        
        session = service.create_anonymous_session(user_id)
        
        assert session.user_id == user_id
        assert session.anonymous_id.startswith("anonymous_")
        assert session.scene == "心理树洞"
        assert session.is_active == True
    
    def test_end_anonymous_session(self, service):
        """测试结束匿名会话"""
        user_id = "user_010"
        
        session = service.create_anonymous_session(user_id)
        session_id = session.session_id
        
        result = service.end_anonymous_session(session_id)
        
        assert result == True
        assert service.anonymous_sessions[session_id].is_active == False
        assert service.anonymous_sessions[session_id].ended_at is not None
    
    def test_create_professional_referral(self, service):
        """测试创建专业转介"""
        user_id = "user_011"
        
        referral = service.create_professional_referral(
            user_id=user_id,
            referral_type="counseling",
            reason="持续负面情绪",
            urgency="high"
        )
        
        assert referral.user_id == user_id
        assert referral.referral_type == "counseling"
        assert referral.urgency == "high"
        assert referral.status == "pending"
        assert len(referral.contact_info) > 0
    
    def test_monitor_and_respond_normal(self, service):
        """测试正常情况的监测和响应"""
        user_id = "user_012"
        text = "今天学习了新知识，感觉还不错"
        
        result = service.monitor_and_respond(user_id, text)
        
        assert result['emotion_detected'] == True
        assert result['alert_created'] == False
        assert result['referral_created'] == False
    
    def test_monitor_and_respond_anxious(self, service):
        """测试焦虑情况的监测和响应"""
        user_id = "user_013"
        text = "我很焦虑，考试压力太大了"
        
        result = service.monitor_and_respond(user_id, text)
        
        assert result['emotion_detected'] == True
        assert len(result['resources_pushed']) > 0
    
    def test_monitor_and_respond_suicide_risk(self, service):
        """测试自杀风险的监测和响应"""
        user_id = "user_014"
        text = "我不想活了，太痛苦了"
        
        result = service.monitor_and_respond(user_id, text)
        
        assert result['emotion_detected'] == True
        assert result['alert_created'] == True
        assert result['referral_created'] == True
        assert len(result['resources_pushed']) > 0
        assert result['alert'].risk_level == "critical"
        assert result['referral'].urgency == "emergency"
    
    def test_monitor_and_respond_continuous_negative(self, service):
        """测试持续负面情绪的监测和响应"""
        user_id = "user_015"
        
        # 模拟8天持续负面情绪
        base_time = datetime.now()
        for day in range(8):
            emotion_request = EmotionAnalysisRequest(
                text="感觉很抑郁，什么都不想做",
                user_id=user_id
            )
            emotion = service.analyze_emotion(emotion_request)
            emotion.timestamp = base_time - timedelta(days=7-day)
            service.emotion_states[user_id][-1] = emotion
        
        # 最后一次监测
        result = service.monitor_and_respond(user_id, "还是感觉很抑郁")
        
        assert result['emotion_detected'] == True
        assert len(result['resources_pushed']) > 0
        assert result['referral_created'] == True
        assert result['health_status'].negative_emotion_days >= 7
    
    def test_get_pending_alerts(self, service):
        """测试获取待处理预警"""
        # 创建几个预警
        service.create_risk_alert("user_016", "suicide_risk", "测试1", 0.9)
        service.create_risk_alert("user_017", "severe_depression", "测试2", 0.8)
        
        pending_alerts = service.get_pending_alerts()
        
        assert len(pending_alerts) >= 2
        assert all(alert.status == "pending" for alert in pending_alerts)
    
    def test_emotion_keyword_detection(self, service):
        """测试情绪关键词检测"""
        test_cases = [
            ("我很焦虑", "anxious", ['焦虑']),
            ("感觉抑郁和无助", "depressed", ['抑郁', '无助']),
            ("想自杀", "depressed", ['自杀']),
            ("今天开心", "positive", []),
        ]
        
        for text, expected_emotion, expected_keywords in test_cases:
            request = EmotionAnalysisRequest(text=text, user_id="test_user")
            emotion = service.analyze_emotion(request)
            
            assert emotion.emotion_type == expected_emotion
            for keyword in expected_keywords:
                assert keyword in emotion.detected_keywords
    
    def test_resource_priority_sorting(self, service):
        """测试资源按优先级排序"""
        user_id = "user_018"
        
        resources = service.push_mental_health_resources(user_id, "anxious")
        
        # 验证资源按优先级降序排列
        for i in range(len(resources) - 1):
            assert resources[i].priority >= resources[i + 1].priority
    
    def test_anonymous_session_id_uniqueness(self, service):
        """测试匿名ID唯一性"""
        user_id = "user_019"
        
        session1 = service.create_anonymous_session(user_id)
        session2 = service.create_anonymous_session(user_id)
        
        assert session1.anonymous_id != session2.anonymous_id
        assert session1.session_id != session2.session_id

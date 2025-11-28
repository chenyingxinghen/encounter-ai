"""人格识别与用户画像服务集成测试"""
import pytest
from src.services.user_profile_service import UserProfileService
from src.services.personality_recognition_service import PersonalityRecognitionService
from src.models.user import UserRegistrationRequest, BigFiveScores


class TestPersonalityIntegrationWithUserProfile:
    """人格识别与用户画像服务集成测试"""
    
    @pytest.fixture
    def personality_service(self):
        """创建人格识别服务"""
        return PersonalityRecognitionService(use_ml=False)
    
    @pytest.fixture
    def profile_service(self, personality_service):
        """创建用户画像服务"""
        return UserProfileService(personality_service=personality_service)
    
    def test_analyze_personality_integration(self, profile_service):
        """测试人格分析集成"""
        # 创建测试用户
        request = UserRegistrationRequest(
            username="testuser",
            email="test@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user = profile_service.register_user(request)
        
        # 分析人格
        text_data = [
            "我喜欢和朋友们一起学习。",
            "有时候我会感到焦虑。",
            "我对新技术充满好奇。"
        ]
        
        scores = profile_service.analyze_personality(user.user_id, text_data)
        
        # 验证结果
        assert isinstance(scores, BigFiveScores)
        assert 0.0 <= scores.neuroticism <= 1.0
        assert 0.0 <= scores.agreeableness <= 1.0
        assert 0.0 <= scores.extraversion <= 1.0
        assert 0.0 <= scores.openness <= 1.0
        assert 0.0 <= scores.conscientiousness <= 1.0
        
        # 验证画像已更新
        profile = profile_service.get_profile(user.user_id)
        assert profile.big_five is not None
        assert profile.big_five.extraversion == scores.extraversion
    
    def test_update_personality_from_behavior_integration(self, profile_service):
        """测试根据行为更新人格集成"""
        # 创建测试用户
        request = UserRegistrationRequest(
            username="testuser2",
            email="test2@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user = profile_service.register_user(request)
        
        # 先分析人格
        text_data = ["我是一个普通的学生。"]
        initial_scores = profile_service.analyze_personality(user.user_id, text_data)
        
        # 根据行为更新
        behavior_data = {
            'response_speed': 5.0,
            'conversation_depth': 0.8,
            'social_frequency': 0.9,
            'emotion_variance': 0.3
        }
        
        updated_scores = profile_service.update_personality_from_behavior(
            user.user_id,
            behavior_data
        )
        
        # 验证结果
        assert isinstance(updated_scores, BigFiveScores)
        assert 0.0 <= updated_scores.neuroticism <= 1.0
        assert 0.0 <= updated_scores.agreeableness <= 1.0
        assert 0.0 <= updated_scores.extraversion <= 1.0
        assert 0.0 <= updated_scores.openness <= 1.0
        assert 0.0 <= updated_scores.conscientiousness <= 1.0
        
        # 验证画像已更新
        profile = profile_service.get_profile(user.user_id)
        assert profile.big_five is not None
        assert profile.big_five.extraversion == updated_scores.extraversion
    
    def test_update_interests_from_conversation(self, profile_service):
        """测试从对话更新兴趣"""
        # 创建测试用户
        request = UserRegistrationRequest(
            username="testuser3",
            email="test3@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user = profile_service.register_user(request)
        
        # 从对话数据更新兴趣
        conversation_data = {
            'interests': ['编程', '机器学习', '算法']
        }
        
        profile_service.update_interests_from_conversation(user.user_id, conversation_data)
        
        # 验证兴趣已更新
        profile = profile_service.get_profile(user.user_id)
        assert '编程' in profile.hobby_interests
        assert '机器学习' in profile.hobby_interests
        assert '算法' in profile.hobby_interests
    
    def test_personality_service_without_ml(self):
        """测试没有ML服务时的降级行为"""
        # 创建没有人格识别服务的用户画像服务
        profile_service = UserProfileService(personality_service=None)
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="testuser4",
            email="test4@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user = profile_service.register_user(request)
        
        # 尝试分析人格（应该返回默认值）
        text_data = ["测试文本"]
        scores = profile_service.analyze_personality(user.user_id, text_data)
        
        # 验证返回默认中性得分
        assert scores.neuroticism == 0.5
        assert scores.agreeableness == 0.5
        assert scores.extraversion == 0.5
        assert scores.openness == 0.5
        assert scores.conscientiousness == 0.5

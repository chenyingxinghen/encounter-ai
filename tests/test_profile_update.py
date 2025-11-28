"""用户画像动态更新服务测试"""
import pytest
from datetime import datetime
from src.services.profile_update_service import ProfileUpdateService
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.models.user import (
    User, UserProfile, BigFiveScores,
    UserRegistrationRequest, InterestSelectionRequest
)
from src.models.conversation import Message


class TestProfileUpdateService:
    """测试用户画像动态更新服务"""
    
    @pytest.fixture
    def user_profile_service(self):
        """创建用户画像服务实例"""
        return UserProfileService()
    
    @pytest.fixture
    def matching_service(self, user_profile_service):
        """创建匹配服务实例"""
        return MatchingService(user_profile_service=user_profile_service)
    
    @pytest.fixture
    def profile_update_service(self, user_profile_service, matching_service):
        """创建画像更新服务实例"""
        return ProfileUpdateService(
            user_profile_service=user_profile_service,
            matching_service=matching_service
        )
    
    @pytest.fixture
    def test_user(self, user_profile_service):
        """创建测试用户"""
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user = user_profile_service.register_user(request)
        
        # 设置初始画像
        user_profile_service.update_profile(user.user_id, {
            'mbti_type': 'INFP',
            'big_five': BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.6,
                extraversion=0.4,
                openness=0.7,
                conscientiousness=0.5
            ),
            'current_scenes': ['考研自习室', '兴趣社群']
        })
        
        return user
    
    def test_analyze_conversation_empty_messages(self, profile_update_service):
        """测试分析空消息列表"""
        result = profile_update_service.analyze_conversation(
            conversation_id="conv_123",
            messages=[]
        )
        
        assert result['conversation_id'] == "conv_123"
        assert result['topics'] == []
        assert result['emotions'] == {}
        assert result['interests'] == []
        assert result['message_count'] == 0
    
    def test_analyze_conversation_with_messages(self, profile_update_service):
        """测试分析包含消息的对话"""
        messages = [
            Message(
                message_id="msg_1",
                conversation_id="conv_123",
                sender_id="user_1",
                content="我最近在准备考研，压力好大啊",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_2",
                conversation_id="conv_123",
                sender_id="user_2",
                content="我也在考研，我们可以一起学习",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_3",
                conversation_id="conv_123",
                sender_id="user_1",
                content="太好了！你目标院校是哪里？",
                message_type="text",
                timestamp=datetime.now()
            )
        ]
        
        result = profile_update_service.analyze_conversation(
            conversation_id="conv_123",
            messages=messages
        )
        
        assert result['conversation_id'] == "conv_123"
        assert result['message_count'] == 3
        assert '考研' in result['topics']
        assert '学习' in result['topics']
        assert 'user_1' in result['emotions']
        assert 'user_2' in result['emotions']
    
    def test_extract_topics(self, profile_update_service):
        """测试话题提取"""
        messages = [
            Message(
                message_id="msg_1",
                conversation_id="conv_123",
                sender_id="user_1",
                content="我喜欢看电影和听音乐",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_2",
                conversation_id="conv_123",
                sender_id="user_2",
                content="我也喜欢音乐，还喜欢运动",
                message_type="text",
                timestamp=datetime.now()
            )
        ]
        
        topics = profile_update_service._extract_topics(messages)
        
        assert '电影' in topics
        assert '音乐' in topics
        assert '运动' in topics
    
    def test_analyze_emotions(self, profile_update_service):
        """测试情绪分析"""
        messages = [
            Message(
                message_id="msg_1",
                conversation_id="conv_123",
                sender_id="user_1",
                content="我今天很开心",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_2",
                conversation_id="conv_123",
                sender_id="user_1",
                content="但是有点担心考试",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_3",
                conversation_id="conv_123",
                sender_id="user_2",
                content="别担心，你一定可以的",
                message_type="text",
                timestamp=datetime.now()
            )
        ]
        
        emotions = profile_update_service._analyze_emotions(messages)
        
        assert 'user_1' in emotions
        assert 'user_2' in emotions
        assert emotions['user_1']['positive'] > 0
        assert emotions['user_1']['anxious'] > 0
        assert emotions['user_1']['total'] == 2
    
    def test_extract_interests(self, profile_update_service):
        """测试兴趣提取"""
        messages = [
            Message(
                message_id="msg_1",
                conversation_id="conv_123",
                sender_id="user_1",
                content="我在准备考研，目标是清华大学",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_2",
                conversation_id="conv_123",
                sender_id="user_2",
                content="我在找实习，想去互联网公司工作",
                message_type="text",
                timestamp=datetime.now()
            )
        ]
        
        interests = profile_update_service._extract_interests(messages)
        
        assert '考研' in interests
        assert '实习' in interests
        assert '工作' in interests
    
    def test_update_profile_from_conversation(
        self,
        profile_update_service,
        test_user
    ):
        """测试根据对话更新画像"""
        conversation_data = {
            'conversation_id': 'conv_123',
            'topics': ['考研', '学习'],
            'emotions': {
                test_user.user_id: {
                    'positive': 2,
                    'negative': 1,
                    'anxious': 1,
                    'neutral': 0,
                    'total': 4,
                    'positive_ratio': 0.5,
                    'negative_ratio': 0.25,
                    'anxious_ratio': 0.25,
                    'neutral_ratio': 0.0
                }
            },
            'interests': ['考研', '学习', '复习']
        }
        
        result = profile_update_service.update_profile_from_conversation(
            user_id=test_user.user_id,
            conversation_data=conversation_data
        )
        
        assert result['user_id'] == test_user.user_id
        assert 'interests_updated' in result
        assert 'emotions_updated' in result
        assert 'change_magnitude' in result
        assert 'should_notify' in result
        assert result['change_magnitude'] >= 0
    
    def test_update_interests_from_data(
        self,
        profile_update_service,
        user_profile_service,
        test_user
    ):
        """测试从数据更新兴趣"""
        conversation_data = {
            'interests': ['考研', '复习', '电影']
        }
        
        updated = profile_update_service._update_interests_from_data(
            user_id=test_user.user_id,
            conversation_data=conversation_data
        )
        
        assert updated is True
        
        profile = user_profile_service.get_profile(test_user.user_id)
        all_interests = (
            profile.academic_interests +
            profile.career_interests +
            profile.hobby_interests
        )
        
        assert '考研' in all_interests
        assert '复习' in all_interests
        assert '电影' in all_interests
    
    def test_update_emotional_features(
        self,
        profile_update_service,
        user_profile_service,
        test_user
    ):
        """测试更新情感特征"""
        conversation_data = {
            'emotions': {
                test_user.user_id: {
                    'positive': 8,
                    'negative': 1,
                    'anxious': 1,
                    'neutral': 0,
                    'total': 10,
                    'positive_ratio': 0.8,
                    'negative_ratio': 0.1,
                    'anxious_ratio': 0.1,
                    'neutral_ratio': 0.0
                }
            }
        }
        
        profile_before = user_profile_service.get_profile(test_user.user_id)
        emotion_stability_before = profile_before.emotion_stability
        social_energy_before = profile_before.social_energy
        
        updated = profile_update_service._update_emotional_features(
            user_id=test_user.user_id,
            conversation_data=conversation_data
        )
        
        assert updated is True
        
        profile_after = user_profile_service.get_profile(test_user.user_id)
        
        # 情绪稳定性应该提高（负面和焦虑情绪少）
        assert profile_after.emotion_stability >= emotion_stability_before
        
        # 社交能量应该提高（积极情绪多）
        assert profile_after.social_energy >= social_energy_before
    
    def test_calculate_profile_change(self, profile_update_service, test_user):
        """测试计算画像变化"""
        profile = UserProfile(
            user_id=test_user.user_id,
            emotion_stability=0.5,
            social_energy=0.5,
            academic_interests=['考研'],
            career_interests=[],
            hobby_interests=['音乐'],
            big_five=BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
        )
        
        snapshot = profile_update_service._create_profile_snapshot(profile)
        
        # 修改画像
        profile.emotion_stability = 0.7
        profile.social_energy = 0.6
        profile.hobby_interests.append('电影')
        
        change = profile_update_service._calculate_profile_change(
            snapshot,
            profile
        )
        
        assert change > 0
        assert change <= 1.0
    
    def test_update_personality_from_behavior(
        self,
        profile_update_service,
        test_user
    ):
        """测试根据行为更新人格"""
        behavior_data = {
            'emotion_volatility': 0.3,  # 低情绪波动
            'interaction_friendliness': 0.8,  # 高友好度
            'social_activity': 0.7,  # 高社交活跃度
            'topic_diversity': 0.6,  # 中等话题多样性
            'response_timeliness': 0.9  # 高及时性
        }
        
        updated_scores = profile_update_service.update_personality_from_behavior(
            user_id=test_user.user_id,
            behavior_data=behavior_data
        )
        
        assert isinstance(updated_scores, BigFiveScores)
        assert 0 <= updated_scores.neuroticism <= 1
        assert 0 <= updated_scores.agreeableness <= 1
        assert 0 <= updated_scores.extraversion <= 1
        assert 0 <= updated_scores.openness <= 1
        assert 0 <= updated_scores.conscientiousness <= 1
    
    def test_generate_profile_update_notification(
        self,
        profile_update_service,
        test_user
    ):
        """测试生成画像更新通知"""
        update_result = {
            'user_id': test_user.user_id,
            'interests_updated': True,
            'emotions_updated': True,
            'change_magnitude': 0.2,
            'should_notify': True,
            'match_recalculated': True,
            'updated_at': datetime.now()
        }
        
        notification = profile_update_service.generate_profile_update_notification(
            user_id=test_user.user_id,
            update_result=update_result
        )
        
        assert notification is not None
        assert notification['user_id'] == test_user.user_id
        assert notification['title'] == '您的画像已更新'
        assert 'message' in notification
        assert 'action' in notification
    
    def test_notification_not_generated_when_not_needed(
        self,
        profile_update_service,
        test_user
    ):
        """测试当不需要通知时不生成通知"""
        update_result = {
            'user_id': test_user.user_id,
            'interests_updated': False,
            'emotions_updated': False,
            'change_magnitude': 0.05,
            'should_notify': False,
            'match_recalculated': False,
            'updated_at': datetime.now()
        }
        
        notification = profile_update_service.generate_profile_update_notification(
            user_id=test_user.user_id,
            update_result=update_result
        )
        
        assert notification is None
    
    def test_trigger_match_recalculation(
        self,
        profile_update_service,
        user_profile_service,
        test_user
    ):
        """测试触发匹配度重新计算"""
        # 创建另一个用户用于匹配
        request = UserRegistrationRequest(
            username="测试用户2",
            email="test2@example.com",
            password="password123",
            school="测试大学",
            major="计算机科学",
            grade=3
        )
        user2 = user_profile_service.register_user(request)
        user_profile_service.update_profile(user2.user_id, {
            'mbti_type': 'ENFP',
            'big_five': BigFiveScores(
                neuroticism=0.4,
                agreeableness=0.7,
                extraversion=0.8,
                openness=0.6,
                conscientiousness=0.5
            ),
            'current_scenes': ['考研自习室', '兴趣社群'],
            'academic_interests': ['考研', '学习']
        })
        
        # 触发匹配重新计算
        profile_update_service._trigger_match_recalculation(test_user.user_id)
        
        # 验证没有抛出异常即可
        assert True
    
    def test_full_workflow(
        self,
        profile_update_service,
        user_profile_service,
        test_user
    ):
        """测试完整的画像更新工作流"""
        # 1. 创建对话消息
        messages = [
            Message(
                message_id="msg_1",
                conversation_id="conv_123",
                sender_id=test_user.user_id,
                content="我最近在准备考研，每天学习很充实",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_2",
                conversation_id="conv_123",
                sender_id="user_2",
                content="加油！我也在考研",
                message_type="text",
                timestamp=datetime.now()
            ),
            Message(
                message_id="msg_3",
                conversation_id="conv_123",
                sender_id=test_user.user_id,
                content="谢谢！我感觉很开心能找到志同道合的伙伴",
                message_type="text",
                timestamp=datetime.now()
            )
        ]
        
        # 2. 分析对话
        conversation_data = profile_update_service.analyze_conversation(
            conversation_id="conv_123",
            messages=messages
        )
        
        assert conversation_data['message_count'] == 3
        assert len(conversation_data['topics']) > 0
        
        # 3. 更新画像
        update_result = profile_update_service.update_profile_from_conversation(
            user_id=test_user.user_id,
            conversation_data=conversation_data
        )
        
        assert update_result['user_id'] == test_user.user_id
        
        # 4. 如果需要，生成通知
        if update_result['should_notify']:
            notification = profile_update_service.generate_profile_update_notification(
                user_id=test_user.user_id,
                update_result=update_result
            )
            assert notification is not None
        
        # 5. 验证画像已更新
        updated_profile = user_profile_service.get_profile(test_user.user_id)
        assert updated_profile.updated_at is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

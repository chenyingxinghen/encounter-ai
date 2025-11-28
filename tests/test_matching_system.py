"""智能匹配系统测试"""
import pytest
from src.models.user import (
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest, BigFiveScores
)
from src.models.matching import Match, SceneConfig, MatchRequest, MatchResult
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.utils.exceptions import ValidationError, NotFoundError


class TestMatchingService:
    """测试匹配服务基本功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        
        # 创建两个测试用户
        self.user1 = self._create_complete_user(
            username="用户1",
            email="user1@example.com",
            mbti_answers=[4] * 60,  # ESTJ倾向
            big_five_answers=[4] * 50,
            academic_interests=["考研", "数学"],
            career_interests=["软件工程师"],
            hobby_interests=["阅读", "音乐"],
            scenes=["考研自习室", "兴趣社群"]
        )
        
        self.user2 = self._create_complete_user(
            username="用户2",
            email="user2@example.com",
            mbti_answers=[4] * 60,  # ESTJ倾向
            big_five_answers=[4] * 50,
            academic_interests=["考研", "计算机"],
            career_interests=["软件工程师"],
            hobby_interests=["阅读", "运动"],
            scenes=["考研自习室"]
        )
    
    def _create_complete_user(
        self,
        username,
        email,
        mbti_answers,
        big_five_answers,
        academic_interests,
        career_interests,
        hobby_interests,
        scenes
    ):
        """创建完整的测试用户"""
        # 注册用户
        reg_request = UserRegistrationRequest(
            username=username,
            email=email,
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        user = self.profile_service.register_user(reg_request)
        
        # MBTI测试
        mbti_request = MBTITestRequest(
            user_id=user.user_id,
            answers=mbti_answers
        )
        self.profile_service.process_mbti_test(mbti_request)
        
        # 大五人格测试
        big_five_request = BigFiveTestRequest(
            user_id=user.user_id,
            answers=big_five_answers
        )
        self.profile_service.process_big_five_test(big_five_request)
        
        # 兴趣标签
        interest_request = InterestSelectionRequest(
            user_id=user.user_id,
            academic_interests=academic_interests,
            career_interests=career_interests,
            hobby_interests=hobby_interests
        )
        self.profile_service.update_interests(interest_request)
        
        # 场景选择
        scene_request = SceneSelectionRequest(
            user_id=user.user_id,
            scenes=scenes
        )
        self.profile_service.update_scenes(scene_request)
        
        # 生成画像
        self.profile_service.generate_initial_profile(user.user_id)
        
        return user
    
    def test_calculate_match_score(self):
        """测试匹配度计算"""
        score = self.matching_service.calculate_match_score(
            self.user1.user_id,
            self.user2.user_id,
            "考研自习室"
        )
        
        assert 0.0 <= score <= 100.0
        assert isinstance(score, float)
    
    def test_find_matches(self):
        """测试查找匹配对象"""
        matches = self.matching_service.find_matches(
            self.user1.user_id,
            "考研自习室",
            limit=10
        )
        
        assert isinstance(matches, list)
        assert len(matches) <= 10
        
        # 应该找到user2
        if len(matches) > 0:
            assert matches[0].user_b_id == self.user2.user_id
            assert matches[0].scene == "考研自习室"
            assert 0.0 <= matches[0].match_score <= 100.0
    
    def test_match_result_sorted(self):
        """测试匹配结果按分数排序"""
        # 创建第三个用户，匹配度较低
        user3 = self._create_complete_user(
            username="用户3",
            email="user3@example.com",
            mbti_answers=[2] * 60,  # 不同的MBTI倾向
            big_five_answers=[2] * 50,
            academic_interests=["英语"],
            career_interests=["教师"],
            hobby_interests=["旅游"],
            scenes=["考研自习室"]
        )
        
        matches = self.matching_service.find_matches(
            self.user1.user_id,
            "考研自习室",
            limit=10
        )
        
        # 验证排序
        for i in range(len(matches) - 1):
            assert matches[i].match_score >= matches[i + 1].match_score
    
    def test_match_limit(self):
        """测试匹配结果数量限制"""
        # 创建多个用户
        for i in range(15):
            self._create_complete_user(
                username=f"用户{i+3}",
                email=f"user{i+3}@example.com",
                mbti_answers=[3] * 60,
                big_five_answers=[3] * 50,
                academic_interests=["考研"],
                career_interests=["工程师"],
                hobby_interests=["阅读"],
                scenes=["考研自习室"]
            )
        
        matches = self.matching_service.find_matches(
            self.user1.user_id,
            "考研自习室",
            limit=5
        )
        
        assert len(matches) <= 5
    
    def test_get_match_reason(self):
        """测试匹配理由生成"""
        reason = self.matching_service.get_match_reason(
            self.user1.user_id,
            self.user2.user_id,
            "考研自习室"
        )
        
        assert isinstance(reason, str)
        assert len(reason) > 0
        # 应该包含一些关键信息
        assert "考研" in reason or "软件工程师" in reason or "阅读" in reason


class TestSceneConfig:
    """测试场景配置"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
    
    def test_get_scene_config(self):
        """测试获取场景配置"""
        config = self.matching_service.get_scene_config("考研自习室")
        
        assert isinstance(config, SceneConfig)
        assert config.scene_name == "考研自习室"
        assert config.display_name == "考研自习室"
        assert len(config.match_weights) > 0
        assert abs(sum(config.match_weights.values()) - 1.0) < 0.01
    
    def test_all_scenes_configured(self):
        """测试所有场景都有配置"""
        scenes = ["考研自习室", "职业咨询室", "心理树洞", "兴趣社群"]
        
        for scene in scenes:
            config = self.matching_service.get_scene_config(scene)
            assert config is not None
            assert config.scene_name == scene
    
    def test_update_match_weights(self):
        """测试更新匹配权重"""
        new_weights = {
            'personality': 0.3,
            'interest': 0.4,
            'scene': 0.2,
            'emotion': 0.1
        }
        
        self.matching_service.update_match_weights("考研自习室", new_weights)
        
        config = self.matching_service.get_scene_config("考研自习室")
        assert config.match_weights == new_weights
    
    def test_update_weights_invalid_sum(self):
        """测试权重总和不为1"""
        invalid_weights = {
            'personality': 0.3,
            'interest': 0.3,
            'scene': 0.3,
            'emotion': 0.3  # 总和为1.2
        }
        
        with pytest.raises(ValidationError, match="sum to 1.0"):
            self.matching_service.update_match_weights("考研自习室", invalid_weights)


class TestPersonalityMatching:
    """测试人格匹配评分"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
    
    def test_same_mbti_high_score(self):
        """测试相同MBTI类型的匹配"""
        user1 = self._create_user_with_mbti([5] * 60)  # ESTJ
        user2 = self._create_user_with_mbti([5] * 60)  # ESTJ
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_personality_score(profile1, profile2)
        
        # 相同MBTI应该有较高分数
        assert score > 50.0
    
    def test_different_mbti_lower_score(self):
        """测试完全不同MBTI类型的匹配"""
        user1 = self._create_user_with_mbti([5] * 60)  # ESTJ
        user2 = self._create_user_with_mbti([1] * 60)  # INFP
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_personality_score(profile1, profile2)
        
        # 完全不同的MBTI应该有较低分数
        assert score < 80.0
    
    def _create_user_with_mbti(self, mbti_answers):
        """创建带有特定MBTI的用户"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = self.profile_service.register_user(
            UserRegistrationRequest(
                username=f"user_{unique_id}",
                email=f"user_{unique_id}@example.com",
                password="password123",
                school="清华大学",
                major="计算机科学",
                grade=2
            )
        )
        
        self.profile_service.process_mbti_test(
            MBTITestRequest(user_id=user.user_id, answers=mbti_answers)
        )
        
        self.profile_service.process_big_five_test(
            BigFiveTestRequest(user_id=user.user_id, answers=[3] * 50)
        )
        
        self.profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
        )
        
        return user


class TestInterestMatching:
    """测试兴趣匹配评分"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
    
    def test_common_interests_high_score(self):
        """测试共同兴趣多的匹配"""
        user1 = self._create_user_with_interests(
            academic=["考研", "数学", "编程"],
            career=["软件工程师"],
            hobby=["阅读", "音乐"]
        )
        
        user2 = self._create_user_with_interests(
            academic=["考研", "数学", "算法"],
            career=["软件工程师"],
            hobby=["阅读", "运动"]
        )
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_interest_score(
            profile1, profile2, "考研自习室"
        )
        
        # 有共同学业兴趣，分数应该较高
        assert score > 30.0
    
    def test_no_common_interests_lower_score(self):
        """测试没有共同兴趣的匹配"""
        user1 = self._create_user_with_interests(
            academic=["考研", "数学"],
            career=["软件工程师"],
            hobby=["阅读"]
        )
        
        user2 = self._create_user_with_interests(
            academic=["英语", "文学"],
            career=["教师"],
            hobby=["旅游"]
        )
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_interest_score(
            profile1, profile2, "考研自习室"
        )
        
        # 没有共同兴趣，分数应该较低
        assert score <= 50.0
    
    def _create_user_with_interests(self, academic, career, hobby):
        """创建带有特定兴趣的用户"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = self.profile_service.register_user(
            UserRegistrationRequest(
                username=f"user_{unique_id}",
                email=f"user_{unique_id}@example.com",
                password="password123",
                school="清华大学",
                major="计算机科学",
                grade=2
            )
        )
        
        self.profile_service.process_mbti_test(
            MBTITestRequest(user_id=user.user_id, answers=[3] * 60)
        )
        
        self.profile_service.process_big_five_test(
            BigFiveTestRequest(user_id=user.user_id, answers=[3] * 50)
        )
        
        self.profile_service.update_interests(
            InterestSelectionRequest(
                user_id=user.user_id,
                academic_interests=academic,
                career_interests=career,
                hobby_interests=hobby
            )
        )
        
        self.profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
        )
        
        return user


class TestSceneMatching:
    """测试场景匹配评分"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
    
    def test_both_in_scene_high_score(self):
        """测试双方都关注该场景"""
        user1 = self._create_user_with_scenes(["考研自习室", "兴趣社群"])
        user2 = self._create_user_with_scenes(["考研自习室"])
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_scene_score(
            profile1, profile2, "考研自习室"
        )
        
        # 双方都关注该场景，分数应该较高
        assert score > 50.0
    
    def test_one_not_in_scene_lower_score(self):
        """测试一方不关注该场景"""
        user1 = self._create_user_with_scenes(["考研自习室"])
        user2 = self._create_user_with_scenes(["兴趣社群"])
        
        profile1 = self.profile_service.get_profile(user1.user_id)
        profile2 = self.profile_service.get_profile(user2.user_id)
        
        score = self.matching_service._calculate_scene_score(
            profile1, profile2, "考研自习室"
        )
        
        # 一方不关注该场景，分数应该较低
        assert score <= 50.0
    
    def _create_user_with_scenes(self, scenes):
        """创建带有特定场景的用户"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = self.profile_service.register_user(
            UserRegistrationRequest(
                username=f"user_{unique_id}",
                email=f"user_{unique_id}@example.com",
                password="password123",
                school="清华大学",
                major="计算机科学",
                grade=2
            )
        )
        
        self.profile_service.process_mbti_test(
            MBTITestRequest(user_id=user.user_id, answers=[3] * 60)
        )
        
        self.profile_service.process_big_five_test(
            BigFiveTestRequest(user_id=user.user_id, answers=[3] * 50)
        )
        
        self.profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=scenes)
        )
        
        return user


class TestMatchResult:
    """测试匹配结果模型"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        
        # 创建两个完整用户
        self.user1 = self._create_complete_user(
            "用户1", "user1@example.com",
            ["考研", "数学"], ["软件工程师"], ["阅读"],
            ["考研自习室"]
        )
        
        self.user2 = self._create_complete_user(
            "用户2", "user2@example.com",
            ["考研", "计算机"], ["软件工程师"], ["音乐"],
            ["考研自习室"]
        )
    
    def _create_complete_user(self, username, email, academic, career, hobby, scenes):
        """创建完整用户"""
        user = self.profile_service.register_user(
            UserRegistrationRequest(
                username=username,
                email=email,
                password="password123",
                school="清华大学",
                major="计算机科学",
                grade=2
            )
        )
        
        self.profile_service.process_mbti_test(
            MBTITestRequest(user_id=user.user_id, answers=[3] * 60)
        )
        
        self.profile_service.process_big_five_test(
            BigFiveTestRequest(user_id=user.user_id, answers=[3] * 50)
        )
        
        self.profile_service.update_interests(
            InterestSelectionRequest(
                user_id=user.user_id,
                academic_interests=academic,
                career_interests=career,
                hobby_interests=hobby
            )
        )
        
        self.profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=scenes)
        )
        
        self.profile_service.generate_initial_profile(user.user_id)
        
        return user
    
    def test_create_match_result(self):
        """测试创建匹配结果"""
        matches = self.matching_service.find_matches(
            self.user1.user_id,
            "考研自习室",
            limit=1
        )
        
        assert len(matches) > 0
        match = matches[0]
        
        result = self.matching_service.create_match_result(
            match,
            self.user1.user_id
        )
        
        assert isinstance(result, MatchResult)
        assert result.match == match
        assert result.user_info['user_id'] == self.user2.user_id
        assert result.user_info['username'] == "用户2"
        assert 'mbti_type' in result.personality_traits
        assert 'academic_interests' in result.interest_tags
        assert len(result.scene_needs) > 0

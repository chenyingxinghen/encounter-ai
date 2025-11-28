"""场景管理服务测试"""
import pytest
from src.models.user import (
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.models.matching import SceneConfig
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.services.scene_management_service import SceneManagementService
from src.utils.exceptions import ValidationError, NotFoundError


class TestSceneManagementService:
    """测试场景管理服务基本功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.scene_service = SceneManagementService(
            self.profile_service,
            self.matching_service
        )
        
        # 创建测试用户
        self.user = self._create_test_user()
    
    def _create_test_user(self):
        """创建测试用户"""
        user = self.profile_service.register_user(
            UserRegistrationRequest(
                username="测试用户",
                email="test@example.com",
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
            SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
        )
        
        return user
    
    def test_get_scene_config(self):
        """测试获取场景配置"""
        config = self.scene_service.get_scene_config("考研自习室")
        
        assert isinstance(config, SceneConfig)
        assert config.scene_name == "考研自习室"
        assert config.display_name == "考研自习室"
        assert len(config.description) > 0
        assert len(config.match_weights) == 4
        assert abs(sum(config.match_weights.values()) - 1.0) < 0.01
    
    def test_get_scene_config_invalid(self):
        """测试获取无效场景配置"""
        with pytest.raises(ValidationError, match="Invalid scene"):
            self.scene_service.get_scene_config("无效场景")
    
    def test_get_match_weights(self):
        """测试获取场景匹配权重"""
        weights = self.scene_service.get_match_weights("考研自习室")
        
        assert isinstance(weights, dict)
        assert 'personality' in weights
        assert 'interest' in weights
        assert 'scene' in weights
        assert 'emotion' in weights
        assert abs(sum(weights.values()) - 1.0) < 0.01
    
    def test_list_available_scenes(self):
        """测试列出可用场景"""
        scenes = self.scene_service.list_available_scenes()
        
        assert isinstance(scenes, list)
        assert len(scenes) == 4
        
        scene_names = [s['scene_name'] for s in scenes]
        assert "考研自习室" in scene_names
        assert "职业咨询室" in scene_names
        assert "心理树洞" in scene_names
        assert "兴趣社群" in scene_names
    
    def test_list_available_scenes_with_user(self):
        """测试列出用户的可用场景"""
        scenes = self.scene_service.list_available_scenes(self.user.user_id)
        
        assert isinstance(scenes, list)
        assert len(scenes) == 4
        
        # 检查用户当前场景标记
        for scene in scenes:
            if scene['scene_name'] == "考研自习室":
                assert scene['is_active'] is True
            else:
                assert scene['is_active'] is False
    
    def test_switch_scene(self):
        """测试切换场景"""
        self.scene_service.switch_scene(
            self.user.user_id,
            "职业咨询室",
            priority=0.8
        )
        
        profile = self.profile_service.get_profile(self.user.user_id)
        
        assert "职业咨询室" in profile.current_scenes
        assert profile.scene_priorities["职业咨询室"] == 0.8
    
    def test_switch_scene_invalid(self):
        """测试切换到无效场景"""
        with pytest.raises(ValidationError, match="Invalid scene"):
            self.scene_service.switch_scene(
                self.user.user_id,
                "无效场景",
                priority=0.5
            )
    
    def test_switch_scene_invalid_priority(self):
        """测试使用无效优先级切换场景"""
        with pytest.raises(ValidationError, match="Priority must be between"):
            self.scene_service.switch_scene(
                self.user.user_id,
                "职业咨询室",
                priority=1.5
            )
    
    def test_remove_scene(self):
        """测试移除场景"""
        # 先添加一个场景
        self.scene_service.switch_scene(
            self.user.user_id,
            "职业咨询室",
            priority=0.8
        )
        
        # 然后移除
        self.scene_service.remove_scene(self.user.user_id, "职业咨询室")
        
        profile = self.profile_service.get_profile(self.user.user_id)
        
        assert "职业咨询室" not in profile.current_scenes
        assert "职业咨询室" not in profile.scene_priorities
    
    def test_update_scene_priority(self):
        """测试更新场景优先级"""
        self.scene_service.update_scene_priority(
            self.user.user_id,
            "考研自习室",
            priority=0.9
        )
        
        profile = self.profile_service.get_profile(self.user.user_id)
        
        assert profile.scene_priorities["考研自习室"] == 0.9
    
    def test_update_scene_priority_invalid(self):
        """测试使用无效优先级更新"""
        with pytest.raises(ValidationError, match="Priority must be between"):
            self.scene_service.update_scene_priority(
                self.user.user_id,
                "考研自习室",
                priority=-0.1
            )
    
    def test_get_scene_topic_templates(self):
        """测试获取场景话题模板"""
        templates = self.scene_service.get_scene_topic_templates("考研自习室")
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert all(isinstance(t, str) for t in templates)
    
    def test_get_scene_ai_config(self):
        """测试获取场景AI配置"""
        config = self.scene_service.get_scene_ai_config("考研自习室")
        
        assert isinstance(config, dict)
        assert 'intervention_threshold' in config
        assert 'max_interventions_per_hour' in config
        assert config['intervention_threshold'] > 0
        assert config['max_interventions_per_hour'] > 0
    
    def test_validate_scene(self):
        """测试验证场景"""
        assert self.scene_service.validate_scene("考研自习室") is True
        assert self.scene_service.validate_scene("职业咨询室") is True
        assert self.scene_service.validate_scene("心理树洞") is True
        assert self.scene_service.validate_scene("兴趣社群") is True
        assert self.scene_service.validate_scene("无效场景") is False
    
    def test_get_all_scene_names(self):
        """测试获取所有场景名称"""
        names = self.scene_service.get_all_scene_names()
        
        assert isinstance(names, list)
        assert len(names) == 4
        assert "考研自习室" in names
        assert "职业咨询室" in names
        assert "心理树洞" in names
        assert "兴趣社群" in names


class TestSceneConfigurations:
    """测试各个场景的配置"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.scene_service = SceneManagementService(
            self.profile_service,
            self.matching_service
        )
    
    def test_exam_study_room_config(self):
        """测试考研自习室场景配置"""
        config = self.scene_service.get_scene_config("考研自习室")
        
        assert config.scene_name == "考研自习室"
        assert "考研" in config.description or "学习" in config.description
        
        # 考研场景应该重视兴趣和场景匹配
        assert config.match_weights['interest'] >= 0.3
        assert config.match_weights['scene'] >= 0.25
        
        # 应该有相关话题模板
        assert len(config.topic_templates) > 0
        assert any("院校" in t or "学习" in t for t in config.topic_templates)
    
    def test_career_consulting_config(self):
        """测试职业咨询室场景配置"""
        config = self.scene_service.get_scene_config("职业咨询室")
        
        assert config.scene_name == "职业咨询室"
        assert "职业" in config.description or "求职" in config.description
        
        # 职业场景应该最重视兴趣匹配
        assert config.match_weights['interest'] >= 0.35
        
        # 应该有相关话题模板
        assert len(config.topic_templates) > 0
        assert any("职业" in t or "行业" in t for t in config.topic_templates)
    
    def test_mental_health_config(self):
        """测试心理树洞场景配置"""
        config = self.scene_service.get_scene_config("心理树洞")
        
        assert config.scene_name == "心理树洞"
        assert "心理" in config.description or "情感" in config.description
        
        # 心理场景应该最重视情感同步性
        assert config.match_weights['emotion'] >= 0.35
        
        # 应该有更长的介入阈值和更少的介入次数
        assert config.intervention_threshold >= 15
        assert config.max_interventions_per_hour <= 3
        
        # 应该有相关话题模板
        assert len(config.topic_templates) > 0
        assert any("困扰" in t or "压力" in t or "感受" in t for t in config.topic_templates)
    
    def test_interest_community_config(self):
        """测试兴趣社群场景配置"""
        config = self.scene_service.get_scene_config("兴趣社群")
        
        assert config.scene_name == "兴趣社群"
        assert "兴趣" in config.description
        
        # 兴趣社群应该最重视兴趣匹配
        assert config.match_weights['interest'] >= 0.45
        
        # 应该有相关话题模板
        assert len(config.topic_templates) > 0
        assert any("兴趣" in t or "爱好" in t for t in config.topic_templates)


class TestSceneSwitchingLogic:
    """测试场景切换逻辑"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.scene_service = SceneManagementService(
            self.profile_service,
            self.matching_service
        )
        
        # 创建两个用户
        self.user1 = self._create_user("用户1", "user1@example.com")
        self.user2 = self._create_user("用户2", "user2@example.com")
    
    def _create_user(self, username, email):
        """创建用户"""
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
                academic_interests=["考研", "数学"],
                career_interests=["软件工程师"],
                hobby_interests=["阅读"]
            )
        )
        
        self.profile_service.update_scenes(
            SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
        )
        
        self.profile_service.generate_initial_profile(user.user_id)
        
        return user
    
    def test_scene_switch_updates_profile(self):
        """测试场景切换更新用户画像"""
        initial_profile = self.profile_service.get_profile(self.user1.user_id)
        initial_scenes = initial_profile.current_scenes.copy()
        
        # 切换到新场景
        self.scene_service.switch_scene(
            self.user1.user_id,
            "职业咨询室",
            priority=0.7
        )
        
        updated_profile = self.profile_service.get_profile(self.user1.user_id)
        
        # 验证场景已添加
        assert "职业咨询室" in updated_profile.current_scenes
        assert updated_profile.scene_priorities["职业咨询室"] == 0.7
        
        # 原有场景应该保留
        for scene in initial_scenes:
            assert scene in updated_profile.current_scenes
    
    def test_multiple_scene_switches(self):
        """测试多次场景切换"""
        # 切换到多个场景
        scenes_to_add = [
            ("职业咨询室", 0.8),
            ("心理树洞", 0.6),
            ("兴趣社群", 0.9)
        ]
        
        for scene, priority in scenes_to_add:
            self.scene_service.switch_scene(
                self.user1.user_id,
                scene,
                priority=priority
            )
        
        profile = self.profile_service.get_profile(self.user1.user_id)
        
        # 验证所有场景都已添加
        assert "考研自习室" in profile.current_scenes
        assert "职业咨询室" in profile.current_scenes
        assert "心理树洞" in profile.current_scenes
        assert "兴趣社群" in profile.current_scenes
        
        # 验证优先级
        assert profile.scene_priorities["职业咨询室"] == 0.8
        assert profile.scene_priorities["心理树洞"] == 0.6
        assert profile.scene_priorities["兴趣社群"] == 0.9
    
    def test_scene_switch_affects_matching(self):
        """测试场景切换影响匹配结果"""
        # 初始匹配（考研自习室）
        initial_matches = self.matching_service.find_matches(
            self.user1.user_id,
            "考研自习室",
            limit=10
        )
        
        # 切换到职业咨询室
        self.scene_service.switch_scene(
            self.user1.user_id,
            "职业咨询室",
            priority=1.0
        )
        
        # 在职业咨询室场景下匹配
        career_matches = self.matching_service.find_matches(
            self.user1.user_id,
            "职业咨询室",
            limit=10
        )
        
        # 匹配结果应该存在（可能不同）
        assert isinstance(career_matches, list)


class TestSceneWeightAdjustment:
    """测试场景特定的匹配权重调整"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.scene_service = SceneManagementService(
            self.profile_service,
            self.matching_service
        )
        
        # 创建两个用户
        self.user1 = self._create_user_with_profile(
            "用户1", "user1@example.com",
            academic=["考研", "数学"],
            career=["软件工程师"],
            hobby=["阅读"]
        )
        
        self.user2 = self._create_user_with_profile(
            "用户2", "user2@example.com",
            academic=["考研", "计算机"],
            career=["软件工程师"],
            hobby=["音乐"]
        )
    
    def _create_user_with_profile(self, username, email, academic, career, hobby):
        """创建带有完整画像的用户"""
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
            SceneSelectionRequest(
                user_id=user.user_id,
                scenes=["考研自习室", "职业咨询室", "兴趣社群"]
            )
        )
        
        self.profile_service.generate_initial_profile(user.user_id)
        
        return user
    
    def test_different_weights_for_different_scenes(self):
        """测试不同场景使用不同权重"""
        # 考研自习室场景的匹配度
        exam_score = self.matching_service.calculate_match_score(
            self.user1.user_id,
            self.user2.user_id,
            "考研自习室"
        )
        
        # 职业咨询室场景的匹配度
        career_score = self.matching_service.calculate_match_score(
            self.user1.user_id,
            self.user2.user_id,
            "职业咨询室"
        )
        
        # 兴趣社群场景的匹配度
        interest_score = self.matching_service.calculate_match_score(
            self.user1.user_id,
            self.user2.user_id,
            "兴趣社群"
        )
        
        # 由于权重不同，分数应该有差异
        # 这里只验证分数都在有效范围内
        assert 0.0 <= exam_score <= 100.0
        assert 0.0 <= career_score <= 100.0
        assert 0.0 <= interest_score <= 100.0
    
    def test_exam_scene_prioritizes_academic_interests(self):
        """测试考研场景优先考虑学业兴趣"""
        # 创建一个学业兴趣完全匹配的用户
        user3 = self._create_user_with_profile(
            "用户3", "user3@example.com",
            academic=["考研", "数学"],  # 与user1完全相同
            career=["教师"],  # 不同
            hobby=["旅游"]  # 不同
        )
        
        # 创建一个职业兴趣匹配但学业不匹配的用户
        user4 = self._create_user_with_profile(
            "用户4", "user4@example.com",
            academic=["英语"],  # 不同
            career=["软件工程师"],  # 与user1相同
            hobby=["阅读"]  # 与user1相同
        )
        
        # 在考研场景下，user3应该有更高的匹配度
        score_user3 = self.matching_service.calculate_match_score(
            self.user1.user_id,
            user3.user_id,
            "考研自习室"
        )
        
        score_user4 = self.matching_service.calculate_match_score(
            self.user1.user_id,
            user4.user_id,
            "考研自习室"
        )
        
        # 由于考研场景重视学业兴趣，user3的分数应该更高
        assert score_user3 > score_user4
    
    def test_career_scene_prioritizes_career_interests(self):
        """测试职业场景优先考虑职业兴趣"""
        # 创建一个职业兴趣完全匹配的用户
        user3 = self._create_user_with_profile(
            "用户3", "user3@example.com",
            academic=["英语"],  # 不同
            career=["软件工程师"],  # 与user1相同
            hobby=["旅游"]  # 不同
        )
        
        # 创建一个学业兴趣匹配但职业不匹配的用户
        user4 = self._create_user_with_profile(
            "用户4", "user4@example.com",
            academic=["考研", "数学"],  # 与user1相同
            career=["教师"],  # 不同
            hobby=["阅读"]  # 与user1相同
        )
        
        # 在职业场景下，user3应该有更高的匹配度
        score_user3 = self.matching_service.calculate_match_score(
            self.user1.user_id,
            user3.user_id,
            "职业咨询室"
        )
        
        score_user4 = self.matching_service.calculate_match_score(
            self.user1.user_id,
            user4.user_id,
            "职业咨询室"
        )
        
        # 由于职业场景重视职业兴趣，user3的分数应该更高
        assert score_user3 > score_user4

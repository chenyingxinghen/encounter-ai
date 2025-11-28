"""用户注册与画像构建测试"""
import pytest
from src.models.user import (
    User, UserProfile, BigFiveScores,
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.services.user_profile_service import UserProfileService
from src.utils.exceptions import ValidationError, NotFoundError


class TestUserRegistration:
    """测试用户注册功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
    
    def test_register_user_success(self):
        """测试成功注册用户"""
        request = UserRegistrationRequest(
            username="张三",
            email="zhangsan@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        
        user = self.service.register_user(request)
        
        assert user.username == "张三"
        assert user.email == "zhangsan@example.com"
        assert user.school == "清华大学"
        assert user.major == "计算机科学"
        assert user.grade == 2
        assert user.user_id is not None
        assert user.profile is not None
    
    def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        request1 = UserRegistrationRequest(
            username="张三",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        
        request2 = UserRegistrationRequest(
            username="李四",
            email="test@example.com",
            password="password456",
            school="北京大学",
            major="数学",
            grade=3
        )
        
        self.service.register_user(request1)
        
        with pytest.raises(ValidationError, match="Email already registered"):
            self.service.register_user(request2)


class TestMBTITest:
    """测试MBTI测试功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        self.user = self.service.register_user(request)
    
    def test_mbti_test_success(self):
        """测试成功完成MBTI测试"""
        # 创建60个答案（全部为3，中等倾向）
        answers = [3] * 60
        
        request = MBTITestRequest(
            user_id=self.user.user_id,
            answers=answers
        )
        
        mbti_type = self.service.process_mbti_test(request)
        
        assert mbti_type is not None
        assert len(mbti_type) == 4
        assert mbti_type in [
            'INTJ', 'INTP', 'ENTJ', 'ENTP',
            'INFJ', 'INFP', 'ENFJ', 'ENFP',
            'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
            'ISTP', 'ISFP', 'ESTP', 'ESFP'
        ]
        
        # 验证画像已更新
        profile = self.service.get_profile(self.user.user_id)
        assert profile.mbti_type == mbti_type
    
    def test_mbti_test_invalid_answer_count(self):
        """测试答案数量不正确"""
        answers = [3] * 50  # 只有50个答案
        
        with pytest.raises(ValueError, match="exactly 60 answers"):
            MBTITestRequest(
                user_id=self.user.user_id,
                answers=answers
            )
    
    def test_mbti_test_invalid_answer_value(self):
        """测试答案值不在范围内"""
        answers = [3] * 59 + [6]  # 最后一个答案超出范围
        
        with pytest.raises(ValueError, match="between 1 and 5"):
            MBTITestRequest(
                user_id=self.user.user_id,
                answers=answers
            )
    
    def test_mbti_test_user_not_found(self):
        """测试用户不存在"""
        answers = [3] * 60
        
        request = MBTITestRequest(
            user_id="nonexistent-user-id",
            answers=answers
        )
        
        with pytest.raises(NotFoundError):
            self.service.process_mbti_test(request)


class TestBigFiveTest:
    """测试大五人格测试功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        self.user = self.service.register_user(request)
    
    def test_big_five_test_success(self):
        """测试成功完成大五人格测试"""
        # 创建50个答案
        answers = [3] * 50
        
        request = BigFiveTestRequest(
            user_id=self.user.user_id,
            answers=answers
        )
        
        scores = self.service.process_big_five_test(request)
        
        assert isinstance(scores, BigFiveScores)
        assert 0.0 <= scores.neuroticism <= 1.0
        assert 0.0 <= scores.agreeableness <= 1.0
        assert 0.0 <= scores.extraversion <= 1.0
        assert 0.0 <= scores.openness <= 1.0
        assert 0.0 <= scores.conscientiousness <= 1.0
        
        # 验证画像已更新
        profile = self.service.get_profile(self.user.user_id)
        assert profile.big_five is not None
    
    def test_big_five_test_invalid_answer_count(self):
        """测试答案数量不正确"""
        answers = [3] * 40  # 只有40个答案
        
        with pytest.raises(ValueError, match="exactly 50 answers"):
            BigFiveTestRequest(
                user_id=self.user.user_id,
                answers=answers
            )


class TestInterestSelection:
    """测试兴趣标签选择功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        self.user = self.service.register_user(request)
    
    def test_update_interests_success(self):
        """测试成功更新兴趣标签"""
        request = InterestSelectionRequest(
            user_id=self.user.user_id,
            academic_interests=["考研", "编程"],
            career_interests=["软件工程师", "数据科学家"],
            hobby_interests=["阅读", "音乐"]
        )
        
        profile = self.service.update_interests(request)
        
        assert profile.academic_interests == ["考研", "编程"]
        assert profile.career_interests == ["软件工程师", "数据科学家"]
        assert profile.hobby_interests == ["阅读", "音乐"]


class TestSceneSelection:
    """测试场景选择功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        self.user = self.service.register_user(request)
    
    def test_update_scenes_success(self):
        """测试成功更新场景选择"""
        request = SceneSelectionRequest(
            user_id=self.user.user_id,
            scenes=["考研自习室", "兴趣社群"]
        )
        
        profile = self.service.update_scenes(request)
        
        assert profile.current_scenes == ["考研自习室", "兴趣社群"]
        assert len(profile.scene_priorities) == 2
        assert profile.scene_priorities["考研自习室"] == 0.5
        assert profile.scene_priorities["兴趣社群"] == 0.5
    
    def test_update_scenes_invalid_scene(self):
        """测试无效的场景"""
        with pytest.raises(ValueError, match="Invalid scene"):
            SceneSelectionRequest(
                user_id=self.user.user_id,
                scenes=["无效场景"]
            )


class TestProfileGeneration:
    """测试画像生成功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
        
        # 创建测试用户
        request = UserRegistrationRequest(
            username="测试用户",
            email="test@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        self.user = self.service.register_user(request)
    
    def test_generate_profile_success(self):
        """测试成功生成完整画像"""
        # 完成MBTI测试
        mbti_request = MBTITestRequest(
            user_id=self.user.user_id,
            answers=[3] * 60
        )
        self.service.process_mbti_test(mbti_request)
        
        # 完成大五人格测试
        big_five_request = BigFiveTestRequest(
            user_id=self.user.user_id,
            answers=[3] * 50
        )
        self.service.process_big_five_test(big_five_request)
        
        # 选择兴趣标签
        interest_request = InterestSelectionRequest(
            user_id=self.user.user_id,
            academic_interests=["考研"],
            career_interests=["软件工程师"],
            hobby_interests=["阅读"]
        )
        self.service.update_interests(interest_request)
        
        # 选择场景
        scene_request = SceneSelectionRequest(
            user_id=self.user.user_id,
            scenes=["考研自习室"]
        )
        self.service.update_scenes(scene_request)
        
        # 生成画像
        profile = self.service.generate_initial_profile(self.user.user_id)
        
        assert profile.mbti_type is not None
        assert profile.big_five is not None
        assert len(profile.current_scenes) > 0
        assert len(profile.profile_vector) > 0
    
    def test_generate_profile_missing_mbti(self):
        """测试缺少MBTI类型"""
        # 只完成大五人格测试和场景选择
        big_five_request = BigFiveTestRequest(
            user_id=self.user.user_id,
            answers=[3] * 50
        )
        self.service.process_big_five_test(big_five_request)
        
        scene_request = SceneSelectionRequest(
            user_id=self.user.user_id,
            scenes=["考研自习室"]
        )
        self.service.update_scenes(scene_request)
        
        with pytest.raises(ValidationError, match="MBTI type not set"):
            self.service.generate_initial_profile(self.user.user_id)
    
    def test_generate_profile_missing_big_five(self):
        """测试缺少大五人格得分"""
        # 只完成MBTI测试和场景选择
        mbti_request = MBTITestRequest(
            user_id=self.user.user_id,
            answers=[3] * 60
        )
        self.service.process_mbti_test(mbti_request)
        
        scene_request = SceneSelectionRequest(
            user_id=self.user.user_id,
            scenes=["考研自习室"]
        )
        self.service.update_scenes(scene_request)
        
        with pytest.raises(ValidationError, match="Big Five scores not set"):
            self.service.generate_initial_profile(self.user.user_id)
    
    def test_generate_profile_missing_scenes(self):
        """测试缺少场景选择"""
        # 只完成MBTI和大五人格测试
        mbti_request = MBTITestRequest(
            user_id=self.user.user_id,
            answers=[3] * 60
        )
        self.service.process_mbti_test(mbti_request)
        
        big_five_request = BigFiveTestRequest(
            user_id=self.user.user_id,
            answers=[3] * 50
        )
        self.service.process_big_five_test(big_five_request)
        
        with pytest.raises(ValidationError, match="Scenes not selected"):
            self.service.generate_initial_profile(self.user.user_id)


class TestCompleteRegistrationFlow:
    """测试完整的注册流程"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = UserProfileService()
    
    def test_complete_registration_flow(self):
        """测试完整的注册流程"""
        # 1. 用户注册
        registration_request = UserRegistrationRequest(
            username="完整流程测试",
            email="complete@example.com",
            password="password123",
            school="清华大学",
            major="计算机科学",
            grade=2
        )
        user = self.service.register_user(registration_request)
        assert user.user_id is not None
        
        # 2. 完成MBTI测试
        mbti_request = MBTITestRequest(
            user_id=user.user_id,
            answers=[4] * 60  # 倾向于E/S/T/J
        )
        mbti_type = self.service.process_mbti_test(mbti_request)
        assert mbti_type is not None
        
        # 3. 完成大五人格测试
        big_five_request = BigFiveTestRequest(
            user_id=user.user_id,
            answers=[4] * 50
        )
        scores = self.service.process_big_five_test(big_five_request)
        assert scores is not None
        
        # 4. 选择兴趣标签
        interest_request = InterestSelectionRequest(
            user_id=user.user_id,
            academic_interests=["考研", "编程"],
            career_interests=["软件工程师"],
            hobby_interests=["阅读", "音乐", "运动"]
        )
        profile = self.service.update_interests(interest_request)
        assert len(profile.academic_interests) == 2
        
        # 5. 选择场景
        scene_request = SceneSelectionRequest(
            user_id=user.user_id,
            scenes=["考研自习室", "兴趣社群"]
        )
        profile = self.service.update_scenes(scene_request)
        assert len(profile.current_scenes) == 2
        
        # 6. 生成初始画像
        final_profile = self.service.generate_initial_profile(user.user_id)
        assert final_profile.mbti_type is not None
        assert final_profile.big_five is not None
        assert len(final_profile.current_scenes) > 0
        assert len(final_profile.profile_vector) > 0
        
        # 验证画像向量维度正确
        # MBTI(4) + BigFive(5) + Emotion(2) + Behavior(2) = 13
        assert len(final_profile.profile_vector) == 13

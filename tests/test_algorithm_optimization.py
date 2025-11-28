"""匹配算法优化测试"""
import pytest
from datetime import datetime, timedelta
from src.models.user import (
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.services.algorithm_optimization_service import AlgorithmOptimizationService
from src.models.optimization import (
    FeedbackData, WeightAdjustment, ABTestConfig, ABTestResult, PerformanceMetrics
)
from src.utils.exceptions import ValidationError, NotFoundError


class TestFeedbackCollection:
    """测试反馈数据收集"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.optimization_service = AlgorithmOptimizationService(self.matching_service)
    
    def test_collect_feedback(self):
        """测试收集反馈"""
        feedback = self.optimization_service.collect_feedback(
            user_id="user1",
            match_id="match1",
            scene="考研自习室",
            satisfaction_score=4.5,
            conversation_quality=8.0,
            match_accuracy=4.0,
            positive_aspects=["人格匹配", "话题相投"],
            negative_aspects=[],
            suggestions="很好"
        )
        
        assert isinstance(feedback, FeedbackData)
        assert feedback.user_id == "user1"
        assert feedback.match_id == "match1"
        assert feedback.scene == "考研自习室"
        assert feedback.satisfaction_score == 4.5
        assert feedback.conversation_quality == 8.0
        assert feedback.match_accuracy == 4.0
        assert len(feedback.positive_aspects) == 2
    
    def test_collect_feedback_invalid_score(self):
        """测试无效的评分"""
        with pytest.raises(ValidationError, match="Satisfaction score"):
            self.optimization_service.collect_feedback(
                user_id="user1",
                match_id="match1",
                scene="考研自习室",
                satisfaction_score=6.0,  # 超出范围
                conversation_quality=8.0,
                match_accuracy=4.0
            )
    
    def test_get_feedback(self):
        """测试获取反馈"""
        feedback = self.optimization_service.collect_feedback(
            user_id="user1",
            match_id="match1",
            scene="考研自习室",
            satisfaction_score=4.5,
            conversation_quality=8.0,
            match_accuracy=4.0
        )
        
        retrieved = self.optimization_service.get_feedback(feedback.feedback_id)
        assert retrieved.feedback_id == feedback.feedback_id
        assert retrieved.user_id == "user1"
    
    def test_get_feedbacks_by_scene(self):
        """测试按场景获取反馈"""
        # 创建多个反馈
        self.optimization_service.collect_feedback(
            user_id="user1",
            match_id="match1",
            scene="考研自习室",
            satisfaction_score=4.5,
            conversation_quality=8.0,
            match_accuracy=4.0
        )
        
        self.optimization_service.collect_feedback(
            user_id="user2",
            match_id="match2",
            scene="考研自习室",
            satisfaction_score=3.5,
            conversation_quality=7.0,
            match_accuracy=3.5
        )
        
        self.optimization_service.collect_feedback(
            user_id="user3",
            match_id="match3",
            scene="职业咨询室",
            satisfaction_score=4.0,
            conversation_quality=7.5,
            match_accuracy=4.0
        )
        
        feedbacks = self.optimization_service.get_feedbacks_by_scene("考研自习室")
        assert len(feedbacks) == 2
        assert all(fb.scene == "考研自习室" for fb in feedbacks)


class TestWeightAdjustment:
    """测试权重动态调整"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.optimization_service = AlgorithmOptimizationService(self.matching_service)
    
    def test_adjust_weights(self):
        """测试调整权重"""
        new_weights = {
            'personality': 0.3,
            'interest': 0.4,
            'scene': 0.2,
            'emotion': 0.1
        }
        
        adjustment = self.optimization_service.adjust_weights(
            scene="考研自习室",
            new_weights=new_weights,
            reason="测试调整"
        )
        
        assert isinstance(adjustment, WeightAdjustment)
        assert adjustment.scene == "考研自习室"
        assert adjustment.new_weights == new_weights
        assert adjustment.reason == "测试调整"
        assert adjustment.performance_before >= 0.0
        
        # 验证权重已应用
        config = self.matching_service.get_scene_config("考研自习室")
        assert config.match_weights == new_weights
    
    def test_evaluate_weight_adjustment(self):
        """测试评估权重调整"""
        new_weights = {
            'personality': 0.3,
            'interest': 0.4,
            'scene': 0.2,
            'emotion': 0.1
        }
        
        adjustment = self.optimization_service.adjust_weights(
            scene="考研自习室",
            new_weights=new_weights,
            reason="测试调整"
        )
        
        # 添加一些反馈数据
        self.optimization_service.collect_feedback(
            user_id="user1",
            match_id="match1",
            scene="考研自习室",
            satisfaction_score=4.5,
            conversation_quality=8.0,
            match_accuracy=4.0
        )
        
        # 评估调整
        evaluated = self.optimization_service.evaluate_weight_adjustment(
            adjustment.adjustment_id
        )
        
        assert evaluated.performance_after is not None
        assert evaluated.evaluated_at is not None
    
    def test_auto_adjust_weights(self):
        """测试自动调整权重"""
        # 创建足够的反馈数据，包含明显的问题
        for i in range(15):
            self.optimization_service.collect_feedback(
                user_id=f"user{i}",
                match_id=f"match{i}",
                scene="考研自习室",
                satisfaction_score=2.5,
                conversation_quality=5.0,
                match_accuracy=2.0,
                negative_aspects=["人格不匹配"]
            )
        
        # 自动调整
        adjustment = self.optimization_service.auto_adjust_weights("考研自习室")
        
        # 应该创建调整记录
        assert adjustment is not None
        assert "人格匹配" in adjustment.reason
        
        # 人格权重应该增加
        config = self.matching_service.get_scene_config("考研自习室")
        assert config.match_weights['personality'] > 0.25
    
    def test_auto_adjust_insufficient_data(self):
        """测试数据不足时不调整"""
        # 只有少量反馈
        for i in range(5):
            self.optimization_service.collect_feedback(
                user_id=f"user{i}",
                match_id=f"match{i}",
                scene="考研自习室",
                satisfaction_score=2.5,
                conversation_quality=5.0,
                match_accuracy=2.0
            )
        
        adjustment = self.optimization_service.auto_adjust_weights("考研自习室")
        assert adjustment is None


class TestABTesting:
    """测试A/B测试框架"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.optimization_service = AlgorithmOptimizationService(self.matching_service)
    
    def test_create_ab_test(self):
        """测试创建A/B测试"""
        control_weights = {
            'personality': 0.25,
            'interest': 0.35,
            'scene': 0.30,
            'emotion': 0.10
        }
        
        treatment_weights = {
            'personality': 0.35,
            'interest': 0.30,
            'scene': 0.25,
            'emotion': 0.10
        }
        
        test_config = self.optimization_service.create_ab_test(
            test_name="人格权重测试",
            scene="考研自习室",
            control_weights=control_weights,
            treatment_weights=treatment_weights,
            traffic_split=0.5,
            min_sample_size=50
        )
        
        assert isinstance(test_config, ABTestConfig)
        assert test_config.test_name == "人格权重测试"
        assert test_config.scene == "考研自习室"
        assert test_config.control_weights == control_weights
        assert test_config.treatment_weights == treatment_weights
        assert test_config.traffic_split == 0.5
        assert test_config.status == "active"
    
    def test_assign_to_test_group(self):
        """测试分配测试组"""
        control_weights = {
            'personality': 0.25,
            'interest': 0.35,
            'scene': 0.30,
            'emotion': 0.10
        }
        
        treatment_weights = {
            'personality': 0.35,
            'interest': 0.30,
            'scene': 0.25,
            'emotion': 0.10
        }
        
        test_config = self.optimization_service.create_ab_test(
            test_name="测试",
            scene="考研自习室",
            control_weights=control_weights,
            treatment_weights=treatment_weights
        )
        
        # 分配用户
        group1 = self.optimization_service.assign_to_test_group(
            test_config.test_id,
            "user1"
        )
        
        assert group1 in ["control", "treatment"]
        
        # 同一用户应该得到相同的分配
        group2 = self.optimization_service.assign_to_test_group(
            test_config.test_id,
            "user1"
        )
        
        assert group1 == group2
    
    def test_get_test_weights(self):
        """测试获取测试权重"""
        control_weights = {
            'personality': 0.25,
            'interest': 0.35,
            'scene': 0.30,
            'emotion': 0.10
        }
        
        treatment_weights = {
            'personality': 0.35,
            'interest': 0.30,
            'scene': 0.25,
            'emotion': 0.10
        }
        
        test_config = self.optimization_service.create_ab_test(
            test_name="测试",
            scene="考研自习室",
            control_weights=control_weights,
            treatment_weights=treatment_weights
        )
        
        weights = self.optimization_service.get_test_weights(
            test_config.test_id,
            "user1"
        )
        
        # 应该返回对照组或实验组的权重
        assert weights in [control_weights, treatment_weights]
    
    def test_evaluate_ab_test(self):
        """测试评估A/B测试"""
        control_weights = {
            'personality': 0.25,
            'interest': 0.35,
            'scene': 0.30,
            'emotion': 0.10
        }
        
        treatment_weights = {
            'personality': 0.35,
            'interest': 0.30,
            'scene': 0.25,
            'emotion': 0.10
        }
        
        test_config = self.optimization_service.create_ab_test(
            test_name="测试",
            scene="考研自习室",
            control_weights=control_weights,
            treatment_weights=treatment_weights,
            min_sample_size=10
        )
        
        # 创建足够的反馈数据（增加数量以确保两组都有足够样本）
        for i in range(30):
            user_id = f"user{i}"
            group = self.optimization_service.assign_to_test_group(
                test_config.test_id,
                user_id
            )
            
            # 实验组表现更好
            if group == "treatment":
                satisfaction = 4.5
                quality = 8.5
            else:
                satisfaction = 3.5
                quality = 7.0
            
            self.optimization_service.collect_feedback(
                user_id=user_id,
                match_id=f"match{i}",
                scene="考研自习室",
                satisfaction_score=satisfaction,
                conversation_quality=quality,
                match_accuracy=4.0
            )
        
        # 评估测试
        result = self.optimization_service.evaluate_ab_test(test_config.test_id)
        
        assert isinstance(result, ABTestResult)
        assert result.test_id == test_config.test_id
        assert result.control_sample_size >= 10
        assert result.treatment_sample_size >= 10
        assert result.winner in ["control", "treatment", "tie"]
    
    def test_complete_ab_test(self):
        """测试完成A/B测试"""
        control_weights = {
            'personality': 0.25,
            'interest': 0.35,
            'scene': 0.30,
            'emotion': 0.10
        }
        
        treatment_weights = {
            'personality': 0.35,
            'interest': 0.30,
            'scene': 0.25,
            'emotion': 0.10
        }
        
        test_config = self.optimization_service.create_ab_test(
            test_name="测试",
            scene="考研自习室",
            control_weights=control_weights,
            treatment_weights=treatment_weights
        )
        
        self.optimization_service.complete_ab_test(test_config.test_id)
        
        # 验证状态已更新
        updated_config = self.optimization_service._ab_tests[test_config.test_id]
        assert updated_config.status == "completed"
        assert updated_config.end_date is not None


class TestPerformanceMetrics:
    """测试性能评估"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.optimization_service = AlgorithmOptimizationService(self.matching_service)
    
    def test_calculate_performance_metrics(self):
        """测试计算性能指标"""
        # 创建反馈数据
        for i in range(10):
            self.optimization_service.collect_feedback(
                user_id=f"user{i}",
                match_id=f"match{i}",
                scene="考研自习室",
                satisfaction_score=4.0,
                conversation_quality=7.5,
                match_accuracy=3.8
            )
        
        metrics = self.optimization_service.calculate_performance_metrics(
            scene="考研自习室",
            period_days=7
        )
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.scene == "考研自习室"
        assert metrics.total_feedbacks == 10
        assert metrics.avg_satisfaction == 4.0
        assert metrics.avg_conversation_quality == 7.5
        assert metrics.avg_match_accuracy == 3.8
    
    def test_calculate_performance_metrics_no_data(self):
        """测试没有数据时的性能指标"""
        metrics = self.optimization_service.calculate_performance_metrics(
            scene="考研自习室",
            period_days=7
        )
        
        assert metrics.total_feedbacks == 0
        assert metrics.avg_satisfaction == 0.0
    
    def test_generate_optimization_report(self):
        """测试生成优化报告"""
        # 创建一些数据
        for i in range(5):
            self.optimization_service.collect_feedback(
                user_id=f"user{i}",
                match_id=f"match{i}",
                scene="考研自习室",
                satisfaction_score=4.0,
                conversation_quality=7.5,
                match_accuracy=3.8
            )
        
        report = self.optimization_service.generate_optimization_report("考研自习室")
        
        assert isinstance(report, dict)
        assert "scene" in report
        assert "performance_metrics" in report
        assert "recent_adjustments" in report
        assert "active_ab_tests" in report
        assert "recommendations" in report
        assert len(report["recommendations"]) > 0


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.profile_service = UserProfileService()
        self.matching_service = MatchingService(self.profile_service)
        self.optimization_service = AlgorithmOptimizationService(self.matching_service)
        
        # 创建测试用户
        self.users = []
        for i in range(5):
            user = self.profile_service.register_user(
                UserRegistrationRequest(
                    username=f"用户{i}",
                    email=f"user{i}@example.com",
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
                    academic_interests=["考研"],
                    career_interests=["工程师"],
                    hobby_interests=["阅读"]
                )
            )
            
            self.profile_service.update_scenes(
                SceneSelectionRequest(user_id=user.user_id, scenes=["考研自习室"])
            )
            
            self.profile_service.generate_initial_profile(user.user_id)
            self.users.append(user)
    
    def test_full_optimization_workflow(self):
        """测试完整的优化流程"""
        # 1. 进行匹配
        matches = self.matching_service.find_matches(
            self.users[0].user_id,
            "考研自习室",
            limit=3
        )
        
        assert len(matches) > 0
        
        # 2. 收集反馈
        for i, match in enumerate(matches):
            self.optimization_service.collect_feedback(
                user_id=self.users[0].user_id,
                match_id=match.match_id,
                scene="考研自习室",
                satisfaction_score=3.0 + i * 0.5,
                conversation_quality=6.0 + i,
                match_accuracy=3.0 + i * 0.3
            )
        
        # 3. 计算性能指标
        metrics = self.optimization_service.calculate_performance_metrics("考研自习室")
        assert metrics.total_feedbacks == len(matches)
        
        # 4. 调整权重
        new_weights = {
            'personality': 0.3,
            'interest': 0.4,
            'scene': 0.2,
            'emotion': 0.1
        }
        adjustment = self.optimization_service.adjust_weights(
            "考研自习室",
            new_weights,
            "基于反馈优化"
        )
        
        assert adjustment is not None
        
        # 5. 评估调整效果
        evaluated = self.optimization_service.evaluate_weight_adjustment(
            adjustment.adjustment_id
        )
        
        assert evaluated.performance_after is not None
        
        # 6. 生成报告
        report = self.optimization_service.generate_optimization_report("考研自习室")
        assert len(report["recent_adjustments"]) > 0

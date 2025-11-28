"""匹配算法优化服务"""
import uuid
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from src.models.optimization import (
    FeedbackData, WeightAdjustment, ABTestConfig, ABTestResult, PerformanceMetrics
)
from src.utils.exceptions import ValidationError, NotFoundError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlgorithmOptimizationService:
    """匹配算法优化服务类"""
    
    def __init__(self, matching_service=None):
        """
        初始化算法优化服务
        
        Args:
            matching_service: 匹配服务实例（用于依赖注入）
        """
        self._matching_service = matching_service
        self._feedbacks: Dict[str, FeedbackData] = {}
        self._weight_adjustments: Dict[str, WeightAdjustment] = {}
        self._ab_tests: Dict[str, ABTestConfig] = {}
        self._ab_test_results: Dict[str, ABTestResult] = {}
        self._ab_test_assignments: Dict[str, str] = {}  # user_id -> group (control/treatment)
        self.logger = logger
    
    # ==================== 反馈数据收集 ====================
    
    def collect_feedback(
        self,
        user_id: str,
        match_id: str,
        scene: str,
        satisfaction_score: float,
        conversation_quality: float,
        match_accuracy: float,
        positive_aspects: List[str] = None,
        negative_aspects: List[str] = None,
        suggestions: str = ""
    ) -> FeedbackData:
        """
        收集用户反馈数据
        
        Args:
            user_id: 用户ID
            match_id: 匹配记录ID
            scene: 场景
            satisfaction_score: 满意度评分 (0-5)
            conversation_quality: 对话质量评分 (0-10)
            match_accuracy: 匹配准确度评分 (0-5)
            positive_aspects: 积极方面
            negative_aspects: 消极方面
            suggestions: 改进建议
            
        Returns:
            FeedbackData: 反馈数据
        """
        # 验证评分范围
        if not (0.0 <= satisfaction_score <= 5.0):
            raise ValidationError("Satisfaction score must be between 0 and 5")
        if not (0.0 <= conversation_quality <= 10.0):
            raise ValidationError("Conversation quality must be between 0 and 10")
        if not (0.0 <= match_accuracy <= 5.0):
            raise ValidationError("Match accuracy must be between 0 and 5")
        
        feedback = FeedbackData(
            feedback_id=str(uuid.uuid4()),
            user_id=user_id,
            match_id=match_id,
            scene=scene,
            satisfaction_score=satisfaction_score,
            conversation_quality=conversation_quality,
            match_accuracy=match_accuracy,
            positive_aspects=positive_aspects or [],
            negative_aspects=negative_aspects or [],
            suggestions=suggestions
        )
        
        self._feedbacks[feedback.feedback_id] = feedback
        self.logger.info(f"Collected feedback from user {user_id} for match {match_id}")
        
        return feedback
    
    def get_feedback(self, feedback_id: str) -> FeedbackData:
        """
        获取反馈数据
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            FeedbackData: 反馈数据
        """
        if feedback_id not in self._feedbacks:
            raise NotFoundError(f"Feedback not found: {feedback_id}")
        return self._feedbacks[feedback_id]
    
    def get_feedbacks_by_scene(
        self,
        scene: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[FeedbackData]:
        """
        获取特定场景的反馈数据
        
        Args:
            scene: 场景
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            List[FeedbackData]: 反馈数据列表
        """
        feedbacks = [
            fb for fb in self._feedbacks.values()
            if fb.scene == scene
        ]
        
        if start_date:
            feedbacks = [fb for fb in feedbacks if fb.created_at >= start_date]
        if end_date:
            feedbacks = [fb for fb in feedbacks if fb.created_at <= end_date]
        
        return feedbacks
    
    # ==================== 权重动态调整 ====================
    
    def adjust_weights(
        self,
        scene: str,
        new_weights: Dict[str, float],
        reason: str
    ) -> WeightAdjustment:
        """
        动态调整匹配权重
        
        Args:
            scene: 场景
            new_weights: 新的权重配置
            reason: 调整原因
            
        Returns:
            WeightAdjustment: 权重调整记录
        """
        if not self._matching_service:
            raise ValidationError("Matching service not initialized")
        
        # 获取当前权重
        scene_config = self._matching_service.get_scene_config(scene)
        old_weights = scene_config.match_weights.copy()
        
        # 计算调整前的性能指标
        performance_before = self._calculate_performance_score(scene)
        
        # 创建调整记录
        adjustment = WeightAdjustment(
            adjustment_id=str(uuid.uuid4()),
            scene=scene,
            old_weights=old_weights,
            new_weights=new_weights,
            reason=reason,
            performance_before=performance_before
        )
        
        # 应用新权重
        self._matching_service.update_match_weights(scene, new_weights)
        
        self._weight_adjustments[adjustment.adjustment_id] = adjustment
        self.logger.info(f"Adjusted weights for scene {scene}: {reason}")
        
        return adjustment
    
    def evaluate_weight_adjustment(
        self,
        adjustment_id: str
    ) -> WeightAdjustment:
        """
        评估权重调整效果
        
        Args:
            adjustment_id: 调整记录ID
            
        Returns:
            WeightAdjustment: 更新后的调整记录
        """
        if adjustment_id not in self._weight_adjustments:
            raise NotFoundError(f"Weight adjustment not found: {adjustment_id}")
        
        adjustment = self._weight_adjustments[adjustment_id]
        
        # 计算调整后的性能指标
        performance_after = self._calculate_performance_score(adjustment.scene)
        
        adjustment.performance_after = performance_after
        adjustment.evaluated_at = datetime.now()
        
        self.logger.info(
            f"Evaluated weight adjustment {adjustment_id}: "
            f"before={adjustment.performance_before:.2f}, "
            f"after={performance_after:.2f}"
        )
        
        return adjustment
    
    def _calculate_performance_score(self, scene: str) -> float:
        """
        计算场景的性能得分
        
        Args:
            scene: 场景
            
        Returns:
            float: 性能得分 (0-100)
        """
        # 获取最近的反馈数据
        recent_feedbacks = self.get_feedbacks_by_scene(
            scene,
            start_date=datetime.now() - timedelta(days=7)
        )
        
        if not recent_feedbacks:
            return 50.0  # 默认中等分数
        
        # 计算平均满意度和质量
        avg_satisfaction = sum(fb.satisfaction_score for fb in recent_feedbacks) / len(recent_feedbacks)
        avg_quality = sum(fb.conversation_quality for fb in recent_feedbacks) / len(recent_feedbacks)
        avg_accuracy = sum(fb.match_accuracy for fb in recent_feedbacks) / len(recent_feedbacks)
        
        # 综合得分（归一化到0-100）
        score = (
            (avg_satisfaction / 5.0) * 0.4 +
            (avg_quality / 10.0) * 0.4 +
            (avg_accuracy / 5.0) * 0.2
        ) * 100
        
        return round(score, 2)
    
    def auto_adjust_weights(self, scene: str) -> Optional[WeightAdjustment]:
        """
        基于反馈数据自动调整权重
        
        Args:
            scene: 场景
            
        Returns:
            Optional[WeightAdjustment]: 调整记录，如果不需要调整则返回None
        """
        # 获取最近的反馈数据
        recent_feedbacks = self.get_feedbacks_by_scene(
            scene,
            start_date=datetime.now() - timedelta(days=7)
        )
        
        if len(recent_feedbacks) < 10:
            self.logger.info(f"Not enough feedback data for auto-adjustment in {scene}")
            return None
        
        # 分析反馈中的消极方面
        negative_counts = defaultdict(int)
        for fb in recent_feedbacks:
            for aspect in fb.negative_aspects:
                negative_counts[aspect] += 1
        
        # 如果没有明显的问题，不调整
        if not negative_counts:
            return None
        
        # 找出最常见的问题
        most_common_issue = max(negative_counts.items(), key=lambda x: x[1])
        issue, count = most_common_issue
        
        # 如果问题不够普遍，不调整
        if count < len(recent_feedbacks) * 0.3:
            return None
        
        # 根据问题类型调整权重
        current_config = self._matching_service.get_scene_config(scene)
        new_weights = current_config.match_weights.copy()
        
        if "人格不匹配" in issue or "性格差异" in issue:
            # 增加人格权重
            new_weights['personality'] = min(new_weights.get('personality', 0.25) + 0.1, 0.6)
            reason = f"自动调整：用户反馈人格匹配问题（{count}次）"
        elif "兴趣不同" in issue or "话题不合" in issue:
            # 增加兴趣权重
            new_weights['interest'] = min(new_weights.get('interest', 0.25) + 0.1, 0.6)
            reason = f"自动调整：用户反馈兴趣匹配问题（{count}次）"
        elif "情绪不同步" in issue or "情感不协调" in issue:
            # 增加情感权重
            new_weights['emotion'] = min(new_weights.get('emotion', 0.25) + 0.1, 0.6)
            reason = f"自动调整：用户反馈情感同步问题（{count}次）"
        else:
            return None
        
        # 归一化权重
        total = sum(new_weights.values())
        new_weights = {k: v / total for k, v in new_weights.items()}
        
        return self.adjust_weights(scene, new_weights, reason)
    
    # ==================== A/B测试框架 ====================
    
    def create_ab_test(
        self,
        test_name: str,
        scene: str,
        control_weights: Dict[str, float],
        treatment_weights: Dict[str, float],
        traffic_split: float = 0.5,
        min_sample_size: int = 100
    ) -> ABTestConfig:
        """
        创建A/B测试
        
        Args:
            test_name: 测试名称
            scene: 测试场景
            control_weights: 对照组权重
            treatment_weights: 实验组权重
            traffic_split: 流量分配比例（实验组占比）
            min_sample_size: 最小样本量
            
        Returns:
            ABTestConfig: A/B测试配置
        """
        # 验证权重
        if abs(sum(control_weights.values()) - 1.0) > 0.01:
            raise ValidationError("Control weights must sum to 1.0")
        if abs(sum(treatment_weights.values()) - 1.0) > 0.01:
            raise ValidationError("Treatment weights must sum to 1.0")
        
        test_config = ABTestConfig(
            test_id=str(uuid.uuid4()),
            test_name=test_name,
            scene=scene,
            control_weights=control_weights,
            treatment_weights=treatment_weights,
            traffic_split=traffic_split,
            min_sample_size=min_sample_size
        )
        
        self._ab_tests[test_config.test_id] = test_config
        self.logger.info(f"Created A/B test: {test_name} for scene {scene}")
        
        return test_config
    
    def assign_to_test_group(
        self,
        test_id: str,
        user_id: str
    ) -> str:
        """
        将用户分配到测试组
        
        Args:
            test_id: 测试ID
            user_id: 用户ID
            
        Returns:
            str: 分配的组别 (control 或 treatment)
        """
        if test_id not in self._ab_tests:
            raise NotFoundError(f"A/B test not found: {test_id}")
        
        test_config = self._ab_tests[test_id]
        
        # 检查用户是否已经分配
        assignment_key = f"{test_id}:{user_id}"
        if assignment_key in self._ab_test_assignments:
            return self._ab_test_assignments[assignment_key]
        
        # 随机分配
        group = "treatment" if random.random() < test_config.traffic_split else "control"
        self._ab_test_assignments[assignment_key] = group
        
        return group
    
    def get_test_weights(
        self,
        test_id: str,
        user_id: str
    ) -> Dict[str, float]:
        """
        获取用户在测试中应使用的权重
        
        Args:
            test_id: 测试ID
            user_id: 用户ID
            
        Returns:
            Dict[str, float]: 权重配置
        """
        if test_id not in self._ab_tests:
            raise NotFoundError(f"A/B test not found: {test_id}")
        
        test_config = self._ab_tests[test_id]
        group = self.assign_to_test_group(test_id, user_id)
        
        if group == "treatment":
            return test_config.treatment_weights
        else:
            return test_config.control_weights
    
    def evaluate_ab_test(
        self,
        test_id: str
    ) -> ABTestResult:
        """
        评估A/B测试结果
        
        Args:
            test_id: 测试ID
            
        Returns:
            ABTestResult: 测试结果
        """
        if test_id not in self._ab_tests:
            raise NotFoundError(f"A/B test not found: {test_id}")
        
        test_config = self._ab_tests[test_id]
        
        # 收集两组的反馈数据
        control_feedbacks = []
        treatment_feedbacks = []
        
        for assignment_key, group in self._ab_test_assignments.items():
            if not assignment_key.startswith(f"{test_id}:"):
                continue
            
            user_id = assignment_key.split(":")[1]
            user_feedbacks = [
                fb for fb in self._feedbacks.values()
                if fb.user_id == user_id and fb.scene == test_config.scene
            ]
            
            if group == "control":
                control_feedbacks.extend(user_feedbacks)
            else:
                treatment_feedbacks.extend(user_feedbacks)
        
        # 检查样本量
        if len(control_feedbacks) < test_config.min_sample_size:
            raise ValidationError(
                f"Insufficient control group sample size: "
                f"{len(control_feedbacks)} < {test_config.min_sample_size}"
            )
        if len(treatment_feedbacks) < test_config.min_sample_size:
            raise ValidationError(
                f"Insufficient treatment group sample size: "
                f"{len(treatment_feedbacks)} < {test_config.min_sample_size}"
            )
        
        # 计算统计指标
        control_satisfaction = sum(fb.satisfaction_score for fb in control_feedbacks) / len(control_feedbacks)
        control_quality = sum(fb.conversation_quality for fb in control_feedbacks) / len(control_feedbacks)
        
        treatment_satisfaction = sum(fb.satisfaction_score for fb in treatment_feedbacks) / len(treatment_feedbacks)
        treatment_quality = sum(fb.conversation_quality for fb in treatment_feedbacks) / len(treatment_feedbacks)
        
        # 简化的统计显著性检验（实际应使用t检验）
        satisfaction_diff = abs(treatment_satisfaction - control_satisfaction)
        quality_diff = abs(treatment_quality - control_quality)
        
        # 简化的p值计算（实际应使用统计检验）
        p_value = max(0.01, 1.0 - (satisfaction_diff + quality_diff) / 10.0)
        is_significant = p_value < 0.05
        
        # 确定获胜组
        if not is_significant:
            winner = "tie"
            recommendation = "差异不显著，建议继续使用当前配置"
        elif treatment_satisfaction > control_satisfaction and treatment_quality > control_quality:
            winner = "treatment"
            recommendation = "实验组表现更好，建议采用新权重配置"
        elif control_satisfaction > treatment_satisfaction and control_quality > treatment_quality:
            winner = "control"
            recommendation = "对照组表现更好，建议保持当前配置"
        else:
            winner = "tie"
            recommendation = "两组各有优势，建议进一步测试"
        
        result = ABTestResult(
            test_id=test_id,
            control_sample_size=len(control_feedbacks),
            control_avg_satisfaction=control_satisfaction,
            control_avg_quality=control_quality,
            treatment_sample_size=len(treatment_feedbacks),
            treatment_avg_satisfaction=treatment_satisfaction,
            treatment_avg_quality=treatment_quality,
            is_significant=is_significant,
            p_value=p_value,
            winner=winner,
            recommendation=recommendation
        )
        
        self._ab_test_results[test_id] = result
        self.logger.info(f"Evaluated A/B test {test_id}: winner={winner}")
        
        return result
    
    def complete_ab_test(
        self,
        test_id: str,
        apply_winner: bool = False
    ) -> None:
        """
        完成A/B测试
        
        Args:
            test_id: 测试ID
            apply_winner: 是否应用获胜组的配置
        """
        if test_id not in self._ab_tests:
            raise NotFoundError(f"A/B test not found: {test_id}")
        
        test_config = self._ab_tests[test_id]
        test_config.status = "completed"
        test_config.end_date = datetime.now()
        
        if apply_winner and test_id in self._ab_test_results:
            result = self._ab_test_results[test_id]
            if result.winner == "treatment":
                self.adjust_weights(
                    test_config.scene,
                    test_config.treatment_weights,
                    f"A/B测试结果：实验组获胜（p={result.p_value:.4f}）"
                )
        
        self.logger.info(f"Completed A/B test {test_id}")
    
    # ==================== 性能评估 ====================
    
    def calculate_performance_metrics(
        self,
        scene: str,
        period_days: int = 7
    ) -> PerformanceMetrics:
        """
        计算性能指标
        
        Args:
            scene: 场景
            period_days: 统计周期（天）
            
        Returns:
            PerformanceMetrics: 性能指标
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # 获取反馈数据
        feedbacks = self.get_feedbacks_by_scene(scene, start_date, end_date)
        
        if not feedbacks:
            # 返回默认指标
            return PerformanceMetrics(
                scene=scene,
                period_start=start_date,
                period_end=end_date,
                total_matches=0,
                avg_match_score=0.0,
                total_feedbacks=0,
                avg_satisfaction=0.0,
                avg_conversation_quality=0.0,
                avg_match_accuracy=0.0,
                avg_conversation_duration=0.0,
                avg_message_count=0.0
            )
        
        # 计算指标
        total_feedbacks = len(feedbacks)
        avg_satisfaction = sum(fb.satisfaction_score for fb in feedbacks) / total_feedbacks
        avg_quality = sum(fb.conversation_quality for fb in feedbacks) / total_feedbacks
        avg_accuracy = sum(fb.match_accuracy for fb in feedbacks) / total_feedbacks
        
        # 获取匹配数据（简化版本）
        unique_matches = len(set(fb.match_id for fb in feedbacks))
        
        metrics = PerformanceMetrics(
            scene=scene,
            period_start=start_date,
            period_end=end_date,
            total_matches=unique_matches,
            avg_match_score=75.0,  # 简化：使用固定值
            total_feedbacks=total_feedbacks,
            avg_satisfaction=avg_satisfaction,
            avg_conversation_quality=avg_quality,
            avg_match_accuracy=avg_accuracy,
            avg_conversation_duration=30.0,  # 简化：使用固定值
            avg_message_count=50.0  # 简化：使用固定值
        )
        
        return metrics
    
    def generate_optimization_report(
        self,
        scene: str
    ) -> Dict:
        """
        生成优化报告
        
        Args:
            scene: 场景
            
        Returns:
            Dict: 优化报告
        """
        # 计算性能指标
        metrics = self.calculate_performance_metrics(scene)
        
        # 获取最近的权重调整
        recent_adjustments = [
            adj for adj in self._weight_adjustments.values()
            if adj.scene == scene and adj.created_at >= datetime.now() - timedelta(days=30)
        ]
        
        # 获取活跃的A/B测试
        active_tests = [
            test for test in self._ab_tests.values()
            if test.scene == scene and test.status == "active"
        ]
        
        report = {
            "scene": scene,
            "performance_metrics": metrics.dict(),
            "recent_adjustments": [adj.dict() for adj in recent_adjustments],
            "active_ab_tests": [test.dict() for test in active_tests],
            "recommendations": self._generate_recommendations(scene, metrics)
        }
        
        return report
    
    def _generate_recommendations(
        self,
        scene: str,
        metrics: PerformanceMetrics
    ) -> List[str]:
        """
        生成优化建议
        
        Args:
            scene: 场景
            metrics: 性能指标
            
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        # 基于满意度的建议
        if metrics.avg_satisfaction < 3.0:
            recommendations.append("用户满意度较低，建议检查匹配算法权重配置")
        
        # 基于对话质量的建议
        if metrics.avg_conversation_quality < 5.0:
            recommendations.append("对话质量偏低，建议增加人格和兴趣匹配权重")
        
        # 基于匹配准确度的建议
        if metrics.avg_match_accuracy < 3.0:
            recommendations.append("匹配准确度不足，建议进行A/B测试优化权重")
        
        # 基于反馈数量的建议
        if metrics.total_feedbacks < 10:
            recommendations.append("反馈数据不足，建议增加用户反馈收集")
        
        if not recommendations:
            recommendations.append("当前性能良好，建议继续监控")
        
        return recommendations

"""智能匹配服务"""
import uuid
import math
from typing import List, Dict, Optional
from datetime import datetime
from src.models.matching import Match, SceneConfig, MatchRequest, MatchResult
from src.models.user import UserProfile
from src.utils.exceptions import NotFoundError, ValidationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MatchingService:
    """智能匹配服务类"""
    
    def __init__(self, user_profile_service=None):
        """
        初始化匹配服务
        
        Args:
            user_profile_service: 用户画像服务实例（用于依赖注入）
        """
        self._user_profile_service = user_profile_service
        self._matches: Dict[str, Match] = {}
        self._scene_configs: Dict[str, SceneConfig] = self._initialize_scene_configs()
        self.logger = logger
    
    def _initialize_scene_configs(self) -> Dict[str, SceneConfig]:
        """初始化场景配置"""
        configs = {}
        
        # 考研自习室场景
        configs['考研自习室'] = SceneConfig(
            scene_name='考研自习室',
            display_name='考研自习室',
            description='为准备考研的同学提供学习伙伴匹配',
            match_weights={
                'personality': 0.25,
                'interest': 0.35,
                'scene': 0.30,
                'emotion': 0.10
            },
            topic_templates=[
                '你的目标院校是哪里？',
                '你每天的学习时间安排是怎样的？',
                '有什么好的学习方法可以分享吗？'
            ]
        )
        
        # 职业咨询室场景
        configs['职业咨询室'] = SceneConfig(
            scene_name='职业咨询室',
            display_name='职业咨询室',
            description='为职业规划和求职提供交流平台',
            match_weights={
                'personality': 0.20,
                'interest': 0.40,
                'scene': 0.30,
                'emotion': 0.10
            },
            topic_templates=[
                '你对哪个行业感兴趣？',
                '你有什么职业规划？',
                '你参加过哪些实习或项目？'
            ]
        )
        
        # 心理树洞场景
        configs['心理树洞'] = SceneConfig(
            scene_name='心理树洞',
            display_name='心理树洞',
            description='提供情感支持和心理倾诉空间',
            match_weights={
                'personality': 0.30,
                'interest': 0.10,
                'scene': 0.20,
                'emotion': 0.40
            },
            topic_templates=[
                '最近有什么让你感到困扰的事情吗？',
                '你通常如何缓解压力？',
                '有什么让你感到开心的事情吗？'
            ]
        )
        
        # 兴趣社群场景
        configs['兴趣社群'] = SceneConfig(
            scene_name='兴趣社群',
            display_name='兴趣社群',
            description='基于共同兴趣爱好的社交匹配',
            match_weights={
                'personality': 0.20,
                'interest': 0.50,
                'scene': 0.20,
                'emotion': 0.10
            },
            topic_templates=[
                '你最喜欢的兴趣爱好是什么？',
                '你平时喜欢做什么？',
                '有什么想一起做的活动吗？'
            ]
        )
        
        return configs
    
    def calculate_match_score(
        self,
        user_a_id: str,
        user_b_id: str,
        scene: str
    ) -> float:
        """
        计算两个用户之间的匹配度
        
        Args:
            user_a_id: 用户A的ID
            user_b_id: 用户B的ID
            scene: 匹配场景
            
        Returns:
            float: 匹配度分数 (0-100)
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 获取用户画像
        profile_a = self._user_profile_service.get_profile(user_a_id)
        profile_b = self._user_profile_service.get_profile(user_b_id)
        
        # 获取场景配置
        scene_config = self._scene_configs.get(scene)
        if not scene_config:
            raise ValidationError(f"Invalid scene: {scene}")
        
        # 计算各维度得分
        personality_score = self._calculate_personality_score(profile_a, profile_b)
        interest_score = self._calculate_interest_score(profile_a, profile_b, scene)
        scene_score = self._calculate_scene_score(profile_a, profile_b, scene)
        emotion_score = self._calculate_emotion_sync_score(profile_a, profile_b)
        
        # 根据场景权重计算总分
        weights = scene_config.match_weights
        total_score = (
            personality_score * weights.get('personality', 0.25) +
            interest_score * weights.get('interest', 0.25) +
            scene_score * weights.get('scene', 0.25) +
            emotion_score * weights.get('emotion', 0.25)
        )
        
        return round(total_score, 2)
    
    def _calculate_personality_score(
        self,
        profile_a: UserProfile,
        profile_b: UserProfile
    ) -> float:
        """
        计算人格匹配得分
        
        Args:
            profile_a: 用户A的画像
            profile_b: 用户B的画像
            
        Returns:
            float: 人格匹配得分 (0-100)
        """
        score = 0.0
        
        # MBTI匹配（40分）
        if profile_a.mbti_type and profile_b.mbti_type:
            mbti_score = self._calculate_mbti_compatibility(
                profile_a.mbti_type,
                profile_b.mbti_type
            )
            score += mbti_score * 40
        
        # 大五人格匹配（60分）
        if profile_a.big_five and profile_b.big_five:
            big_five_score = self._calculate_big_five_compatibility(
                profile_a.big_five,
                profile_b.big_five
            )
            score += big_five_score * 60
        
        return min(score, 100.0)
    
    def _calculate_mbti_compatibility(self, mbti_a: str, mbti_b: str) -> float:
        """
        计算MBTI兼容性
        
        Args:
            mbti_a: 用户A的MBTI类型
            mbti_b: 用户B的MBTI类型
            
        Returns:
            float: 兼容性得分 (0-1)
        """
        if not mbti_a or not mbti_b or len(mbti_a) != 4 or len(mbti_b) != 4:
            return 0.5
        
        # 计算相同维度的数量
        same_dimensions = sum(1 for i in range(4) if mbti_a[i] == mbti_b[i])
        
        # 某些维度的互补性更好（如E/I）
        # 简化版本：2-3个维度相同为最佳
        if same_dimensions == 2 or same_dimensions == 3:
            return 0.9
        elif same_dimensions == 4:
            return 0.8  # 完全相同可能缺乏互补
        elif same_dimensions == 1:
            return 0.6
        else:
            return 0.4
    
    def _calculate_big_five_compatibility(self, big_five_a, big_five_b) -> float:
        """
        计算大五人格兼容性
        
        Args:
            big_five_a: 用户A的大五人格得分
            big_five_b: 用户B的大五人格得分
            
        Returns:
            float: 兼容性得分 (0-1)
        """
        # 计算各维度的相似度
        dimensions = [
            'neuroticism',
            'agreeableness',
            'extraversion',
            'openness',
            'conscientiousness'
        ]
        
        similarities = []
        for dim in dimensions:
            score_a = getattr(big_five_a, dim)
            score_b = getattr(big_five_b, dim)
            # 使用余弦相似度的简化版本
            similarity = 1.0 - abs(score_a - score_b)
            similarities.append(similarity)
        
        # 某些维度更重要（如宜人性、外向性）
        weights = [0.15, 0.25, 0.25, 0.15, 0.20]
        weighted_similarity = sum(s * w for s, w in zip(similarities, weights))
        
        return weighted_similarity
    
    def _calculate_interest_score(
        self,
        profile_a: UserProfile,
        profile_b: UserProfile,
        scene: str
    ) -> float:
        """
        计算兴趣匹配得分
        
        Args:
            profile_a: 用户A的画像
            profile_b: 用户B的画像
            scene: 匹配场景
            
        Returns:
            float: 兴趣匹配得分 (0-100)
        """
        # 根据场景选择相关的兴趣类型
        if scene == '考研自习室':
            interests_a = set(profile_a.academic_interests)
            interests_b = set(profile_b.academic_interests)
        elif scene == '职业咨询室':
            interests_a = set(profile_a.career_interests)
            interests_b = set(profile_b.career_interests)
        else:
            # 兴趣社群和心理树洞使用所有兴趣
            interests_a = set(
                profile_a.academic_interests +
                profile_a.career_interests +
                profile_a.hobby_interests
            )
            interests_b = set(
                profile_b.academic_interests +
                profile_b.career_interests +
                profile_b.hobby_interests
            )
        
        if not interests_a or not interests_b:
            return 50.0  # 默认中等分数
        
        # 计算Jaccard相似度
        intersection = len(interests_a & interests_b)
        union = len(interests_a | interests_b)
        
        if union == 0:
            return 50.0
        
        jaccard_similarity = intersection / union
        
        # 转换为0-100分
        score = jaccard_similarity * 100
        
        return round(score, 2)
    
    def _calculate_scene_score(
        self,
        profile_a: UserProfile,
        profile_b: UserProfile,
        scene: str
    ) -> float:
        """
        计算场景匹配得分
        
        Args:
            profile_a: 用户A的画像
            profile_b: 用户B的画像
            scene: 匹配场景
            
        Returns:
            float: 场景匹配得分 (0-100)
        """
        # 检查双方是否都关注该场景
        scene_in_a = scene in profile_a.current_scenes
        scene_in_b = scene in profile_b.current_scenes
        
        if not scene_in_a or not scene_in_b:
            return 30.0  # 如果有一方不关注该场景，给较低分
        
        # 获取场景优先级
        priority_a = profile_a.scene_priorities.get(scene, 0.0)
        priority_b = profile_b.scene_priorities.get(scene, 0.0)
        
        # 优先级越高，匹配度越高
        avg_priority = (priority_a + priority_b) / 2.0
        
        # 转换为0-100分
        score = 50.0 + avg_priority * 50.0
        
        return round(score, 2)
    
    def _calculate_emotion_sync_score(
        self,
        profile_a: UserProfile,
        profile_b: UserProfile
    ) -> float:
        """
        计算情感同步性得分
        
        Args:
            profile_a: 用户A的画像
            profile_b: 用户B的画像
            
        Returns:
            float: 情感同步性得分 (0-100)
        """
        # 情绪稳定性相似度
        emotion_stability_diff = abs(
            profile_a.emotion_stability - profile_b.emotion_stability
        )
        emotion_similarity = 1.0 - emotion_stability_diff
        
        # 社交能量相似度
        social_energy_diff = abs(
            profile_a.social_energy - profile_b.social_energy
        )
        social_similarity = 1.0 - social_energy_diff
        
        # 综合得分
        score = (emotion_similarity * 0.5 + social_similarity * 0.5) * 100
        
        return round(score, 2)
    
    def find_matches(
        self,
        user_id: str,
        scene: str,
        limit: int = 10
    ) -> List[Match]:
        """
        为用户查找匹配对象
        
        Args:
            user_id: 用户ID
            scene: 匹配场景
            limit: 返回结果数量限制
            
        Returns:
            List[Match]: 匹配结果列表，按匹配度排序
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 获取所有用户（实际应该从数据库查询）
        all_user_ids = self._get_all_user_ids()
        
        # 排除自己
        candidate_ids = [uid for uid in all_user_ids if uid != user_id]
        
        if not candidate_ids:
            return []
        
        # 计算与每个候选用户的匹配度
        matches = []
        for candidate_id in candidate_ids:
            try:
                match = self._create_match(user_id, candidate_id, scene)
                matches.append(match)
            except Exception as e:
                self.logger.warning(
                    f"Failed to create match between {user_id} and {candidate_id}: {e}"
                )
                continue
        
        # 按匹配度排序并限制数量
        sorted_matches = self._sort_and_limit_matches(matches, limit)
        
        # 保存匹配记录
        for match in sorted_matches:
            self._matches[match.match_id] = match
        
        return sorted_matches
    
    def _create_match(
        self,
        user_a_id: str,
        user_b_id: str,
        scene: str
    ) -> Match:
        """
        创建匹配记录
        
        Args:
            user_a_id: 用户A的ID
            user_b_id: 用户B的ID
            scene: 匹配场景
            
        Returns:
            Match: 匹配记录
        """
        # 获取用户画像
        profile_a = self._user_profile_service.get_profile(user_a_id)
        profile_b = self._user_profile_service.get_profile(user_b_id)
        
        # 计算各维度得分
        personality_score = self._calculate_personality_score(profile_a, profile_b)
        interest_score = self._calculate_interest_score(profile_a, profile_b, scene)
        scene_score = self._calculate_scene_score(profile_a, profile_b, scene)
        emotion_score = self._calculate_emotion_sync_score(profile_a, profile_b)
        
        # 计算总分
        total_score = self.calculate_match_score(user_a_id, user_b_id, scene)
        
        # 生成匹配理由
        match_reason = self.get_match_reason(user_a_id, user_b_id, scene)
        
        # 创建匹配记录
        match = Match(
            match_id=str(uuid.uuid4()),
            user_a_id=user_a_id,
            user_b_id=user_b_id,
            scene=scene,
            match_score=total_score,
            match_reason=match_reason,
            personality_score=personality_score,
            interest_score=interest_score,
            scene_score=scene_score,
            emotion_sync_score=emotion_score,
            status='pending',
            created_at=datetime.now()
        )
        
        return match
    
    def _sort_and_limit_matches(
        self,
        matches: List[Match],
        limit: int
    ) -> List[Match]:
        """
        对匹配结果排序并限制数量
        
        Args:
            matches: 匹配结果列表
            limit: 数量限制
            
        Returns:
            List[Match]: 排序后的匹配结果
        """
        # 按匹配度从高到低排序
        sorted_matches = sorted(
            matches,
            key=lambda m: m.match_score,
            reverse=True
        )
        
        # 限制数量
        return sorted_matches[:limit]
    
    def get_match_reason(
        self,
        user_a_id: str,
        user_b_id: str,
        scene: str = None
    ) -> str:
        """
        生成匹配理由
        
        Args:
            user_a_id: 用户A的ID
            user_b_id: 用户B的ID
            scene: 匹配场景（可选）
            
        Returns:
            str: 匹配理由
        """
        if not self._user_profile_service:
            return "系统推荐"
        
        try:
            profile_a = self._user_profile_service.get_profile(user_a_id)
            profile_b = self._user_profile_service.get_profile(user_b_id)
        except NotFoundError:
            return "系统推荐"
        
        reasons = []
        
        # MBTI匹配理由
        if profile_a.mbti_type and profile_b.mbti_type:
            if profile_a.mbti_type == profile_b.mbti_type:
                reasons.append(f"你们都是{profile_a.mbti_type}人格类型")
            else:
                same_count = sum(
                    1 for i in range(4)
                    if profile_a.mbti_type[i] == profile_b.mbti_type[i]
                )
                if same_count >= 2:
                    reasons.append("你们的性格特质有很多相似之处")
        
        # 兴趣匹配理由
        if scene == '考研自习室':
            common_interests = set(profile_a.academic_interests) & set(
                profile_b.academic_interests
            )
            if common_interests:
                interests_str = "、".join(list(common_interests)[:2])
                reasons.append(f"你们都在准备{interests_str}")
        elif scene == '职业咨询室':
            common_interests = set(profile_a.career_interests) & set(
                profile_b.career_interests
            )
            if common_interests:
                interests_str = "、".join(list(common_interests)[:2])
                reasons.append(f"你们都对{interests_str}感兴趣")
        else:
            all_interests_a = set(
                profile_a.academic_interests +
                profile_a.career_interests +
                profile_a.hobby_interests
            )
            all_interests_b = set(
                profile_b.academic_interests +
                profile_b.career_interests +
                profile_b.hobby_interests
            )
            common_interests = all_interests_a & all_interests_b
            if common_interests:
                interests_str = "、".join(list(common_interests)[:2])
                reasons.append(f"你们都喜欢{interests_str}")
        
        # 场景匹配理由
        if scene and scene in profile_a.current_scenes and scene in profile_b.current_scenes:
            reasons.append(f"你们都关注{scene}场景")
        
        # 情感特征匹配理由
        emotion_diff = abs(profile_a.emotion_stability - profile_b.emotion_stability)
        if emotion_diff < 0.2:
            reasons.append("你们的情绪特征相似")
        
        if not reasons:
            reasons.append("系统综合评估推荐")
        
        return "，".join(reasons)
    
    def update_match_weights(self, scene: str, weights: Dict[str, float]) -> None:
        """
        更新场景的匹配权重
        
        Args:
            scene: 场景名称
            weights: 新的权重配置
        """
        if scene not in self._scene_configs:
            raise ValidationError(f"Invalid scene: {scene}")
        
        # 验证权重总和
        if abs(sum(weights.values()) - 1.0) > 0.01:
            raise ValidationError("Weights must sum to 1.0")
        
        self._scene_configs[scene].match_weights = weights
        self.logger.info(f"Updated match weights for scene: {scene}")
    
    def get_scene_config(self, scene: str) -> SceneConfig:
        """
        获取场景配置
        
        Args:
            scene: 场景名称
            
        Returns:
            SceneConfig: 场景配置
        """
        if scene not in self._scene_configs:
            raise ValidationError(f"Invalid scene: {scene}")
        return self._scene_configs[scene]
    
    def _get_all_user_ids(self) -> List[str]:
        """
        获取所有用户ID
        
        Returns:
            List[str]: 用户ID列表
        """
        if not self._user_profile_service:
            return []
        
        # 从用户画像服务获取所有用户ID
        # 这里假设服务有一个内部的用户存储
        if hasattr(self._user_profile_service, '_profiles'):
            return list(self._user_profile_service._profiles.keys())
        
        return []
    
    def get_match(self, match_id: str) -> Match:
        """
        获取匹配记录
        
        Args:
            match_id: 匹配记录ID
            
        Returns:
            Match: 匹配记录
        """
        if match_id not in self._matches:
            raise NotFoundError(f"Match not found: {match_id}")
        return self._matches[match_id]
    
    def create_match_result(
        self,
        match: Match,
        requesting_user_id: str
    ) -> MatchResult:
        """
        创建匹配结果（包含对方的详细信息）
        
        Args:
            match: 匹配记录
            requesting_user_id: 请求用户的ID
            
        Returns:
            MatchResult: 匹配结果
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 确定对方的ID
        other_user_id = (
            match.user_b_id if match.user_a_id == requesting_user_id
            else match.user_a_id
        )
        
        # 获取对方的用户信息和画像
        other_user = self._user_profile_service.get_user(other_user_id)
        other_profile = self._user_profile_service.get_profile(other_user_id)
        
        # 构建返回信息
        user_info = {
            'user_id': other_user.user_id,
            'username': other_user.username,
            'school': other_user.school,
            'major': other_user.major,
            'grade': other_user.grade
        }
        
        personality_traits = {
            'mbti_type': other_profile.mbti_type,
            'big_five': other_profile.big_five.dict() if other_profile.big_five else None
        }
        
        interest_tags = {
            'academic_interests': other_profile.academic_interests,
            'career_interests': other_profile.career_interests,
            'hobby_interests': other_profile.hobby_interests
        }
        
        scene_needs = other_profile.current_scenes
        
        return MatchResult(
            match=match,
            user_info=user_info,
            personality_traits=personality_traits,
            interest_tags=interest_tags,
            scene_needs=scene_needs
        )

    def get_match_history(self, user_id: str, limit: int = 20) -> List[Match]:
        """
        获取用户的匹配历史
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            List[Match]: 匹配记录列表
        """
        user_matches = [
            match for match in self._matches.values()
            if match.user_a_id == user_id or match.user_b_id == user_id
        ]
        
        # 按创建时间倒序排序
        user_matches.sort(key=lambda x: x.created_at, reverse=True)
        
        return user_matches[:limit]
    
    def accept_match(self, match_id: str, user_id: str) -> Match:
        """
        接受匹配
        
        Args:
            match_id: 匹配ID
            user_id: 用户ID
            
        Returns:
            Match: 更新后的匹配记录
        """
        if match_id not in self._matches:
            raise NotFoundError(f"Match not found: {match_id}")
        
        match = self._matches[match_id]
        
        # 验证用户权限
        if user_id not in [match.user_a_id, match.user_b_id]:
            raise ValidationError("User not authorized to accept this match")
        
        # 更新状态
        match.status = "accepted"
        
        self.logger.info(f"Match {match_id} accepted by user {user_id}")
        
        return match
    
    def reject_match(self, match_id: str, user_id: str) -> Match:
        """
        拒绝匹配
        
        Args:
            match_id: 匹配ID
            user_id: 用户ID
            
        Returns:
            Match: 更新后的匹配记录
        """
        if match_id not in self._matches:
            raise NotFoundError(f"Match not found: {match_id}")
        
        match = self._matches[match_id]
        
        # 验证用户权限
        if user_id not in [match.user_a_id, match.user_b_id]:
            raise ValidationError("User not authorized to reject this match")
        
        # 更新状态
        match.status = "rejected"
        
        self.logger.info(f"Match {match_id} rejected by user {user_id}")
        
        return match

"""用户画像动态更新服务"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from src.models.conversation import Message
from src.models.user import BigFiveScores
from src.utils.logger import get_logger
from src.utils.exceptions import NotFoundError, ValidationError

logger = get_logger(__name__)


class ProfileUpdateService:
    """用户画像动态更新服务类"""
    
    # 情绪关键词映射
    EMOTION_KEYWORDS = {
        'positive': ['开心', '高兴', '快乐', '兴奋', '满意', '喜欢', '爱', '棒', '好', '赞'],
        'negative': ['难过', '伤心', '失望', '沮丧', '痛苦', '讨厌', '恨', '糟糕', '差'],
        'anxious': ['焦虑', '紧张', '担心', '害怕', '恐惧', '不安', '压力', '烦躁'],
        'neutral': ['还行', '一般', '普通', '平常', '正常']
    }
    
    # 兴趣话题关键词
    INTEREST_KEYWORDS = {
        'academic': ['学习', '考研', '考试', '课程', '论文', '研究', '实验', '作业', '复习'],
        'career': ['工作', '实习', '求职', '面试', '简历', '职业', '公司', '行业', '岗位'],
        'hobby': ['电影', '音乐', '运动', '游戏', '旅游', '摄影', '绘画', '阅读', '书']
    }
    
    # 画像更新阈值
    UPDATE_THRESHOLD = 0.15  # 画像变化超过15%时通知用户
    
    def __init__(self, user_profile_service=None, matching_service=None):
        """
        初始化服务
        
        Args:
            user_profile_service: 用户画像服务实例
            matching_service: 匹配服务实例
        """
        self._user_profile_service = user_profile_service
        self._matching_service = matching_service
        self._profile_snapshots: Dict[str, Dict] = {}  # 用于跟踪画像变化
        self.logger = logger
    
    def analyze_conversation(
        self,
        conversation_id: str,
        messages: List[Message]
    ) -> Dict[str, any]:
        """
        分析对话内容并提取关键信息
        
        Args:
            conversation_id: 对话ID
            messages: 消息列表
            
        Returns:
            Dict: 包含话题、情绪、兴趣等关键信息的字典
        """
        if not messages:
            return {
                'topics': [],
                'emotions': {},
                'interests': [],
                'conversation_id': conversation_id,
                'message_count': 0,
                'analyzed_at': datetime.now()
            }
        
        # 提取话题
        topics = self._extract_topics(messages)
        
        # 分析情绪
        emotions = self._analyze_emotions(messages)
        
        # 提取兴趣
        interests = self._extract_interests(messages)
        
        analysis_result = {
            'conversation_id': conversation_id,
            'topics': topics,
            'emotions': emotions,
            'interests': interests,
            'message_count': len(messages),
            'analyzed_at': datetime.now()
        }
        
        self.logger.info(
            f"Analyzed conversation {conversation_id}: "
            f"{len(topics)} topics, {len(interests)} interests"
        )
        
        return analysis_result
    
    def _extract_topics(self, messages: List[Message]) -> List[str]:
        """
        从消息中提取话题
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 话题列表
        """
        topics = set()
        
        for message in messages:
            content = message.content.lower()
            
            # 简化的话题提取：查找关键词
            for category, keywords in self.INTEREST_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in content:
                        topics.add(keyword)
        
        return list(topics)
    
    def _analyze_emotions(self, messages: List[Message]) -> Dict[str, Dict]:
        """
        分析消息中的情绪
        
        Args:
            messages: 消息列表
            
        Returns:
            Dict: 每个用户的情绪统计
        """
        user_emotions = {}
        
        for message in messages:
            user_id = message.sender_id
            if user_id not in user_emotions:
                user_emotions[user_id] = {
                    'positive': 0,
                    'negative': 0,
                    'anxious': 0,
                    'neutral': 0,
                    'total': 0
                }
            
            # 检测情绪关键词
            content = message.content.lower()
            emotion_detected = False
            
            for emotion_type, keywords in self.EMOTION_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in content:
                        user_emotions[user_id][emotion_type] += 1
                        emotion_detected = True
                        break
                if emotion_detected:
                    break
            
            if not emotion_detected:
                user_emotions[user_id]['neutral'] += 1
            
            user_emotions[user_id]['total'] += 1
        
        # 计算情绪比例
        for user_id in user_emotions:
            total = user_emotions[user_id]['total']
            if total > 0:
                for emotion_type in ['positive', 'negative', 'anxious', 'neutral']:
                    count = user_emotions[user_id][emotion_type]
                    user_emotions[user_id][f'{emotion_type}_ratio'] = count / total
        
        return user_emotions
    
    def _extract_interests(self, messages: List[Message]) -> List[str]:
        """
        从消息中提取兴趣标签
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 兴趣标签列表
        """
        interests = set()
        
        for message in messages:
            content = message.content.lower()
            
            # 提取兴趣关键词
            for category, keywords in self.INTEREST_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in content:
                        interests.add(keyword)
        
        return list(interests)
    
    def update_profile_from_conversation(
        self,
        user_id: str,
        conversation_data: Dict
    ) -> Dict[str, any]:
        """
        根据对话数据更新用户画像
        
        Args:
            user_id: 用户ID
            conversation_data: 对话分析数据
            
        Returns:
            Dict: 更新结果，包含是否触发通知等信息
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        # 保存画像快照用于比较
        profile = self._user_profile_service.get_profile(user_id)
        snapshot = self._create_profile_snapshot(profile)
        
        # 更新兴趣标签
        interests_updated = self._update_interests_from_data(user_id, conversation_data)
        
        # 更新情感特征
        emotions_updated = self._update_emotional_features(user_id, conversation_data)
        
        # 计算画像变化程度
        updated_profile = self._user_profile_service.get_profile(user_id)
        change_magnitude = self._calculate_profile_change(snapshot, updated_profile)
        
        # 判断是否需要通知用户
        should_notify = change_magnitude >= self.UPDATE_THRESHOLD
        
        # 如果画像有显著变化，触发匹配度重新计算
        match_recalculated = False
        if should_notify and self._matching_service:
            self._trigger_match_recalculation(user_id)
            match_recalculated = True
        
        result = {
            'user_id': user_id,
            'interests_updated': interests_updated,
            'emotions_updated': emotions_updated,
            'change_magnitude': change_magnitude,
            'should_notify': should_notify,
            'match_recalculated': match_recalculated,
            'updated_at': datetime.now()
        }
        
        self.logger.info(
            f"Updated profile for user {user_id}: "
            f"change={change_magnitude:.2%}, notify={should_notify}"
        )
        
        return result
    
    def _create_profile_snapshot(self, profile) -> Dict:
        """
        创建画像快照用于比较
        
        Args:
            profile: 用户画像
            
        Returns:
            Dict: 画像快照
        """
        return {
            'emotion_stability': profile.emotion_stability,
            'social_energy': profile.social_energy,
            'interest_count': len(
                profile.academic_interests +
                profile.career_interests +
                profile.hobby_interests
            ),
            'big_five': profile.big_five.dict() if profile.big_five else None
        }
    
    def _update_interests_from_data(
        self,
        user_id: str,
        conversation_data: Dict
    ) -> bool:
        """
        根据对话数据更新兴趣标签
        
        Args:
            user_id: 用户ID
            conversation_data: 对话数据
            
        Returns:
            bool: 是否有更新
        """
        extracted_interests = conversation_data.get('interests', [])
        if not extracted_interests:
            return False
        
        profile = self._user_profile_service.get_profile(user_id)
        
        # 分类兴趣
        academic_interests = set(profile.academic_interests)
        career_interests = set(profile.career_interests)
        hobby_interests = set(profile.hobby_interests)
        
        updated = False
        for interest in extracted_interests:
            # 根据关键词分类
            if interest in self.INTEREST_KEYWORDS['academic']:
                if interest not in academic_interests:
                    academic_interests.add(interest)
                    updated = True
            elif interest in self.INTEREST_KEYWORDS['career']:
                if interest not in career_interests:
                    career_interests.add(interest)
                    updated = True
            else:
                if interest not in hobby_interests:
                    hobby_interests.add(interest)
                    updated = True
        
        if updated:
            self._user_profile_service.update_profile(user_id, {
                'academic_interests': list(academic_interests),
                'career_interests': list(career_interests),
                'hobby_interests': list(hobby_interests)
            })
        
        return updated
    
    def _update_emotional_features(
        self,
        user_id: str,
        conversation_data: Dict
    ) -> bool:
        """
        根据对话数据更新情感特征
        
        Args:
            user_id: 用户ID
            conversation_data: 对话数据
            
        Returns:
            bool: 是否有更新
        """
        emotions = conversation_data.get('emotions', {})
        user_emotions = emotions.get(user_id)
        
        if not user_emotions:
            return False
        
        profile = self._user_profile_service.get_profile(user_id)
        
        # 计算情绪稳定性（负面和焦虑情绪越少，稳定性越高）
        negative_ratio = user_emotions.get('negative_ratio', 0)
        anxious_ratio = user_emotions.get('anxious_ratio', 0)
        
        # 使用指数移动平均更新情绪稳定性
        alpha = 0.3  # 平滑系数
        new_instability = (negative_ratio + anxious_ratio) / 2
        new_stability = 1.0 - new_instability
        
        updated_stability = (
            alpha * new_stability +
            (1 - alpha) * profile.emotion_stability
        )
        
        # 计算社交能量（积极情绪越多，社交能量越高）
        positive_ratio = user_emotions.get('positive_ratio', 0)
        new_energy = positive_ratio
        
        updated_energy = (
            alpha * new_energy +
            (1 - alpha) * profile.social_energy
        )
        
        # 更新画像
        self._user_profile_service.update_profile(user_id, {
            'emotion_stability': round(updated_stability, 3),
            'social_energy': round(updated_energy, 3)
        })
        
        return True
    
    def _calculate_profile_change(
        self,
        snapshot: Dict,
        updated_profile
    ) -> float:
        """
        计算画像变化程度
        
        Args:
            snapshot: 画像快照
            updated_profile: 更新后的画像
            
        Returns:
            float: 变化程度 (0-1)
        """
        changes = []
        
        # 情绪稳定性变化
        emotion_change = abs(
            snapshot['emotion_stability'] - updated_profile.emotion_stability
        )
        changes.append(emotion_change)
        
        # 社交能量变化
        energy_change = abs(
            snapshot['social_energy'] - updated_profile.social_energy
        )
        changes.append(energy_change)
        
        # 兴趣数量变化
        current_interest_count = len(
            updated_profile.academic_interests +
            updated_profile.career_interests +
            updated_profile.hobby_interests
        )
        interest_change = abs(
            snapshot['interest_count'] - current_interest_count
        ) / max(snapshot['interest_count'], 1)
        changes.append(interest_change)
        
        # 大五人格变化
        if snapshot['big_five'] and updated_profile.big_five:
            big_five_change = self._calculate_big_five_change(
                snapshot['big_five'],
                updated_profile.big_five.dict()
            )
            changes.append(big_five_change)
        
        # 返回平均变化
        return sum(changes) / len(changes) if changes else 0.0
    
    def _calculate_big_five_change(
        self,
        old_scores: Dict,
        new_scores: Dict
    ) -> float:
        """
        计算大五人格变化
        
        Args:
            old_scores: 旧的大五人格得分
            new_scores: 新的大五人格得分
            
        Returns:
            float: 变化程度
        """
        dimensions = [
            'neuroticism',
            'agreeableness',
            'extraversion',
            'openness',
            'conscientiousness'
        ]
        
        changes = []
        for dim in dimensions:
            change = abs(old_scores[dim] - new_scores[dim])
            changes.append(change)
        
        return sum(changes) / len(changes)
    
    def _trigger_match_recalculation(self, user_id: str) -> None:
        """
        触发匹配度重新计算
        
        Args:
            user_id: 用户ID
        """
        if not self._matching_service:
            self.logger.warning("Matching service not initialized")
            return
        
        # 获取用户当前关注的场景
        profile = self._user_profile_service.get_profile(user_id)
        
        # 为每个场景重新计算匹配
        for scene in profile.current_scenes:
            try:
                # 重新查找匹配
                matches = self._matching_service.find_matches(
                    user_id=user_id,
                    scene=scene,
                    limit=10
                )
                self.logger.info(
                    f"Recalculated {len(matches)} matches for user {user_id} "
                    f"in scene {scene}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to recalculate matches for user {user_id}: {e}"
                )
    
    def update_personality_from_behavior(
        self,
        user_id: str,
        behavior_data: Dict[str, float]
    ) -> BigFiveScores:
        """
        根据用户行为模式动态调整人格特质评分
        
        Args:
            user_id: 用户ID
            behavior_data: 行为数据字典，包含各种行为指标
            
        Returns:
            BigFiveScores: 更新后的人格得分
        """
        if not self._user_profile_service:
            raise ValidationError("User profile service not initialized")
        
        profile = self._user_profile_service.get_profile(user_id)
        
        if not profile.big_five:
            # 如果还没有人格得分，先设置默认值
            profile.big_five = BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
        
        # 使用行为数据调整人格得分
        current_scores = profile.big_five.dict()
        updated_scores = self._adjust_personality_scores(current_scores, behavior_data)
        
        # 创建新的BigFiveScores对象
        new_big_five = BigFiveScores(**updated_scores)
        
        # 更新画像
        self._user_profile_service.update_profile(user_id, {'big_five': new_big_five})
        
        self.logger.info(f"Updated personality from behavior for user {user_id}")
        
        return new_big_five
    
    def _adjust_personality_scores(
        self,
        current_scores: Dict[str, float],
        behavior_data: Dict[str, float]
    ) -> Dict[str, float]:
        """
        根据行为数据调整人格得分
        
        Args:
            current_scores: 当前人格得分
            behavior_data: 行为数据
            
        Returns:
            Dict: 调整后的人格得分
        """
        alpha = 0.2  # 调整系数，避免变化过大
        
        updated_scores = current_scores.copy()
        
        # 根据不同行为指标调整不同维度
        
        # 神经质：根据情绪波动调整
        if 'emotion_volatility' in behavior_data:
            volatility = behavior_data['emotion_volatility']
            updated_scores['neuroticism'] = (
                (1 - alpha) * current_scores['neuroticism'] +
                alpha * volatility
            )
        
        # 宜人性：根据互动友好度调整
        if 'interaction_friendliness' in behavior_data:
            friendliness = behavior_data['interaction_friendliness']
            updated_scores['agreeableness'] = (
                (1 - alpha) * current_scores['agreeableness'] +
                alpha * friendliness
            )
        
        # 外向性：根据社交活跃度调整
        if 'social_activity' in behavior_data:
            activity = behavior_data['social_activity']
            updated_scores['extraversion'] = (
                (1 - alpha) * current_scores['extraversion'] +
                alpha * activity
            )
        
        # 开放性：根据话题多样性调整
        if 'topic_diversity' in behavior_data:
            diversity = behavior_data['topic_diversity']
            updated_scores['openness'] = (
                (1 - alpha) * current_scores['openness'] +
                alpha * diversity
            )
        
        # 尽责性：根据回复及时性调整
        if 'response_timeliness' in behavior_data:
            timeliness = behavior_data['response_timeliness']
            updated_scores['conscientiousness'] = (
                (1 - alpha) * current_scores['conscientiousness'] +
                alpha * timeliness
            )
        
        # 确保所有得分在0-1范围内
        for key in updated_scores:
            updated_scores[key] = max(0.0, min(1.0, updated_scores[key]))
        
        return updated_scores
    
    def generate_profile_update_notification(
        self,
        user_id: str,
        update_result: Dict
    ) -> Dict[str, any]:
        """
        生成画像更新通知
        
        Args:
            user_id: 用户ID
            update_result: 更新结果
            
        Returns:
            Dict: 通知内容
        """
        if not update_result.get('should_notify'):
            return None
        
        profile = self._user_profile_service.get_profile(user_id)
        
        notification = {
            'user_id': user_id,
            'title': '您的画像已更新',
            'message': self._generate_notification_message(update_result, profile),
            'change_magnitude': update_result['change_magnitude'],
            'updated_at': update_result['updated_at'],
            'action': {
                'type': 'view_profile',
                'label': '查看更新后的画像'
            }
        }
        
        return notification
    
    def _generate_notification_message(
        self,
        update_result: Dict,
        profile
    ) -> str:
        """
        生成通知消息
        
        Args:
            update_result: 更新结果
            profile: 用户画像
            
        Returns:
            str: 通知消息
        """
        messages = []
        
        if update_result.get('interests_updated'):
            interest_count = len(
                profile.academic_interests +
                profile.career_interests +
                profile.hobby_interests
            )
            messages.append(f"发现了您的新兴趣，当前共有{interest_count}个兴趣标签")
        
        if update_result.get('emotions_updated'):
            messages.append(
                f"您的情感特征已更新（情绪稳定性：{profile.emotion_stability:.1%}）"
            )
        
        if update_result.get('match_recalculated'):
            messages.append("已为您重新匹配更合适的成长伙伴")
        
        if not messages:
            messages.append("您的画像已根据最近的对话进行了优化")
        
        return "，".join(messages) + "。"

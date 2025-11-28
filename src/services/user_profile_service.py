"""用户画像服务"""
import uuid
import hashlib
from datetime import datetime
from typing import Optional, List, Dict
from src.models.user import (
    User, UserProfile, BigFiveScores,
    UserRegistrationRequest, MBTITestRequest, BigFiveTestRequest,
    InterestSelectionRequest, SceneSelectionRequest
)
from src.utils.exceptions import ValidationError, NotFoundError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserProfileService:
    """用户画像服务类"""
    
    def __init__(self, personality_service=None):
        """
        初始化服务
        
        Args:
            personality_service: 人格识别服务实例（可选，用于依赖注入）
        """
        # 临时存储，实际应使用数据库
        self._users: Dict[str, User] = {}
        self._profiles: Dict[str, UserProfile] = {}
        self._personality_service = personality_service
        self.logger = logger
    
    def create_profile(self, user_id: str, basic_info: dict) -> UserProfile:
        """
        创建用户画像
        
        Args:
            user_id: 用户ID
            basic_info: 基本信息字典
            
        Returns:
            UserProfile: 创建的用户画像
        """
        profile = UserProfile(
            user_id=user_id,
            updated_at=datetime.now()
        )
        self._profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, updates: dict) -> UserProfile:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            updates: 更新内容字典
            
        Returns:
            UserProfile: 更新后的用户画像
        """
        if user_id not in self._profiles:
            raise NotFoundError(f"Profile not found for user: {user_id}")
        
        profile = self._profiles[user_id]
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now()
        
        return profile
    
    def get_profile(self, user_id: str) -> UserProfile:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserProfile: 用户画像
        """
        if user_id not in self._profiles:
            raise NotFoundError(f"Profile not found for user: {user_id}")
        return self._profiles[user_id]
    
    def register_user(self, request: UserRegistrationRequest) -> User:
        """
        注册新用户
        
        Args:
            request: 用户注册请求
            
        Returns:
            User: 创建的用户对象
        """
        # 检查邮箱是否已存在
        for user in self._users.values():
            if user.email == request.email:
                raise ValidationError("Email already registered")
        
        # 生成用户ID
        user_id = str(uuid.uuid4())
        
        # 创建密码哈希
        password_hash = self._hash_password(request.password)
        
        # 创建用户对象
        user = User(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            school=request.school,
            major=request.major,
            grade=request.grade,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        # 创建初始画像
        profile = self.create_profile(user_id, {})
        user.profile = profile
        
        # 保存用户
        self._users[user_id] = user
        
        return user
    
    def process_mbti_test(self, request: MBTITestRequest) -> str:
        """
        处理MBTI测试并返回类型
        
        Args:
            request: MBTI测试请求
            
        Returns:
            str: MBTI类型
        """
        if request.user_id not in self._users:
            raise NotFoundError(f"User not found: {request.user_id}")
        
        # 简化的MBTI计算逻辑
        # 实际应该根据标准MBTI评分规则
        answers = request.answers
        
        # E/I: 外向/内向 (问题1-15)
        ei_score = sum(answers[0:15])
        e_or_i = 'E' if ei_score > 37.5 else 'I'
        
        # S/N: 感觉/直觉 (问题16-30)
        sn_score = sum(answers[15:30])
        s_or_n = 'S' if sn_score > 37.5 else 'N'
        
        # T/F: 思考/情感 (问题31-45)
        tf_score = sum(answers[30:45])
        t_or_f = 'T' if tf_score > 37.5 else 'F'
        
        # J/P: 判断/知觉 (问题46-60)
        jp_score = sum(answers[45:60])
        j_or_p = 'J' if jp_score > 37.5 else 'P'
        
        mbti_type = f"{e_or_i}{s_or_n}{t_or_f}{j_or_p}"
        
        # 更新用户画像
        self.update_profile(request.user_id, {'mbti_type': mbti_type})
        
        return mbti_type
    
    def process_big_five_test(self, request: BigFiveTestRequest) -> BigFiveScores:
        """
        处理大五人格测试并返回得分
        
        Args:
            request: 大五人格测试请求
            
        Returns:
            BigFiveScores: 大五人格得分
        """
        if request.user_id not in self._users:
            raise NotFoundError(f"User not found: {request.user_id}")
        
        # 简化的大五人格计算逻辑
        # 实际应该根据标准大五人格评分规则
        answers = request.answers
        
        # 每个维度10题
        neuroticism = sum(answers[0:10]) / 50.0
        agreeableness = sum(answers[10:20]) / 50.0
        extraversion = sum(answers[20:30]) / 50.0
        openness = sum(answers[30:40]) / 50.0
        conscientiousness = sum(answers[40:50]) / 50.0
        
        scores = BigFiveScores(
            neuroticism=neuroticism,
            agreeableness=agreeableness,
            extraversion=extraversion,
            openness=openness,
            conscientiousness=conscientiousness
        )
        
        # 更新用户画像
        self.update_profile(request.user_id, {'big_five': scores})
        
        return scores
    
    def update_interests(self, request: InterestSelectionRequest) -> UserProfile:
        """
        更新用户兴趣标签
        
        Args:
            request: 兴趣选择请求
            
        Returns:
            UserProfile: 更新后的用户画像
        """
        if request.user_id not in self._users:
            raise NotFoundError(f"User not found: {request.user_id}")
        
        updates = {
            'academic_interests': request.academic_interests,
            'career_interests': request.career_interests,
            'hobby_interests': request.hobby_interests
        }
        
        return self.update_profile(request.user_id, updates)
    
    def update_scenes(self, request: SceneSelectionRequest) -> UserProfile:
        """
        更新用户场景选择
        
        Args:
            request: 场景选择请求
            
        Returns:
            UserProfile: 更新后的用户画像
        """
        if request.user_id not in self._users:
            raise NotFoundError(f"User not found: {request.user_id}")
        
        # 计算场景优先级（均等分配）
        scene_priorities = {scene: 1.0 / len(request.scenes) for scene in request.scenes}
        
        updates = {
            'current_scenes': request.scenes,
            'scene_priorities': scene_priorities
        }
        
        return self.update_profile(request.user_id, updates)
    
    def generate_initial_profile(self, user_id: str) -> UserProfile:
        """
        生成初始用户画像（完成所有设置后）
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserProfile: 完整的用户画像
        """
        if user_id not in self._users:
            raise NotFoundError(f"User not found: {user_id}")
        
        profile = self.get_profile(user_id)
        
        # 验证必要信息是否完整
        if not profile.mbti_type:
            raise ValidationError("MBTI type not set")
        if not profile.big_five:
            raise ValidationError("Big Five scores not set")
        if not profile.current_scenes:
            raise ValidationError("Scenes not selected")
        
        # 生成画像向量（简化版本）
        # 实际应该使用更复杂的向量化算法
        profile_vector = self._generate_profile_vector(profile)
        profile.profile_vector = profile_vector
        profile.updated_at = datetime.now()
        
        return profile
    
    def _hash_password(self, password: str) -> str:
        """
        生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 密码哈希
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_profile_vector(self, profile: UserProfile) -> List[float]:
        """
        生成用户画像向量
        
        Args:
            profile: 用户画像
            
        Returns:
            List[float]: 画像向量
        """
        vector = []
        
        # MBTI编码（4维）
        mbti_encoding = self._encode_mbti(profile.mbti_type)
        vector.extend(mbti_encoding)
        
        # 大五人格（5维）
        if profile.big_five:
            vector.extend([
                profile.big_five.neuroticism,
                profile.big_five.agreeableness,
                profile.big_five.extraversion,
                profile.big_five.openness,
                profile.big_five.conscientiousness
            ])
        else:
            vector.extend([0.5] * 5)
        
        # 情感特征（2维）
        vector.extend([profile.emotion_stability, profile.social_energy])
        
        # 行为特征（2维）
        vector.extend([
            min(profile.response_speed / 100.0, 1.0),  # 归一化
            profile.conversation_depth
        ])
        
        return vector
    
    def _encode_mbti(self, mbti_type: Optional[str]) -> List[float]:
        """
        编码MBTI类型为向量
        
        Args:
            mbti_type: MBTI类型
            
        Returns:
            List[float]: MBTI向量
        """
        if not mbti_type or len(mbti_type) != 4:
            return [0.5, 0.5, 0.5, 0.5]
        
        encoding = []
        encoding.append(1.0 if mbti_type[0] == 'E' else 0.0)  # E/I
        encoding.append(1.0 if mbti_type[1] == 'S' else 0.0)  # S/N
        encoding.append(1.0 if mbti_type[2] == 'T' else 0.0)  # T/F
        encoding.append(1.0 if mbti_type[3] == 'J' else 0.0)  # J/P
        
        return encoding
    
    def get_user(self, user_id: str) -> User:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象
        """
        if user_id not in self._users:
            raise NotFoundError(f"User not found: {user_id}")
        return self._users[user_id]
    
    def authenticate_user(self, email: str, password: str) -> User:
        """
        验证用户凭证
        
        Args:
            email: 用户邮箱
            password: 密码
            
        Returns:
            User: 验证成功的用户对象
            
        Raises:
            NotFoundError: 用户不存在或密码错误
        """
        password_hash = self._hash_password(password)
        
        for user in self._users.values():
            if user.email == email and user.password_hash == password_hash:
                # 更新最后活跃时间
                user.last_active = datetime.now()
                return user
        
        raise NotFoundError("Invalid email or password")
    
    def analyze_personality(self, user_id: str, text_data: List[str]) -> BigFiveScores:
        """
        使用AI模型分析用户人格特质
        
        Args:
            user_id: 用户ID
            text_data: 用户的文本数据列表（对话、评论等）
            
        Returns:
            BigFiveScores: 分析得到的大五人格得分
        """
        if user_id not in self._users:
            raise NotFoundError(f"User not found: {user_id}")
        
        if self._personality_service is None:
            self.logger.warning("Personality service not initialized, using default scores")
            # 如果没有人格识别服务，返回默认得分
            return BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
        
        # 使用人格识别服务分析文本
        scores = self._personality_service.analyze_personality(text_data)
        
        # 更新用户画像
        self.update_profile(user_id, {'big_five': scores})
        
        return scores
    
    def update_interests(self, request: InterestSelectionRequest) -> UserProfile:
        """
        更新用户兴趣标签
        
        Args:
            request: 兴趣选择请求
            
        Returns:
            UserProfile: 更新后的用户画像
        """
        if request.user_id not in self._users:
            raise NotFoundError(f"User not found: {request.user_id}")
        
        updates = {
            'academic_interests': request.academic_interests,
            'career_interests': request.career_interests,
            'hobby_interests': request.hobby_interests
        }
        
        return self.update_profile(request.user_id, updates)
    
    def update_interests_from_conversation(self, user_id: str, conversation_data: Dict) -> None:
        """
        根据对话数据更新用户兴趣标签
        
        Args:
            user_id: 用户ID
            conversation_data: 对话数据字典
        """
        if user_id not in self._users:
            raise NotFoundError(f"User not found: {user_id}")
        
        profile = self.get_profile(user_id)
        
        # 从对话数据中提取兴趣关键词（简化版本）
        # 实际应该使用NLP技术进行更精确的提取
        extracted_interests = conversation_data.get('interests', [])
        
        # 合并新兴趣到现有兴趣
        current_interests = set(profile.hobby_interests)
        current_interests.update(extracted_interests)
        
        # 更新画像
        self.update_profile(user_id, {'hobby_interests': list(current_interests)})
        
        self.logger.info(f"Updated interests for user {user_id}")
    
    def update_personality_from_behavior(self, user_id: str, behavior_data: Dict[str, float]) -> BigFiveScores:
        """
        根据用户行为模式动态调整人格特质评分
        
        Args:
            user_id: 用户ID
            behavior_data: 行为数据字典
            
        Returns:
            BigFiveScores: 更新后的人格得分
        """
        if user_id not in self._users:
            raise NotFoundError(f"User not found: {user_id}")
        
        profile = self.get_profile(user_id)
        
        if not profile.big_five:
            # 如果还没有人格得分，先设置默认值
            profile.big_five = BigFiveScores(
                neuroticism=0.5,
                agreeableness=0.5,
                extraversion=0.5,
                openness=0.5,
                conscientiousness=0.5
            )
        
        if self._personality_service is None:
            self.logger.warning("Personality service not initialized, cannot update from behavior")
            return profile.big_five
        
        # 使用人格识别服务更新得分
        updated_scores = self._personality_service.update_personality_from_behavior(
            profile.big_five,
            behavior_data
        )
        
        # 更新画像
        self.update_profile(user_id, {'big_five': updated_scores})
        
        self.logger.info(f"Updated personality from behavior for user {user_id}")
        
        return updated_scores

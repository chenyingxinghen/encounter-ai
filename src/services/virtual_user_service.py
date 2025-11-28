"""虚拟用户服务"""
import uuid
import random
from datetime import datetime
from typing import List, Dict, Optional
from src.models.virtual_user import (
    VirtualUser, VirtualUserStats, VirtualUserGenerationConfig
)
from src.models.user import UserProfile, BigFiveScores
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VirtualUserService:
    """虚拟用户服务类"""
    
    # MBTI类型对应的人格特征映射
    MBTI_PERSONALITY_MAP = {
        # 分析师型
        'INTJ': {'extraversion': 0.2, 'openness': 0.8, 'conscientiousness': 0.8, 'agreeableness': 0.4, 'neuroticism': 0.3},
        'INTP': {'extraversion': 0.2, 'openness': 0.9, 'conscientiousness': 0.5, 'agreeableness': 0.5, 'neuroticism': 0.4},
        'ENTJ': {'extraversion': 0.8, 'openness': 0.7, 'conscientiousness': 0.9, 'agreeableness': 0.3, 'neuroticism': 0.2},
        'ENTP': {'extraversion': 0.8, 'openness': 0.9, 'conscientiousness': 0.4, 'agreeableness': 0.4, 'neuroticism': 0.3},
        
        # 外交家型
        'INFJ': {'extraversion': 0.3, 'openness': 0.8, 'conscientiousness': 0.7, 'agreeableness': 0.8, 'neuroticism': 0.4},
        'INFP': {'extraversion': 0.2, 'openness': 0.9, 'conscientiousness': 0.5, 'agreeableness': 0.9, 'neuroticism': 0.5},
        'ENFJ': {'extraversion': 0.8, 'openness': 0.7, 'conscientiousness': 0.7, 'agreeableness': 0.9, 'neuroticism': 0.3},
        'ENFP': {'extraversion': 0.9, 'openness': 0.9, 'conscientiousness': 0.4, 'agreeableness': 0.8, 'neuroticism': 0.4},
        
        # 守护者型
        'ISTJ': {'extraversion': 0.2, 'openness': 0.3, 'conscientiousness': 0.9, 'agreeableness': 0.6, 'neuroticism': 0.3},
        'ISFJ': {'extraversion': 0.2, 'openness': 0.3, 'conscientiousness': 0.8, 'agreeableness': 0.9, 'neuroticism': 0.4},
        'ESTJ': {'extraversion': 0.8, 'openness': 0.3, 'conscientiousness': 0.9, 'agreeableness': 0.5, 'neuroticism': 0.2},
        'ESFJ': {'extraversion': 0.9, 'openness': 0.4, 'conscientiousness': 0.8, 'agreeableness': 0.9, 'neuroticism': 0.3},
        
        # 探险家型
        'ISTP': {'extraversion': 0.3, 'openness': 0.7, 'conscientiousness': 0.4, 'agreeableness': 0.4, 'neuroticism': 0.3},
        'ISFP': {'extraversion': 0.3, 'openness': 0.8, 'conscientiousness': 0.4, 'agreeableness': 0.8, 'neuroticism': 0.4},
        'ESTP': {'extraversion': 0.9, 'openness': 0.6, 'conscientiousness': 0.4, 'agreeableness': 0.5, 'neuroticism': 0.2},
        'ESFP': {'extraversion': 0.9, 'openness': 0.7, 'conscientiousness': 0.4, 'agreeableness': 0.8, 'neuroticism': 0.3},
    }
    
    # MBTI类型对应的对话风格
    MBTI_RESPONSE_STYLE_MAP = {
        'INTJ': '简洁理性，注重逻辑和效率',
        'INTP': '深入分析，喜欢探讨理论',
        'ENTJ': '果断直接，善于组织和领导',
        'ENTP': '创新活跃，喜欢辩论和头脑风暴',
        'INFJ': '深刻洞察，关注他人感受',
        'INFP': '温和理想，表达富有诗意',
        'ENFJ': '热情鼓励，善于激励他人',
        'ENFP': '热情开放，充满创意和想象',
        'ISTJ': '务实可靠，注重细节和规则',
        'ISFJ': '温暖体贴，关心他人需求',
        'ESTJ': '高效组织，注重实际结果',
        'ESFJ': '友好热心，善于社交互动',
        'ISTP': '冷静实用，善于解决问题',
        'ISFP': '温和灵活，注重当下体验',
        'ESTP': '活力充沛，喜欢行动和冒险',
        'ESFP': '活泼外向，享受社交和娱乐',
    }
    
    def __init__(self):
        """初始化服务"""
        self._virtual_users: Dict[str, VirtualUser] = {}
        self._virtual_profiles: Dict[str, UserProfile] = {}
        self._real_user_count: int = 0
        self.logger = logger
    
    def initialize_virtual_users(self, config: Optional[VirtualUserGenerationConfig] = None) -> List[VirtualUser]:
        """
        初始化虚拟用户库
        
        Args:
            config: 生成配置，如果为None则使用默认配置
            
        Returns:
            List[VirtualUser]: 生成的虚拟用户列表
        """
        if config is None:
            config = VirtualUserGenerationConfig()
        
        self.logger.info(f"Initializing {config.total_count} virtual users...")
        
        virtual_users = []
        
        # 确保每种MBTI类型至少有一个虚拟用户
        users_per_type = config.total_count // len(config.mbti_types)
        remaining = config.total_count % len(config.mbti_types)
        
        for idx, mbti_type in enumerate(config.mbti_types):
            # 计算该类型应生成的用户数
            count = users_per_type + (1 if idx < remaining else 0)
            
            for i in range(count):
                virtual_user = self._generate_virtual_user(
                    mbti_type=mbti_type,
                    schools=config.schools,
                    majors=config.majors
                )
                virtual_users.append(virtual_user)
                self._virtual_users[virtual_user.user_id] = virtual_user
                
                # 生成对应的用户画像
                profile = self._generate_virtual_profile(virtual_user)
                self._virtual_profiles[virtual_user.user_id] = profile
        
        self.logger.info(f"Successfully initialized {len(virtual_users)} virtual users")
        return virtual_users
    
    def _generate_virtual_user(
        self,
        mbti_type: str,
        schools: List[str],
        majors: List[str]
    ) -> VirtualUser:
        """
        生成单个虚拟用户
        
        Args:
            mbti_type: MBTI类型
            schools: 学校列表
            majors: 专业列表
            
        Returns:
            VirtualUser: 生成的虚拟用户
        """
        user_id = f"virtual_{uuid.uuid4()}"
        username = f"AI伙伴_{mbti_type}_{random.randint(1000, 9999)}"
        
        # 根据MBTI类型设置回复速度范围
        # 外向型(E)回复更快，内向型(I)回复较慢
        if mbti_type[0] == 'E':
            response_speed_range = (5.0, 20.0)
        else:
            response_speed_range = (15.0, 40.0)
        
        # 根据MBTI类型设置消息长度范围
        # 思考型(T)和判断型(J)倾向于更长的消息
        if 'T' in mbti_type or 'J' in mbti_type:
            message_length_range = (50, 200)
        else:
            message_length_range = (30, 150)
        
        virtual_user = VirtualUser(
            user_id=user_id,
            username=username,
            is_virtual=True,
            school=random.choice(schools),
            major=random.choice(majors),
            grade=random.randint(1, 4),
            mbti_type=mbti_type,
            response_style=self.MBTI_RESPONSE_STYLE_MAP[mbti_type],
            response_speed_range=response_speed_range,
            message_length_range=message_length_range,
            match_weight=1.0,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        return virtual_user
    
    def _generate_virtual_profile(self, virtual_user: VirtualUser) -> UserProfile:
        """
        为虚拟用户生成用户画像
        
        Args:
            virtual_user: 虚拟用户对象
            
        Returns:
            UserProfile: 生成的用户画像
        """
        # 根据MBTI类型获取人格特征
        personality_traits = self.MBTI_PERSONALITY_MAP[virtual_user.mbti_type]
        
        # 添加随机波动（±0.1）使虚拟用户更多样化
        big_five = BigFiveScores(
            neuroticism=max(0.0, min(1.0, personality_traits['neuroticism'] + random.uniform(-0.1, 0.1))),
            agreeableness=max(0.0, min(1.0, personality_traits['agreeableness'] + random.uniform(-0.1, 0.1))),
            extraversion=max(0.0, min(1.0, personality_traits['extraversion'] + random.uniform(-0.1, 0.1))),
            openness=max(0.0, min(1.0, personality_traits['openness'] + random.uniform(-0.1, 0.1))),
            conscientiousness=max(0.0, min(1.0, personality_traits['conscientiousness'] + random.uniform(-0.1, 0.1)))
        )
        
        # 生成兴趣标签
        academic_interests = self._generate_interests_for_major(virtual_user.major)
        hobby_interests = self._generate_random_hobbies()
        career_interests = self._generate_career_interests(virtual_user.major)
        
        # 生成场景选择
        current_scenes = random.sample(['考研自习室', '职业咨询室', '心理树洞', '兴趣社群'], k=random.randint(1, 3))
        scene_priorities = {scene: 1.0 / len(current_scenes) for scene in current_scenes}
        
        # 计算情感特征
        emotion_stability = 1.0 - big_five.neuroticism
        social_energy = big_five.extraversion
        
        # 计算行为特征
        avg_response_speed = sum(virtual_user.response_speed_range) / 2
        conversation_depth = (big_five.openness + big_five.conscientiousness) / 2
        
        profile = UserProfile(
            user_id=virtual_user.user_id,
            mbti_type=virtual_user.mbti_type,
            big_five=big_five,
            academic_interests=academic_interests,
            career_interests=career_interests,
            hobby_interests=hobby_interests,
            current_scenes=current_scenes,
            scene_priorities=scene_priorities,
            emotion_stability=emotion_stability,
            social_energy=social_energy,
            response_speed=avg_response_speed,
            conversation_depth=conversation_depth,
            profile_vector=self._generate_profile_vector(big_five, virtual_user.mbti_type),
            updated_at=datetime.now()
        )
        
        return profile
    
    def _generate_interests_for_major(self, major: str) -> List[str]:
        """根据专业生成学业兴趣"""
        interest_map = {
            "计算机科学": ["算法", "数据结构", "操作系统", "计算机网络"],
            "软件工程": ["软件设计", "项目管理", "敏捷开发", "测试"],
            "人工智能": ["机器学习", "深度学习", "自然语言处理", "计算机视觉"],
            "数据科学": ["数据分析", "统计学", "数据挖掘", "可视化"],
            "电子工程": ["电路设计", "信号处理", "嵌入式系统", "通信"],
            "机械工程": ["机械设计", "材料力学", "热力学", "制造工艺"],
            "经济学": ["微观经济", "宏观经济", "计量经济", "金融市场"],
            "金融学": ["投资学", "公司金融", "金融工程", "风险管理"],
            "心理学": ["认知心理学", "发展心理学", "社会心理学", "临床心理学"],
            "教育学": ["教育心理学", "课程设计", "教学方法", "教育技术"],
            "新闻传播": ["新闻写作", "传播理论", "新媒体", "广告学"],
            "外语": ["语言学", "翻译", "文学", "跨文化交际"]
        }
        
        interests = interest_map.get(major, ["通识教育", "学术研究"])
        return random.sample(interests, k=min(3, len(interests)))
    
    def _generate_random_hobbies(self) -> List[str]:
        """生成随机兴趣爱好"""
        hobbies = [
            "阅读", "音乐", "电影", "运动", "旅行", "摄影",
            "绘画", "写作", "游戏", "烹饪", "健身", "瑜伽",
            "舞蹈", "唱歌", "乐器", "编程", "手工", "园艺"
        ]
        return random.sample(hobbies, k=random.randint(2, 5))
    
    def _generate_career_interests(self, major: str) -> List[str]:
        """根据专业生成职业兴趣"""
        career_map = {
            "计算机科学": ["软件工程师", "算法工程师", "系统架构师"],
            "软件工程": ["前端开发", "后端开发", "全栈工程师", "产品经理"],
            "人工智能": ["AI研究员", "机器学习工程师", "数据科学家"],
            "数据科学": ["数据分析师", "数据工程师", "商业分析师"],
            "电子工程": ["硬件工程师", "嵌入式工程师", "通信工程师"],
            "机械工程": ["机械设计师", "制造工程师", "研发工程师"],
            "经济学": ["经济分析师", "政策研究员", "咨询顾问"],
            "金融学": ["投资分析师", "风险管理", "金融顾问"],
            "心理学": ["心理咨询师", "人力资源", "用户研究"],
            "教育学": ["教师", "教育咨询", "培训师"],
            "新闻传播": ["记者", "编辑", "新媒体运营", "公关"],
            "外语": ["翻译", "教师", "国际商务", "外交"]
        }
        
        careers = career_map.get(major, ["创业", "自由职业"])
        return random.sample(careers, k=min(2, len(careers)))
    
    def _generate_profile_vector(self, big_five: BigFiveScores, mbti_type: str) -> List[float]:
        """生成画像向量"""
        vector = []
        
        # MBTI编码（4维）
        vector.append(1.0 if mbti_type[0] == 'E' else 0.0)
        vector.append(1.0 if mbti_type[1] == 'S' else 0.0)
        vector.append(1.0 if mbti_type[2] == 'T' else 0.0)
        vector.append(1.0 if mbti_type[3] == 'J' else 0.0)
        
        # 大五人格（5维）
        vector.extend([
            big_five.neuroticism,
            big_five.agreeableness,
            big_five.extraversion,
            big_five.openness,
            big_five.conscientiousness
        ])
        
        return vector
    
    def get_virtual_user(self, user_id: str) -> Optional[VirtualUser]:
        """
        获取虚拟用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[VirtualUser]: 虚拟用户对象，如果不存在则返回None
        """
        return self._virtual_users.get(user_id)
    
    def get_virtual_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        获取虚拟用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserProfile]: 用户画像，如果不存在则返回None
        """
        return self._virtual_profiles.get(user_id)
    
    def is_virtual_user(self, user_id: str) -> bool:
        """
        判断是否为虚拟用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否为虚拟用户
        """
        return user_id in self._virtual_users
    
    def simulate_response(self, virtual_user_id: str, message: str, context: Dict) -> Dict:
        """
        模拟虚拟用户的对话回复
        
        Args:
            virtual_user_id: 虚拟用户ID
            message: 收到的消息
            context: 对话上下文
            
        Returns:
            Dict: 包含回复内容和元数据的字典
        """
        virtual_user = self.get_virtual_user(virtual_user_id)
        if not virtual_user:
            raise ValueError(f"Virtual user not found: {virtual_user_id}")
        
        # 模拟回复延迟
        response_delay = random.uniform(*virtual_user.response_speed_range)
        
        # 模拟消息长度
        message_length = random.randint(*virtual_user.message_length_range)
        
        # 根据MBTI类型生成回复风格的提示
        response_hint = self._generate_response_hint(virtual_user, message, context)
        
        return {
            'user_id': virtual_user_id,
            'response_delay': response_delay,
            'expected_length': message_length,
            'response_style': virtual_user.response_style,
            'response_hint': response_hint,
            'mbti_type': virtual_user.mbti_type
        }
    
    def _generate_response_hint(self, virtual_user: VirtualUser, message: str, context: Dict) -> str:
        """生成回复提示"""
        mbti = virtual_user.mbti_type
        
        # 根据MBTI类型生成不同的回复倾向
        hints = {
            'INTJ': '以逻辑和效率为导向，提供深入的分析',
            'INTP': '探讨理论和概念，提出新的视角',
            'ENTJ': '果断给出建议，关注目标和结果',
            'ENTP': '提出创新想法，喜欢辩论和讨论',
            'INFJ': '关注对方感受，提供深刻的洞察',
            'INFP': '表达理想和价值观，富有同理心',
            'ENFJ': '鼓励和激励对方，关注人际关系',
            'ENFP': '热情回应，分享创意和可能性',
            'ISTJ': '提供实用建议，注重细节和规则',
            'ISFJ': '温暖体贴，关心对方需求',
            'ESTJ': '高效解决问题，注重实际操作',
            'ESFJ': '友好互动，营造和谐氛围',
            'ISTP': '冷静分析问题，提供实用解决方案',
            'ISFP': '温和回应，关注当下感受',
            'ESTP': '活力充沛，鼓励行动',
            'ESFP': '活泼互动，分享快乐体验'
        }
        
        return hints.get(mbti, '自然回应')
    
    def update_real_user_count(self, count: int) -> None:
        """
        更新真实用户数量
        
        Args:
            count: 真实用户数量
        """
        self._real_user_count = count
        self.logger.info(f"Real user count updated to: {count}")
        
        # 根据真实用户数量动态调整虚拟用户权重
        self._adjust_virtual_user_weights()
    
    def _adjust_virtual_user_weights(self) -> None:
        """根据真实用户数量动态调整虚拟用户匹配权重"""
        if self._real_user_count < 1000:
            # 真实用户少于1000，虚拟用户权重为1.0
            new_weight = 1.0
        elif self._real_user_count < 10000:
            # 真实用户在1000-10000之间，线性递减
            new_weight = 1.0 - (self._real_user_count - 1000) / 9000
        else:
            # 真实用户超过10000，虚拟用户权重为0（停止推送）
            new_weight = 0.0
        
        # 更新所有虚拟用户的权重
        for virtual_user in self._virtual_users.values():
            virtual_user.match_weight = new_weight
        
        self.logger.info(f"Virtual user match weight adjusted to: {new_weight:.2f}")
    
    def get_statistics(self) -> VirtualUserStats:
        """
        获取虚拟用户统计信息
        
        Returns:
            VirtualUserStats: 统计信息
        """
        # 统计MBTI类型分布
        mbti_distribution = {}
        for virtual_user in self._virtual_users.values():
            mbti_type = virtual_user.mbti_type
            mbti_distribution[mbti_type] = mbti_distribution.get(mbti_type, 0) + 1
        
        # 统计活跃虚拟用户（权重>0）
        active_count = sum(1 for vu in self._virtual_users.values() if vu.match_weight > 0)
        
        # 获取当前权重
        current_weight = list(self._virtual_users.values())[0].match_weight if self._virtual_users else 0.0
        
        return VirtualUserStats(
            total_virtual_users=len(self._virtual_users),
            total_real_users=self._real_user_count,
            virtual_user_weight=current_weight,
            mbti_distribution=mbti_distribution,
            active_virtual_users=active_count,
            timestamp=datetime.now()
        )
    
    def get_all_virtual_users(self) -> List[VirtualUser]:
        """
        获取所有虚拟用户
        
        Returns:
            List[VirtualUser]: 虚拟用户列表
        """
        return list(self._virtual_users.values())
    
    def get_active_virtual_users(self) -> List[VirtualUser]:
        """
        获取所有活跃的虚拟用户（权重>0）
        
        Returns:
            List[VirtualUser]: 活跃虚拟用户列表
        """
        return [vu for vu in self._virtual_users.values() if vu.match_weight > 0]

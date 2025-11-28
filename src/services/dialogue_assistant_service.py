"""AI对话助手服务"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from src.models.conversation import (
    AIIntervention,
    SilenceType,
    UserPreference,
    Message,
    Conversation
)
from src.utils.logger import get_logger
from src.utils.exceptions import ConversationNotFoundError

logger = get_logger(__name__)


class DialogueAssistantService:
    """AI对话助手服务类"""
    
    # 沉默检测阈值
    SILENCE_DURATION_THRESHOLD = 15  # 秒
    SHORT_MESSAGE_THRESHOLD = 30  # 字符
    SHORT_MESSAGE_COUNT = 3  # 连续短消息数量
    
    # 介入频率控制
    INTERVENTION_COOLDOWN = 20 * 60  # 20分钟（秒）
    
    def __init__(self):
        """初始化对话助手服务"""
        # 使用内存存储（实际应用中应使用数据库）
        self.interventions: Dict[str, List[AIIntervention]] = {}
        self.user_preferences: Dict[str, UserPreference] = {}
        self.last_message_time: Dict[str, datetime] = {}
        logger.info("DialogueAssistantService initialized")
    
    def detect_silence(
        self,
        conversation_id: str,
        recent_messages: List[Message]
    ) -> Tuple[bool, Optional[SilenceType]]:
        """
        检测对话沉默
        
        Args:
            conversation_id: 对话ID
            recent_messages: 最近的消息列表
            
        Returns:
            Tuple[bool, Optional[SilenceType]]: (是否沉默, 沉默类型)
        """
        # 检查时间沉默
        current_time = datetime.now()
        last_msg_time = self.last_message_time.get(conversation_id)
        
        time_silence = False
        if last_msg_time:
            silence_duration = (current_time - last_msg_time).total_seconds()
            time_silence = silence_duration > self.SILENCE_DURATION_THRESHOLD
        
        # 检查短消息沉默
        short_message_silence = False
        if len(recent_messages) >= self.SHORT_MESSAGE_COUNT:
            last_n_messages = recent_messages[-self.SHORT_MESSAGE_COUNT:]
            short_message_silence = all(
                len(msg.content) < self.SHORT_MESSAGE_THRESHOLD
                for msg in last_n_messages
            )
        
        # 判断是否沉默
        is_silent = time_silence or short_message_silence
        
        if not is_silent:
            return False, None
        
        # 识别沉默类型
        silence_type = self._identify_silence_type(recent_messages)
        
        logger.info(
            f"Silence detected in conversation {conversation_id}: "
            f"type={silence_type.type}, confidence={silence_type.confidence}"
        )
        
        return True, silence_type
    
    def _identify_silence_type(self, recent_messages: List[Message]) -> SilenceType:
        """
        识别沉默类型（内向型/焦虑型）
        
        Args:
            recent_messages: 最近的消息列表
            
        Returns:
            SilenceType: 沉默类型
        """
        if not recent_messages:
            return SilenceType(type="none", confidence=0.5)
        
        # 分析最近消息的情绪
        anxious_count = 0
        negative_count = 0
        total_with_emotion = 0
        
        for msg in recent_messages[-10:]:  # 分析最近10条消息
            if msg.emotion:
                total_with_emotion += 1
                if msg.emotion == "anxious":
                    anxious_count += 1
                elif msg.emotion == "negative":
                    negative_count += 1
        
        # 如果焦虑情绪占比高，判断为焦虑型沉默
        if total_with_emotion > 0:
            anxious_ratio = anxious_count / total_with_emotion
            if anxious_ratio > 0.4:
                return SilenceType(type="anxious", confidence=min(0.9, anxious_ratio + 0.3))
            
            # 如果负面情绪占比高，也可能是焦虑型
            negative_ratio = (anxious_count + negative_count) / total_with_emotion
            if negative_ratio > 0.5:
                return SilenceType(type="anxious", confidence=min(0.8, negative_ratio + 0.2))
        
        # 默认判断为内向型沉默
        return SilenceType(type="introverted", confidence=0.6)
    
    def should_intervene(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        判断是否应该介入
        
        Args:
            conversation_id: 对话ID
            user_id: 用户ID
            
        Returns:
            bool: 是否应该介入
        """
        # 检查用户偏好
        preference = self.user_preferences.get(user_id)
        if preference and not preference.ai_intervention_enabled:
            logger.info(f"AI intervention disabled for user {user_id}")
            return False
        
        # 检查介入频率限制
        interventions = self.interventions.get(conversation_id, [])
        if interventions:
            last_intervention = interventions[-1]
            time_since_last = (datetime.now() - last_intervention.timestamp).total_seconds()
            
            if time_since_last < self.INTERVENTION_COOLDOWN:
                logger.info(
                    f"Intervention cooldown active for conversation {conversation_id}: "
                    f"{time_since_last:.0f}s since last intervention"
                )
                return False
        
        return True
    
    def generate_topic_suggestion(
        self,
        conversation_id: str,
        scene: str,
        recent_messages: List[Message],
        silence_type: Optional[SilenceType] = None
    ) -> str:
        """
        生成话题建议
        
        Args:
            conversation_id: 对话ID
            scene: 对话场景
            recent_messages: 最近的消息列表
            silence_type: 沉默类型
            
        Returns:
            str: 话题建议内容
        """
        # 场景特定的话题模板
        scene_topics = {
            "考研自习室": [
                "你们可以聊聊各自的备考进度，互相鼓励一下",
                "不如分享一下最近学习中遇到的难点？说不定能互相帮助",
                "可以聊聊目标院校的情况，或者交流一下学习方法",
                "休息一下，聊聊考研之外的兴趣爱好也不错"
            ],
            "职业咨询室": [
                "可以聊聊各自对未来职业的规划和想法",
                "不如分享一下实习或工作的经验？",
                "聊聊你们理想中的工作环境是什么样的",
                "可以交流一下对行业发展的看法"
            ],
            "心理树洞": [
                "如果愿意的话，可以聊聊最近的心情和感受",
                "有时候倾诉出来会好受一些，对方也许能理解你",
                "可以聊聊让你感到放松的事情",
                "不如分享一下你们的解压方式？"
            ],
            "兴趣社群": [
                "可以聊聊你们共同的兴趣爱好",
                "不如分享一下最近发现的有趣内容？",
                "聊聊你们是怎么培养这个兴趣的",
                "可以交流一下相关的经验和心得"
            ]
        }
        
        # 根据沉默类型调整建议语气
        if silence_type and silence_type.type == "anxious":
            prefix = "别紧张，慢慢来。"
        elif silence_type and silence_type.type == "introverted":
            prefix = "没关系，可以从简单的话题开始。"
        else:
            prefix = ""
        
        # 获取场景话题
        topics = scene_topics.get(scene, [
            "可以聊聊你们的共同点",
            "不如分享一下各自的想法？",
            "聊聊你们感兴趣的话题"
        ])
        
        # 简单选择第一个话题（实际应用中可以使用更智能的选择策略）
        import random
        topic = random.choice(topics)
        
        suggestion = f"{prefix}{topic}" if prefix else topic
        
        logger.info(
            f"Generated topic suggestion for conversation {conversation_id}: {suggestion}"
        )
        
        return suggestion
    
    def provide_emotional_support(
        self,
        user_id: str,
        emotion: str,
        recent_messages: List[Message]
    ) -> str:
        """
        提供情绪支持
        
        Args:
            user_id: 用户ID
            emotion: 情绪类型
            recent_messages: 最近的消息列表
            
        Returns:
            str: 情绪支持内容
        """
        # 情绪支持模板
        support_templates = {
            "anxious": [
                "我注意到你可能有些紧张，深呼吸，放轻松。对方也是来交流的朋友。",
                "感到焦虑很正常，慢慢来，不用着急。你可以先从简单的话题开始。",
                "别担心，每个人都会有紧张的时候。试着放松心情，享受交流的过程。"
            ],
            "negative": [
                "我感觉到你可能心情不太好，如果愿意的话，可以和对方聊聊。",
                "有时候倾诉出来会好受一些，对方也许能理解你的感受。",
                "心情低落的时候，和理解你的人聊聊天会有帮助。"
            ],
            "positive": [
                "看起来你们聊得很开心，继续保持这种轻松的氛围吧！",
                "很高兴看到你们交流得这么愉快！"
            ],
            "neutral": [
                "放轻松，真诚地表达自己就好。",
                "慢慢来，找到你们都感兴趣的话题。"
            ]
        }
        
        # 获取支持语句
        templates = support_templates.get(emotion, support_templates["neutral"])
        
        import random
        support = random.choice(templates)
        
        logger.info(
            f"Generated emotional support for user {user_id} with emotion {emotion}: {support}"
        )
        
        return support
    
    def record_intervention(
        self,
        conversation_id: str,
        trigger_type: str,
        intervention_type: str,
        content: str
    ) -> AIIntervention:
        """
        记录AI介入
        
        Args:
            conversation_id: 对话ID
            trigger_type: 触发类型
            intervention_type: 介入类型
            content: 介入内容
            
        Returns:
            AIIntervention: AI介入记录
        """
        intervention_id = str(uuid.uuid4())
        
        intervention = AIIntervention(
            intervention_id=intervention_id,
            conversation_id=conversation_id,
            trigger_type=trigger_type,
            intervention_type=intervention_type,
            content=content,
            timestamp=datetime.now()
        )
        
        # 存储介入记录
        if conversation_id not in self.interventions:
            self.interventions[conversation_id] = []
        self.interventions[conversation_id].append(intervention)
        
        logger.info(
            f"Recorded AI intervention {intervention_id} for conversation {conversation_id}"
        )
        
        return intervention
    
    def update_user_response(
        self,
        intervention_id: str,
        conversation_id: str,
        response: str
    ) -> AIIntervention:
        """
        更新用户对AI介入的响应
        
        Args:
            intervention_id: 介入记录ID
            conversation_id: 对话ID
            response: 用户响应 (accepted, rejected, ignored)
            
        Returns:
            AIIntervention: 更新后的AI介入记录
        """
        interventions = self.interventions.get(conversation_id, [])
        
        for intervention in interventions:
            if intervention.intervention_id == intervention_id:
                intervention.user_response = response
                
                logger.info(
                    f"Updated user response for intervention {intervention_id}: {response}"
                )
                
                return intervention
        
        raise ValueError(f"Intervention {intervention_id} not found")
    
    def record_user_preference(
        self,
        user_id: str,
        ai_intervention_enabled: bool
    ) -> UserPreference:
        """
        记录用户偏好
        
        Args:
            user_id: 用户ID
            ai_intervention_enabled: 是否启用AI介入
            
        Returns:
            UserPreference: 用户偏好
        """
        preference = self.user_preferences.get(user_id)
        
        if preference:
            preference.ai_intervention_enabled = ai_intervention_enabled
            preference.updated_at = datetime.now()
            
            if not ai_intervention_enabled:
                preference.last_rejection_time = datetime.now()
                preference.rejection_count += 1
        else:
            preference = UserPreference(
                user_id=user_id,
                ai_intervention_enabled=ai_intervention_enabled,
                last_rejection_time=datetime.now() if not ai_intervention_enabled else None,
                rejection_count=1 if not ai_intervention_enabled else 0,
                updated_at=datetime.now()
            )
            self.user_preferences[user_id] = preference
        
        logger.info(
            f"Recorded user preference for user {user_id}: "
            f"ai_intervention_enabled={ai_intervention_enabled}"
        )
        
        return preference
    
    def get_user_preference(self, user_id: str) -> Optional[UserPreference]:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserPreference]: 用户偏好，如果不存在则返回None
        """
        return self.user_preferences.get(user_id)
    
    def get_intervention_history(
        self,
        conversation_id: str
    ) -> List[AIIntervention]:
        """
        获取对话的AI介入历史
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            List[AIIntervention]: AI介入记录列表
        """
        return self.interventions.get(conversation_id, [])
    
    def update_last_message_time(
        self,
        conversation_id: str,
        timestamp: datetime
    ) -> None:
        """
        更新对话的最后消息时间
        
        Args:
            conversation_id: 对话ID
            timestamp: 时间戳
        """
        self.last_message_time[conversation_id] = timestamp
        
    def get_silence_duration(self, conversation_id: str) -> float:
        """
        获取当前沉默时长（秒）
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            float: 沉默时长（秒）
        """
        last_msg_time = self.last_message_time.get(conversation_id)
        if not last_msg_time:
            return 0.0
        
        return (datetime.now() - last_msg_time).total_seconds()

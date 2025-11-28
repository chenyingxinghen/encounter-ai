"""对话质量监测服务"""
import uuid
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter
from src.models.conversation import Conversation, Message
from src.models.quality import (
    QualityMetrics,
    ConversationReport,
    SatisfactionFeedback,
    QualityMonitoringRequest,
    SatisfactionFeedbackRequest,
    TopicSegment
)
from src.services.conversation_service import ConversationService
from src.utils.logger import get_logger
from src.utils.exceptions import ConversationNotFoundError

logger = get_logger(__name__)


class ConversationQualityService:
    """对话质量监测服务类"""
    
    def __init__(self, conversation_service: ConversationService):
        """
        初始化对话质量监测服务
        
        Args:
            conversation_service: 对话服务实例
        """
        self.conversation_service = conversation_service
        self.feedback_storage: Dict[str, List[SatisfactionFeedback]] = {}
        self.reports_storage: Dict[str, ConversationReport] = {}
        
        # 质量阈值配置
        self.LOW_QUALITY_THRESHOLD = 5.0  # 整体质量得分低于5.0视为低质量
        self.MIN_MESSAGES_FOR_ANALYSIS = 10  # 至少10条消息才进行分析
        
        logger.info("ConversationQualityService initialized")
    
    def analyze_topic_depth(
        self,
        messages: List[Message]
    ) -> Tuple[float, int, float]:
        """
        分析话题深度
        
        Args:
            messages: 消息列表
            
        Returns:
            Tuple[float, int, float]: (话题深度得分, 话题数量, 平均话题持续时间)
        """
        if len(messages) < 2:
            return 0.0, 0, 0.0
        
        # 提取话题片段
        topic_segments = self._segment_topics(messages)
        
        if not topic_segments:
            return 0.0, 0, 0.0
        
        # 计算话题深度得分
        total_depth = sum(segment.depth_score for segment in topic_segments)
        avg_depth = total_depth / len(topic_segments)
        
        # 计算平均话题持续时间
        total_duration = sum(segment.message_count for segment in topic_segments)
        avg_duration = total_duration / len(topic_segments)
        
        # 话题深度得分 = 平均深度 * (1 + log(话题数量))
        # 鼓励多样化的话题，但不过分惩罚专注的对话
        import math
        topic_diversity_factor = 1 + math.log(len(topic_segments) + 1) / 10
        final_score = min(10.0, avg_depth * topic_diversity_factor)
        
        logger.info(
            f"Topic depth analysis: score={final_score:.2f}, "
            f"topics={len(topic_segments)}, avg_duration={avg_duration:.2f}"
        )
        
        return final_score, len(topic_segments), avg_duration
    
    def _segment_topics(self, messages: List[Message]) -> List[TopicSegment]:
        """
        将对话分割成话题片段
        
        Args:
            messages: 消息列表
            
        Returns:
            List[TopicSegment]: 话题片段列表
        """
        if len(messages) < 2:
            return []
        
        segments = []
        current_segment_start = 0
        current_keywords = self._extract_keywords(messages[0].content)
        
        for i in range(1, len(messages)):
            msg_keywords = self._extract_keywords(messages[i].content)
            
            # 计算关键词重叠度
            overlap = len(set(current_keywords) & set(msg_keywords))
            similarity = overlap / max(len(current_keywords), len(msg_keywords), 1)
            
            # 如果相似度低于阈值，认为话题发生了转换
            if similarity < 0.3 or i - current_segment_start > 20:
                # 保存当前片段
                segment_messages = messages[current_segment_start:i]
                depth_score = self._calculate_segment_depth(segment_messages)
                
                segment = TopicSegment(
                    topic_id=str(uuid.uuid4()),
                    conversation_id=messages[0].conversation_id,
                    start_message_index=current_segment_start,
                    end_message_index=i - 1,
                    topic_keywords=current_keywords[:5],  # 保留前5个关键词
                    depth_score=depth_score,
                    message_count=i - current_segment_start
                )
                segments.append(segment)
                
                # 开始新片段
                current_segment_start = i
                current_keywords = msg_keywords
            else:
                # 合并关键词
                current_keywords = list(set(current_keywords + msg_keywords))
        
        # 保存最后一个片段
        if current_segment_start < len(messages):
            segment_messages = messages[current_segment_start:]
            depth_score = self._calculate_segment_depth(segment_messages)
            
            segment = TopicSegment(
                topic_id=str(uuid.uuid4()),
                conversation_id=messages[0].conversation_id,
                start_message_index=current_segment_start,
                end_message_index=len(messages) - 1,
                topic_keywords=current_keywords[:5],
                depth_score=depth_score,
                message_count=len(messages) - current_segment_start
            )
            segments.append(segment)
        
        return segments
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 文本内容
            
        Returns:
            List[str]: 关键词列表
        """
        # 简单的关键词提取：移除停用词，提取长度>=2的词
        stopwords = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '们',
                     '这', '那', '有', '和', '就', '不', '都', '而', '及', '与',
                     '吗', '呢', '吧', '啊', '哦', '嗯', '哈', '呀'}
        
        # 使用正则表达式分词（简单版本）
        words = re.findall(r'[\u4e00-\u9fa5]+', text)
        keywords = [w for w in words if len(w) >= 2 and w not in stopwords]
        
        return keywords
    
    def _calculate_segment_depth(self, messages: List[Message]) -> float:
        """
        计算话题片段的深度得分
        
        Args:
            messages: 消息列表
            
        Returns:
            float: 深度得分 (0-10)
        """
        if not messages:
            return 0.0
        
        # 深度指标：
        # 1. 消息长度（更长的消息表示更深入的讨论）
        avg_length = sum(len(msg.content) for msg in messages) / len(messages)
        length_score = min(10.0, avg_length / 10)  # 100字为满分
        
        # 2. 消息数量（更多的消息表示持续的讨论）
        count_score = min(10.0, len(messages) / 2)  # 20条消息为满分
        
        # 3. 词汇多样性
        all_words = []
        for msg in messages:
            all_words.extend(self._extract_keywords(msg.content))
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        diversity_score = (unique_words / max(total_words, 1)) * 10 if total_words > 0 else 0
        
        # 综合得分
        depth_score = (length_score * 0.4 + count_score * 0.3 + diversity_score * 0.3)
        
        return min(10.0, depth_score)
    
    def analyze_response_consistency(
        self,
        messages: List[Message],
        conversation: Conversation
    ) -> Tuple[float, float, float]:
        """
        分析回应一致性
        
        Args:
            messages: 消息列表
            conversation: 对话对象
            
        Returns:
            Tuple[float, float, float]: (回应一致性得分, 平均回应时间, 回应长度方差)
        """
        if len(messages) < 2:
            return 0.0, 0.0, 0.0
        
        # 计算回应时间
        response_times = []
        for i in range(1, len(messages)):
            if messages[i].sender_id != messages[i-1].sender_id:
                time_diff = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()
                response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # 计算回应长度方差
        message_lengths = [len(msg.content) for msg in messages]
        avg_length = sum(message_lengths) / len(message_lengths)
        variance = sum((l - avg_length) ** 2 for l in message_lengths) / len(message_lengths)
        
        # 计算一致性得分
        # 1. 回应时间一致性（回应时间越稳定越好）
        if response_times:
            time_variance = sum((t - avg_response_time) ** 2 for t in response_times) / len(response_times)
            time_consistency = 1.0 / (1.0 + time_variance / 100)  # 归一化
        else:
            time_consistency = 0.0
        
        # 2. 回应长度一致性（长度越稳定越好）
        length_consistency = 1.0 / (1.0 + variance / 1000)  # 归一化
        
        # 3. 交互平衡性（双方消息数量应该相对平衡）
        user_a_count = sum(1 for msg in messages if msg.sender_id == conversation.user_a_id)
        user_b_count = sum(1 for msg in messages if msg.sender_id == conversation.user_b_id)
        balance = min(user_a_count, user_b_count) / max(user_a_count, user_b_count, 1)
        
        # 综合得分
        consistency_score = (time_consistency * 0.3 + length_consistency * 0.3 + balance * 0.4)
        
        logger.info(
            f"Response consistency analysis: score={consistency_score:.2f}, "
            f"avg_response_time={avg_response_time:.2f}s, variance={variance:.2f}"
        )
        
        return consistency_score, avg_response_time, variance
    
    def analyze_emotion_sync(
        self,
        messages: List[Message]
    ) -> Tuple[float, float]:
        """
        分析情感同步性
        
        Args:
            messages: 消息列表
            
        Returns:
            Tuple[float, float]: (情感同步性得分, 情绪一致率)
        """
        if len(messages) < 2:
            return 0.0, 0.0
        
        # 为没有情感标注的消息进行简单的情感分析
        messages_with_emotion = self._analyze_emotions(messages)
        
        # 计算相邻消息的情感一致性
        emotion_matches = 0
        total_pairs = 0
        
        for i in range(1, len(messages_with_emotion)):
            if messages_with_emotion[i].sender_id != messages_with_emotion[i-1].sender_id:
                emotion1 = messages_with_emotion[i-1].emotion
                emotion2 = messages_with_emotion[i].emotion
                
                if emotion1 and emotion2:
                    # 情感匹配规则
                    if emotion1 == emotion2:
                        emotion_matches += 1.0
                    elif self._emotions_compatible(emotion1, emotion2):
                        emotion_matches += 0.5
                    
                    total_pairs += 1
        
        # 计算情绪一致率
        alignment_rate = emotion_matches / total_pairs if total_pairs > 0 else 0.0
        
        # 计算情感同步性得分
        # 考虑情绪一致率和情绪强度的协调性
        emotion_sync_score = alignment_rate
        
        logger.info(
            f"Emotion sync analysis: score={emotion_sync_score:.2f}, "
            f"alignment_rate={alignment_rate:.2f}"
        )
        
        return emotion_sync_score, alignment_rate
    
    def _analyze_emotions(self, messages: List[Message]) -> List[Message]:
        """
        为消息分析情感（如果尚未标注）
        
        Args:
            messages: 消息列表
            
        Returns:
            List[Message]: 带有情感标注的消息列表
        """
        # 简单的基于关键词的情感分析
        positive_keywords = ['开心', '高兴', '快乐', '喜欢', '棒', '好', '赞', '哈哈', '😊', '👍']
        negative_keywords = ['难过', '伤心', '失望', '糟糕', '差', '烦', '累', '😢', '😞']
        anxious_keywords = ['担心', '焦虑', '紧张', '害怕', '不安', '压力', '😰', '😨']
        
        result_messages = []
        for msg in messages:
            if msg.emotion is None:
                # 分析情感
                content_lower = msg.content.lower()
                
                positive_count = sum(1 for kw in positive_keywords if kw in content_lower)
                negative_count = sum(1 for kw in negative_keywords if kw in content_lower)
                anxious_count = sum(1 for kw in anxious_keywords if kw in content_lower)
                
                # 确定主导情感
                if anxious_count > 0:
                    emotion = 'anxious'
                    intensity = min(1.0, anxious_count / 3)
                elif positive_count > negative_count:
                    emotion = 'positive'
                    intensity = min(1.0, positive_count / 3)
                elif negative_count > positive_count:
                    emotion = 'negative'
                    intensity = min(1.0, negative_count / 3)
                else:
                    emotion = 'neutral'
                    intensity = 0.5
                
                # 创建新的消息对象（带有情感标注）
                msg_dict = msg.dict()
                msg_dict['emotion'] = emotion
                msg_dict['emotion_intensity'] = intensity
                result_messages.append(Message(**msg_dict))
            else:
                result_messages.append(msg)
        
        return result_messages
    
    def _emotions_compatible(self, emotion1: str, emotion2: str) -> bool:
        """
        判断两种情感是否兼容
        
        Args:
            emotion1: 情感1
            emotion2: 情感2
            
        Returns:
            bool: 是否兼容
        """
        # 定义兼容的情感对
        compatible_pairs = {
            ('positive', 'neutral'),
            ('neutral', 'positive'),
            ('negative', 'anxious'),
            ('anxious', 'negative'),
        }
        
        return (emotion1, emotion2) in compatible_pairs
    
    def monitor_conversation_quality(
        self,
        request: QualityMonitoringRequest
    ) -> QualityMetrics:
        """
        实时监测对话质量
        
        Args:
            request: 质量监测请求
            
        Returns:
            QualityMetrics: 质量指标
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        # 获取对话信息
        conversation = self.conversation_service.get_conversation(request.conversation_id)
        
        # 获取对话历史
        from src.models.conversation import ConversationHistoryRequest
        history_request = ConversationHistoryRequest(
            conversation_id=request.conversation_id,
            limit=500
        )
        messages = self.conversation_service.get_conversation_history(history_request)
        messages = list(reversed(messages))  # 按时间正序
        
        if len(messages) < self.MIN_MESSAGES_FOR_ANALYSIS:
            # 消息太少，返回默认指标
            logger.warning(
                f"Conversation {request.conversation_id} has too few messages "
                f"({len(messages)}) for quality analysis"
            )
            return QualityMetrics(
                conversation_id=request.conversation_id,
                topic_depth_score=0.0,
                topic_count=0,
                average_topic_duration=0.0,
                response_consistency_score=0.0,
                average_response_time=0.0,
                response_length_variance=0.0,
                emotion_sync_score=0.0,
                emotion_alignment_rate=0.0,
                overall_quality_score=0.0
            )
        
        # 分析话题深度
        topic_depth_score, topic_count, avg_topic_duration = self.analyze_topic_depth(messages)
        
        # 分析回应一致性
        response_consistency_score, avg_response_time, response_variance = \
            self.analyze_response_consistency(messages, conversation)
        
        # 分析情感同步性
        emotion_sync_score, emotion_alignment_rate = self.analyze_emotion_sync(messages)
        
        # 计算整体质量得分
        overall_quality_score = (
            topic_depth_score * 0.4 +
            response_consistency_score * 10 * 0.3 +
            emotion_sync_score * 10 * 0.3
        )
        
        metrics = QualityMetrics(
            conversation_id=request.conversation_id,
            topic_depth_score=topic_depth_score,
            topic_count=topic_count,
            average_topic_duration=avg_topic_duration,
            response_consistency_score=response_consistency_score,
            average_response_time=avg_response_time,
            response_length_variance=response_variance,
            emotion_sync_score=emotion_sync_score,
            emotion_alignment_rate=emotion_alignment_rate,
            overall_quality_score=overall_quality_score
        )
        
        # 更新对话的质量指标
        self.conversation_service.update_quality_metrics(
            conversation_id=request.conversation_id,
            topic_depth_score=topic_depth_score,
            emotion_sync_score=emotion_sync_score
        )
        
        logger.info(
            f"Quality metrics calculated for conversation {request.conversation_id}: "
            f"overall_score={overall_quality_score:.2f}"
        )
        
        return metrics
    
    def generate_conversation_report(
        self,
        conversation_id: str
    ) -> ConversationReport:
        """
        生成对话质量报告
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            ConversationReport: 对话质量报告
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        # 获取对话信息
        conversation = self.conversation_service.get_conversation(conversation_id)
        
        # 监测质量指标
        request = QualityMonitoringRequest(conversation_id=conversation_id)
        metrics = self.monitor_conversation_quality(request)
        
        # 计算对话时长
        if conversation.ended_at:
            duration = (conversation.ended_at - conversation.started_at).total_seconds()
        else:
            duration = (datetime.now() - conversation.started_at).total_seconds()
        
        # 获取满意度反馈
        feedbacks = self.feedback_storage.get(conversation_id, [])
        user_a_satisfaction = None
        user_b_satisfaction = None
        
        for feedback in feedbacks:
            if feedback.user_id == conversation.user_a_id:
                user_a_satisfaction = feedback.satisfaction_score
            elif feedback.user_id == conversation.user_b_id:
                user_b_satisfaction = feedback.satisfaction_score
        
        # 生成建议
        suggestions = self._generate_suggestions(metrics, conversation)
        
        # 判断是否为低质量对话
        is_low_quality = metrics.overall_quality_score < self.LOW_QUALITY_THRESHOLD
        
        # 创建报告
        report_id = str(uuid.uuid4())
        report = ConversationReport(
            report_id=report_id,
            conversation_id=conversation_id,
            user_a_id=conversation.user_a_id,
            user_b_id=conversation.user_b_id,
            scene=conversation.scene,
            started_at=conversation.started_at,
            ended_at=conversation.ended_at,
            duration_seconds=duration,
            message_count=conversation.message_count,
            metrics=metrics,
            user_a_satisfaction=user_a_satisfaction,
            user_b_satisfaction=user_b_satisfaction,
            suggestions=suggestions,
            is_low_quality=is_low_quality
        )
        
        # 存储报告
        self.reports_storage[conversation_id] = report
        
        logger.info(
            f"Generated conversation report {report_id} for conversation {conversation_id}"
        )
        
        return report
    
    def _generate_suggestions(
        self,
        metrics: QualityMetrics,
        conversation: Conversation
    ) -> List[str]:
        """
        根据质量指标生成改进建议
        
        Args:
            metrics: 质量指标
            conversation: 对话对象
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        
        # 话题深度建议
        if metrics.topic_depth_score < 5.0:
            suggestions.append("尝试深入探讨感兴趣的话题，分享更多细节和个人经历")
        
        if metrics.topic_count < 3:
            suggestions.append("可以尝试探索更多不同的话题，增加对话的多样性")
        
        # 回应一致性建议
        if metrics.response_consistency_score < 0.5:
            suggestions.append("保持稳定的回应节奏，让对话更加流畅")
        
        if metrics.average_response_time > 60:
            suggestions.append("尽量及时回复消息，避免对话中断")
        
        # 情感同步性建议
        if metrics.emotion_sync_score < 0.5:
            suggestions.append("多关注对方的情绪状态，给予适当的情感回应")
        
        # 整体质量建议
        if metrics.overall_quality_score < 5.0:
            suggestions.append("当前对话质量较低，建议尝试其他匹配对象")
        
        # 场景特定建议
        if conversation.scene == '考研自习室':
            if metrics.topic_depth_score < 6.0:
                suggestions.append("可以分享更多学习方法和备考经验")
        elif conversation.scene == '心理树洞':
            if metrics.emotion_sync_score < 0.6:
                suggestions.append("多给予对方情感支持和共情")
        
        return suggestions
    
    def collect_satisfaction_feedback(
        self,
        request: SatisfactionFeedbackRequest
    ) -> SatisfactionFeedback:
        """
        收集满意度反馈
        
        Args:
            request: 满意度反馈请求
            
        Returns:
            SatisfactionFeedback: 满意度反馈对象
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        # 验证对话存在
        conversation = self.conversation_service.get_conversation(request.conversation_id)
        
        # 验证用户是对话参与者
        if request.user_id not in [conversation.user_a_id, conversation.user_b_id]:
            from src.utils.exceptions import UnauthorizedAccessError
            raise UnauthorizedAccessError(
                f"User {request.user_id} is not a participant in conversation {request.conversation_id}"
            )
        
        # 创建反馈
        feedback_id = str(uuid.uuid4())
        feedback = SatisfactionFeedback(
            feedback_id=feedback_id,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            satisfaction_score=request.satisfaction_score,
            feedback_text=request.feedback_text,
            feedback_tags=request.feedback_tags
        )
        
        # 存储反馈
        if request.conversation_id not in self.feedback_storage:
            self.feedback_storage[request.conversation_id] = []
        self.feedback_storage[request.conversation_id].append(feedback)
        
        # 更新对话的满意度得分
        self.conversation_service.update_quality_metrics(
            conversation_id=request.conversation_id,
            satisfaction_score=request.satisfaction_score
        )
        
        logger.info(
            f"Collected satisfaction feedback {feedback_id} from user {request.user_id} "
            f"for conversation {request.conversation_id}: score={request.satisfaction_score}"
        )
        
        return feedback
    
    def detect_low_quality_conversation(
        self,
        conversation_id: str
    ) -> Tuple[bool, List[str]]:
        """
        检测低质量对话并提供建议
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Tuple[bool, List[str]]: (是否为低质量对话, 建议列表)
            
        Raises:
            ConversationNotFoundError: 对话不存在
        """
        # 监测质量指标
        request = QualityMonitoringRequest(conversation_id=conversation_id)
        metrics = self.monitor_conversation_quality(request)
        
        # 判断是否为低质量对话
        is_low_quality = metrics.overall_quality_score < self.LOW_QUALITY_THRESHOLD
        
        # 生成建议
        conversation = self.conversation_service.get_conversation(conversation_id)
        suggestions = self._generate_suggestions(metrics, conversation)
        
        if is_low_quality:
            suggestions.append("建议尝试其他匹配对象，寻找更合适的交流伙伴")
        
        logger.info(
            f"Low quality detection for conversation {conversation_id}: "
            f"is_low_quality={is_low_quality}, overall_score={metrics.overall_quality_score:.2f}"
        )
        
        return is_low_quality, suggestions
    
    def get_conversation_report(self, conversation_id: str) -> Optional[ConversationReport]:
        """
        获取对话质量报告
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Optional[ConversationReport]: 对话质量报告，如果不存在则返回None
        """
        return self.reports_storage.get(conversation_id)
    
    def get_user_feedbacks(self, conversation_id: str) -> List[SatisfactionFeedback]:
        """
        获取对话的所有满意度反馈
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            List[SatisfactionFeedback]: 满意度反馈列表
        """
        return self.feedback_storage.get(conversation_id, [])

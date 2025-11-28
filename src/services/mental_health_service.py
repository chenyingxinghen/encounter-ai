"""心理健康监测与支持服务"""
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from collections import defaultdict

from src.models.mental_health import (
    EmotionState,
    MentalHealthStatus,
    MentalHealthResource,
    ResourcePushRecord,
    RiskAlert,
    AnonymousSession,
    ProfessionalReferral,
    EmotionAnalysisRequest,
    MentalHealthCheckRequest
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MentalHealthService:
    """心理健康监测与支持服务"""
    
    # 负面情绪关键词库
    NEGATIVE_KEYWORDS = {
        'anxious': ['焦虑', '紧张', '不安', '担心', '害怕', '恐惧', '压力大', '烦躁'],
        'depressed': ['抑郁', '沮丧', '绝望', '无助', '痛苦', '难过', '伤心', '失落', 
                      '孤独', '空虚', '麻木', '没意思', '活着没意义'],
        'suicide_risk': ['自杀', '结束生命', '不想活', '活不下去', '想死', '了结', 
                        '解脱', '一了百了', '跳楼', '割腕'],
        'self_harm': ['自残', '伤害自己', '割伤', '烫伤', '打自己']
    }
    
    # 心理健康资源库
    DEFAULT_RESOURCES = [
        {
            'resource_id': 'res_001',
            'resource_type': 'hotline',
            'title': '全国心理援助热线',
            'description': '24小时免费心理咨询热线',
            'contact_info': '400-161-9995',
            'target_emotions': ['anxious', 'depressed'],
            'priority': 10
        },
        {
            'resource_id': 'res_002',
            'resource_type': 'hotline',
            'title': '北京心理危机研究与干预中心',
            'description': '专业心理危机干预热线',
            'contact_info': '010-82951332',
            'target_emotions': ['suicide_risk', 'severe_depression'],
            'priority': 10
        },
        {
            'resource_id': 'res_003',
            'resource_type': 'counseling',
            'title': '校园心理咨询中心',
            'description': '学校提供的免费心理咨询服务',
            'content': '请联系您所在学校的心理咨询中心预约咨询',
            'target_emotions': ['anxious', 'depressed'],
            'priority': 8
        },
        {
            'resource_id': 'res_004',
            'resource_type': 'article',
            'title': '如何应对焦虑情绪',
            'description': '科学的焦虑管理方法',
            'url': 'https://example.com/anxiety-management',
            'target_emotions': ['anxious'],
            'priority': 5
        },
        {
            'resource_id': 'res_005',
            'resource_type': 'article',
            'title': '走出抑郁的阴霾',
            'description': '理解和应对抑郁情绪',
            'url': 'https://example.com/depression-help',
            'target_emotions': ['depressed'],
            'priority': 5
        }
    ]
    
    def __init__(self):
        """初始化服务"""
        # 存储用户情绪状态（实际应使用数据库）
        self.emotion_states: Dict[str, List[EmotionState]] = defaultdict(list)
        # 存储心理健康状态
        self.health_statuses: Dict[str, MentalHealthStatus] = {}
        # 存储资源推送记录
        self.push_records: Dict[str, List[ResourcePushRecord]] = defaultdict(list)
        # 存储风险预警
        self.risk_alerts: List[RiskAlert] = []
        # 存储匿名会话
        self.anonymous_sessions: Dict[str, AnonymousSession] = {}
        # 存储专业转介
        self.referrals: List[ProfessionalReferral] = []
        
        # 初始化资源库
        self.resources: Dict[str, MentalHealthResource] = {}
        for res_data in self.DEFAULT_RESOURCES:
            resource = MentalHealthResource(**res_data)
            self.resources[resource.resource_id] = resource
        
        logger.info("心理健康监测服务初始化完成")
    
    def analyze_emotion(self, request: EmotionAnalysisRequest) -> EmotionState:
        """
        分析文本情感
        
        Args:
            request: 情感分析请求
            
        Returns:
            EmotionState: 情绪状态
        """
        text = request.text.lower()
        
        # 检测负面情绪关键词
        detected_keywords = []
        emotion_scores = {
            'anxious': 0.0,
            'depressed': 0.0,
            'suicide_risk': 0.0,
            'self_harm': 0.0,
            'negative': 0.0
        }
        
        # 检测各类关键词
        for emotion_type, keywords in self.NEGATIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    detected_keywords.append(keyword)
                    emotion_scores[emotion_type] += 1.0
        
        # 确定主要情绪类型和强度
        if emotion_scores['suicide_risk'] > 0:
            emotion_type = 'depressed'  # 自杀风险归类为严重抑郁
            intensity = min(1.0, 0.8 + emotion_scores['suicide_risk'] * 0.1)
        elif emotion_scores['self_harm'] > 0:
            emotion_type = 'depressed'
            intensity = min(1.0, 0.7 + emotion_scores['self_harm'] * 0.1)
        elif emotion_scores['depressed'] > 0:
            emotion_type = 'depressed'
            intensity = min(1.0, 0.5 + emotion_scores['depressed'] * 0.1)
        elif emotion_scores['anxious'] > 0:
            emotion_type = 'anxious'
            intensity = min(1.0, 0.5 + emotion_scores['anxious'] * 0.1)
        else:
            # 简单的正面/负面判断
            negative_words = ['不好', '糟糕', '难受', '不开心', '烦']
            positive_words = ['开心', '高兴', '快乐', '好', '棒', '喜欢']
            
            neg_count = sum(1 for word in negative_words if word in text)
            pos_count = sum(1 for word in positive_words if word in text)
            
            if neg_count > pos_count:
                emotion_type = 'negative'
                intensity = min(0.6, 0.3 + neg_count * 0.1)
            elif pos_count > neg_count:
                emotion_type = 'positive'
                intensity = min(0.8, 0.4 + pos_count * 0.1)
            else:
                emotion_type = 'neutral'
                intensity = 0.3
        
        # 创建情绪状态
        emotion_state = EmotionState(
            user_id=request.user_id or "unknown",
            emotion_type=emotion_type,
            intensity=intensity,
            detected_keywords=detected_keywords,
            source_message_id=request.message_id,
            timestamp=datetime.now()
        )
        
        # 存储情绪状态
        if request.user_id:
            self.emotion_states[request.user_id].append(emotion_state)
            # 只保留最近30天的记录
            cutoff_date = datetime.now() - timedelta(days=30)
            self.emotion_states[request.user_id] = [
                es for es in self.emotion_states[request.user_id]
                if es.timestamp >= cutoff_date
            ]
        
        logger.info(f"情感分析完成: user_id={request.user_id}, emotion={emotion_type}, intensity={intensity:.2f}")
        
        return emotion_state
    
    def check_mental_health(self, request: MentalHealthCheckRequest) -> MentalHealthStatus:
        """
        检查用户心理健康状态
        
        Args:
            request: 心理健康检查请求
            
        Returns:
            MentalHealthStatus: 心理健康状态
        """
        user_id = request.user_id
        check_days = request.check_recent_days
        
        # 获取最近的情绪记录
        cutoff_date = datetime.now() - timedelta(days=check_days)
        recent_emotions = [
            es for es in self.emotion_states.get(user_id, [])
            if es.timestamp >= cutoff_date
        ]
        
        # 计算负面情绪天数
        negative_emotion_days = 0
        last_negative_date = None
        
        if recent_emotions:
            # 按日期分组
            emotions_by_date = defaultdict(list)
            for emotion in recent_emotions:
                date_key = emotion.timestamp.date()
                emotions_by_date[date_key].append(emotion)
            
            # 检查连续负面情绪天数
            sorted_dates = sorted(emotions_by_date.keys(), reverse=True)
            consecutive_negative = 0
            
            for date in sorted_dates:
                day_emotions = emotions_by_date[date]
                # 如果当天有负面情绪（焦虑或抑郁）
                has_negative = any(
                    e.emotion_type in ['anxious', 'depressed'] and e.intensity > 0.5
                    for e in day_emotions
                )
                
                if has_negative:
                    consecutive_negative += 1
                    if last_negative_date is None:
                        last_negative_date = datetime.combine(date, datetime.min.time())
                else:
                    break
            
            negative_emotion_days = consecutive_negative
        
        # 计算情绪稳定性得分
        if recent_emotions:
            # 情绪波动越大，稳定性越低
            intensities = [e.intensity for e in recent_emotions]
            if len(intensities) > 1:
                variance = sum((x - sum(intensities)/len(intensities))**2 for x in intensities) / len(intensities)
                emotion_stability_score = max(0.0, 1.0 - variance)
            else:
                emotion_stability_score = 0.7
            
            # 负面情绪占比
            negative_count = sum(1 for e in recent_emotions if e.emotion_type in ['anxious', 'depressed'])
            negative_ratio = negative_count / len(recent_emotions)
            emotion_stability_score *= (1.0 - negative_ratio * 0.5)
        else:
            emotion_stability_score = 0.8  # 默认值
        
        # 确定风险等级
        risk_level = self._calculate_risk_level(
            negative_emotion_days,
            emotion_stability_score,
            recent_emotions
        )
        
        # 创建或更新心理健康状态
        status = MentalHealthStatus(
            user_id=user_id,
            risk_level=risk_level,
            emotion_stability_score=emotion_stability_score,
            negative_emotion_days=negative_emotion_days,
            last_negative_emotion_date=last_negative_date,
            recent_emotions=recent_emotions[-10:],  # 只保留最近10条
            updated_at=datetime.now()
        )
        
        self.health_statuses[user_id] = status
        
        logger.info(f"心理健康检查完成: user_id={user_id}, risk_level={risk_level}, "
                   f"negative_days={negative_emotion_days}")
        
        return status
    
    def _calculate_risk_level(
        self,
        negative_days: int,
        stability_score: float,
        recent_emotions: List[EmotionState]
    ) -> str:
        """
        计算风险等级
        
        Args:
            negative_days: 连续负面情绪天数
            stability_score: 情绪稳定性得分
            recent_emotions: 最近的情绪记录
            
        Returns:
            str: 风险等级
        """
        # 检查是否有自杀风险或自残关键词
        has_critical_keywords = any(
            keyword in self.NEGATIVE_KEYWORDS['suicide_risk'] + self.NEGATIVE_KEYWORDS['self_harm']
            for emotion in recent_emotions
            for keyword in emotion.detected_keywords
        )
        
        if has_critical_keywords:
            return 'critical'
        
        # 检查严重抑郁
        severe_depression = any(
            emotion.emotion_type == 'depressed' and emotion.intensity > 0.8
            for emotion in recent_emotions
        )
        
        if severe_depression or negative_days >= 7:
            return 'high'
        
        if negative_days >= 3 or stability_score < 0.4:
            return 'medium'
        
        return 'low'
    
    def push_mental_health_resources(
        self,
        user_id: str,
        emotion_type: str
    ) -> List[MentalHealthResource]:
        """
        推送心理健康资源
        
        Args:
            user_id: 用户ID
            emotion_type: 情绪类型
            
        Returns:
            List[MentalHealthResource]: 推送的资源列表
        """
        # 筛选适合的资源
        suitable_resources = [
            resource for resource in self.resources.values()
            if emotion_type in resource.target_emotions
        ]
        
        # 按优先级排序
        suitable_resources.sort(key=lambda r: r.priority, reverse=True)
        
        # 推送资源（最多3个）
        pushed_resources = suitable_resources[:3]
        
        # 记录推送
        for resource in pushed_resources:
            push_record = ResourcePushRecord(
                push_id=str(uuid.uuid4()),
                user_id=user_id,
                resource_id=resource.resource_id,
                push_reason=f"检测到{emotion_type}情绪",
                pushed_at=datetime.now()
            )
            self.push_records[user_id].append(push_record)
        
        logger.info(f"推送心理健康资源: user_id={user_id}, count={len(pushed_resources)}")
        
        return pushed_resources
    
    def create_risk_alert(
        self,
        user_id: str,
        alert_type: str,
        detected_content: str,
        confidence: float
    ) -> RiskAlert:
        """
        创建风险预警
        
        Args:
            user_id: 用户ID
            alert_type: 预警类型
            detected_content: 检测到的内容
            confidence: 置信度
            
        Returns:
            RiskAlert: 风险预警
        """
        # 确定风险等级
        if alert_type in ['suicide_risk', 'self_harm']:
            risk_level = 'critical'
        else:
            risk_level = 'high'
        
        alert = RiskAlert(
            alert_id=str(uuid.uuid4()),
            user_id=user_id,
            risk_level=risk_level,
            alert_type=alert_type,
            detected_content=detected_content,
            confidence=confidence,
            status='pending',
            notified_staff=False,
            created_at=datetime.now()
        )
        
        self.risk_alerts.append(alert)
        
        # 如果是严重风险，立即标记为已通知工作人员
        if risk_level == 'critical':
            alert.notified_staff = True
            logger.warning(f"严重风险预警: user_id={user_id}, type={alert_type}, "
                          f"confidence={confidence:.2f}")
            # 实际应用中应该发送通知给人工客服
        
        logger.info(f"创建风险预警: alert_id={alert.alert_id}, user_id={user_id}, "
                   f"type={alert_type}")
        
        return alert
    
    def create_anonymous_session(self, user_id: str) -> AnonymousSession:
        """
        创建匿名倾诉会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            AnonymousSession: 匿名会话
        """
        # 生成匿名ID
        anonymous_id = f"anonymous_{uuid.uuid4().hex[:8]}"
        
        session = AnonymousSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            anonymous_id=anonymous_id,
            scene="心理树洞",
            is_active=True,
            created_at=datetime.now()
        )
        
        self.anonymous_sessions[session.session_id] = session
        
        logger.info(f"创建匿名会话: session_id={session.session_id}, "
                   f"anonymous_id={anonymous_id}")
        
        return session
    
    def end_anonymous_session(self, session_id: str) -> bool:
        """
        结束匿名倾诉会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功
        """
        if session_id not in self.anonymous_sessions:
            logger.warning(f"匿名会话不存在: session_id={session_id}")
            return False
        
        session = self.anonymous_sessions[session_id]
        session.is_active = False
        session.ended_at = datetime.now()
        
        logger.info(f"结束匿名会话: session_id={session_id}")
        
        return True
    
    def create_professional_referral(
        self,
        user_id: str,
        referral_type: str,
        reason: str,
        urgency: str
    ) -> ProfessionalReferral:
        """
        创建专业资源转介
        
        Args:
            user_id: 用户ID
            referral_type: 转介类型
            reason: 转介原因
            urgency: 紧急程度
            
        Returns:
            ProfessionalReferral: 专业转介
        """
        # 根据紧急程度提供联系方式
        contact_info_map = {
            'emergency': '请立即拨打急救电话120或心理危机热线400-161-9995',
            'high': '请尽快联系校园心理咨询中心或拨打心理援助热线400-161-9995',
            'medium': '建议预约校园心理咨询中心或专业心理咨询师',
            'low': '可以考虑预约校园心理咨询中心进行咨询'
        }
        
        referral = ProfessionalReferral(
            referral_id=str(uuid.uuid4()),
            user_id=user_id,
            referral_type=referral_type,
            reason=reason,
            urgency=urgency,
            contact_info=contact_info_map.get(urgency, contact_info_map['medium']),
            status='pending',
            user_consented=False,
            created_at=datetime.now()
        )
        
        self.referrals.append(referral)
        
        logger.info(f"创建专业转介: referral_id={referral.referral_id}, "
                   f"user_id={user_id}, type={referral_type}, urgency={urgency}")
        
        return referral
    
    def monitor_and_respond(self, user_id: str, text: str, message_id: Optional[str] = None) -> Dict:
        """
        监测并响应用户心理健康状况（综合方法）
        
        Args:
            user_id: 用户ID
            text: 用户文本
            message_id: 消息ID
            
        Returns:
            Dict: 响应结果
        """
        result = {
            'emotion_detected': False,
            'resources_pushed': [],
            'alert_created': False,
            'referral_created': False,
            'anonymous_session_offered': False
        }
        
        # 1. 分析情感
        emotion_request = EmotionAnalysisRequest(
            text=text,
            user_id=user_id,
            message_id=message_id
        )
        emotion_state = self.analyze_emotion(emotion_request)
        result['emotion_detected'] = True
        result['emotion_state'] = emotion_state
        
        # 2. 检查心理健康状态
        health_request = MentalHealthCheckRequest(user_id=user_id, check_recent_days=7)
        health_status = self.check_mental_health(health_request)
        result['health_status'] = health_status
        
        # 3. 根据情况采取行动
        
        # 3.1 检测到自杀风险或自残 - 最高优先级
        if any(kw in self.NEGATIVE_KEYWORDS['suicide_risk'] + self.NEGATIVE_KEYWORDS['self_harm']
               for kw in emotion_state.detected_keywords):
            # 创建严重风险预警
            alert = self.create_risk_alert(
                user_id=user_id,
                alert_type='suicide_risk' if any(kw in self.NEGATIVE_KEYWORDS['suicide_risk'] 
                                                 for kw in emotion_state.detected_keywords) else 'self_harm',
                detected_content=text[:100],
                confidence=emotion_state.intensity
            )
            result['alert_created'] = True
            result['alert'] = alert
            
            # 创建紧急转介
            referral = self.create_professional_referral(
                user_id=user_id,
                referral_type='emergency',
                reason='检测到自杀风险或自残倾向',
                urgency='emergency'
            )
            result['referral_created'] = True
            result['referral'] = referral
            
            # 推送紧急资源
            resources = self.push_mental_health_resources(user_id, 'suicide_risk')
            result['resources_pushed'] = resources
        
        # 3.2 持续低落情绪超过3天
        elif health_status.negative_emotion_days >= 3:
            # 推送心理健康资源
            resources = self.push_mental_health_resources(
                user_id,
                emotion_state.emotion_type
            )
            result['resources_pushed'] = resources
            
            # 如果超过7天，创建转介
            if health_status.negative_emotion_days >= 7:
                referral = self.create_professional_referral(
                    user_id=user_id,
                    referral_type='counseling',
                    reason=f'持续负面情绪{health_status.negative_emotion_days}天',
                    urgency='high'
                )
                result['referral_created'] = True
                result['referral'] = referral
        
        # 3.3 检测到负面情绪关键词
        elif emotion_state.detected_keywords and emotion_state.emotion_type in ['anxious', 'depressed']:
            # 推送相关资源
            resources = self.push_mental_health_resources(
                user_id,
                emotion_state.emotion_type
            )
            result['resources_pushed'] = resources
        
        logger.info(f"心理健康监测完成: user_id={user_id}, "
                   f"emotion={emotion_state.emotion_type}, "
                   f"risk_level={health_status.risk_level}")
        
        return result
    
    def get_user_mental_health_status(self, user_id: str) -> Optional[MentalHealthStatus]:
        """获取用户心理健康状态"""
        return self.health_statuses.get(user_id)
    
    def get_user_push_records(self, user_id: str) -> List[ResourcePushRecord]:
        """获取用户资源推送记录"""
        return self.push_records.get(user_id, [])
    
    def get_pending_alerts(self) -> List[RiskAlert]:
        """获取待处理的风险预警"""
        return [alert for alert in self.risk_alerts if alert.status == 'pending']
    
    def get_user_referrals(self, user_id: str) -> List[ProfessionalReferral]:
        """获取用户的专业转介记录"""
        return [ref for ref in self.referrals if ref.user_id == user_id]

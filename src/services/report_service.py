"""成长报告生成服务"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

from src.models.growth_report import (
    GrowthReport, WeeklyReport, MonthlyReport, AnnualReport,
    ReportGenerationRequest, ReportDownloadRequest, ReportShareRequest, ShareLink
)
from src.models.conversation import Conversation, Message
from src.models.quality import ConversationReport, QualityMetrics
from src.models.mental_health import EmotionState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """报告生成服务"""
    
    def __init__(self):
        """初始化报告服务"""
        # 模拟数据存储
        self.reports: Dict[str, GrowthReport] = {}
        self.share_links: Dict[str, ShareLink] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, List[Message]] = {}
        self.quality_reports: Dict[str, ConversationReport] = {}
        self.emotion_records: Dict[str, List[EmotionState]] = {}
    
    def generate_weekly_report(self, user_id: str) -> WeeklyReport:
        """
        生成周报
        
        Args:
            user_id: 用户ID
            
        Returns:
            WeeklyReport: 周报对象
        """
        logger.info(f"Generating weekly report for user {user_id}")
        
        # 计算时间范围（最近7天）
        period_end = datetime.now()
        period_start = period_end - timedelta(days=7)
        
        # 收集统计数据
        stats = self._collect_statistics(user_id, period_start, period_end)
        
        # 生成成长亮点
        highlights = self._generate_highlights(stats, 'weekly')
        
        # 生成改进建议
        suggestions = self._generate_suggestions(stats, 'weekly')
        
        # 生成可视化数据
        visualization_data = self._generate_visualization_data(stats, 'weekly')
        
        # 创建周报
        report = WeeklyReport(
            report_id=str(uuid.uuid4()),
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            total_conversations=stats['total_conversations'],
            total_messages=stats['total_messages'],
            average_conversation_quality=stats['average_conversation_quality'],
            emotion_health_score=stats['emotion_health_score'],
            social_skill_score=stats['social_skill_score'],
            highlights=highlights,
            suggestions=suggestions,
            visualization_data=visualization_data,
            most_active_day=stats.get('most_active_day'),
            most_active_scene=stats.get('most_active_scene'),
            new_connections=stats.get('new_connections', 0)
        )
        
        # 保存报告
        self.reports[report.report_id] = report
        
        logger.info(f"Weekly report generated: {report.report_id}")
        return report
    
    def generate_monthly_report(self, user_id: str) -> MonthlyReport:
        """
        生成月报
        
        Args:
            user_id: 用户ID
            
        Returns:
            MonthlyReport: 月报对象
        """
        logger.info(f"Generating monthly report for user {user_id}")
        
        # 计算时间范围（最近30天）
        period_end = datetime.now()
        period_start = period_end - timedelta(days=30)
        
        # 收集统计数据
        stats = self._collect_statistics(user_id, period_start, period_end)
        
        # 生成成长亮点
        highlights = self._generate_highlights(stats, 'monthly')
        
        # 生成改进建议
        suggestions = self._generate_suggestions(stats, 'monthly')
        
        # 生成可视化数据
        visualization_data = self._generate_visualization_data(stats, 'monthly')
        
        # 计算趋势数据（按周）
        conversation_quality_trend = self._calculate_weekly_trend(
            user_id, period_start, period_end, 'quality'
        )
        emotion_health_trend = self._calculate_weekly_trend(
            user_id, period_start, period_end, 'emotion'
        )
        
        # 创建月报
        report = MonthlyReport(
            report_id=str(uuid.uuid4()),
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            total_conversations=stats['total_conversations'],
            total_messages=stats['total_messages'],
            average_conversation_quality=stats['average_conversation_quality'],
            emotion_health_score=stats['emotion_health_score'],
            social_skill_score=stats['social_skill_score'],
            highlights=highlights,
            suggestions=suggestions,
            visualization_data=visualization_data,
            conversation_quality_trend=conversation_quality_trend,
            emotion_health_trend=emotion_health_trend,
            top_topics=stats.get('top_topics', []),
            scene_distribution=stats.get('scene_distribution', {})
        )
        
        # 保存报告
        self.reports[report.report_id] = report
        
        logger.info(f"Monthly report generated: {report.report_id}")
        return report
    
    def generate_annual_report(self, user_id: str) -> AnnualReport:
        """
        生成年报
        
        Args:
            user_id: 用户ID
            
        Returns:
            AnnualReport: 年报对象
        """
        logger.info(f"Generating annual report for user {user_id}")
        
        # 计算时间范围（最近365天）
        period_end = datetime.now()
        period_start = period_end - timedelta(days=365)
        
        # 收集统计数据
        stats = self._collect_statistics(user_id, period_start, period_end)
        
        # 生成成长亮点
        highlights = self._generate_highlights(stats, 'annual')
        
        # 生成改进建议
        suggestions = self._generate_suggestions(stats, 'annual')
        
        # 生成可视化数据
        visualization_data = self._generate_visualization_data(stats, 'annual')
        
        # 生成里程碑
        milestones = self._generate_milestones(stats)
        
        # 生成年度总结
        yearly_summary = self._generate_yearly_summary(stats)
        
        # 创建年报
        report = AnnualReport(
            report_id=str(uuid.uuid4()),
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            total_conversations=stats['total_conversations'],
            total_messages=stats['total_messages'],
            average_conversation_quality=stats['average_conversation_quality'],
            emotion_health_score=stats['emotion_health_score'],
            social_skill_score=stats['social_skill_score'],
            highlights=highlights,
            suggestions=suggestions,
            visualization_data=visualization_data,
            milestones=milestones,
            personality_evolution=stats.get('personality_evolution', {}),
            yearly_summary=yearly_summary,
            total_friends=stats.get('total_friends', 0),
            longest_conversation_minutes=stats.get('longest_conversation_minutes', 0.0)
        )
        
        # 保存报告
        self.reports[report.report_id] = report
        
        logger.info(f"Annual report generated: {report.report_id}")
        return report
    
    def get_report(self, report_id: str) -> Optional[GrowthReport]:
        """
        获取报告
        
        Args:
            report_id: 报告ID
            
        Returns:
            Optional[GrowthReport]: 报告对象，如果不存在则返回None
        """
        return self.reports.get(report_id)
    
    def list_user_reports(self, user_id: str, report_type: Optional[str] = None) -> List[GrowthReport]:
        """
        列出用户的所有报告
        
        Args:
            user_id: 用户ID
            report_type: 报告类型过滤（可选）
            
        Returns:
            List[GrowthReport]: 报告列表
        """
        reports = [r for r in self.reports.values() if r.user_id == user_id]
        
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        
        # 按生成时间倒序排序
        reports.sort(key=lambda x: x.generated_at, reverse=True)
        
        return reports
    
    def download_report(self, report_id: str, format: str = 'pdf') -> Dict:
        """
        下载报告
        
        Args:
            report_id: 报告ID
            format: 下载格式（pdf, json, html）
            
        Returns:
            Dict: 包含下载信息的字典
        """
        logger.info(f"Downloading report {report_id} in format {format}")
        
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")
        
        # 根据格式生成下载内容
        if format == 'json':
            content = report.dict()
            content_type = 'application/json'
        elif format == 'html':
            content = self._generate_html_report(report)
            content_type = 'text/html'
        elif format == 'pdf':
            content = self._generate_pdf_report(report)
            content_type = 'application/pdf'
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return {
            'report_id': report_id,
            'format': format,
            'content': content,
            'content_type': content_type,
            'filename': f"growth_report_{report_id}.{format}"
        }
    
    def share_report(self, report_id: str, share_type: str, privacy_level: str = 'friends') -> ShareLink:
        """
        分享报告
        
        Args:
            report_id: 报告ID
            share_type: 分享类型（link, image, social）
            privacy_level: 隐私级别（public, friends, private）
            
        Returns:
            ShareLink: 分享链接对象
        """
        logger.info(f"Sharing report {report_id} as {share_type} with privacy {privacy_level}")
        
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")
        
        # 创建分享链接
        share_id = str(uuid.uuid4())
        share_url = f"https://youth-companion.com/share/{share_id}"
        
        # 设置过期时间（30天）
        expires_at = datetime.now() + timedelta(days=30)
        
        share_link = ShareLink(
            share_id=share_id,
            report_id=report_id,
            user_id=report.user_id,
            share_url=share_url,
            share_type=share_type,
            privacy_level=privacy_level,
            expires_at=expires_at
        )
        
        # 保存分享链接
        self.share_links[share_id] = share_link
        
        logger.info(f"Share link created: {share_url}")
        return share_link
    
    def visualize_growth_data(self, user_id: str) -> Dict:
        """
        可视化用户成长数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 可视化数据
        """
        logger.info(f"Visualizing growth data for user {user_id}")
        
        # 获取最近的报告
        reports = self.list_user_reports(user_id)
        if not reports:
            return {}
        
        latest_report = reports[0]
        return latest_report.visualization_data
    
    def _collect_statistics(self, user_id: str, period_start: datetime, period_end: datetime) -> Dict:
        """
        收集统计数据
        
        Args:
            user_id: 用户ID
            period_start: 开始时间
            period_end: 结束时间
            
        Returns:
            Dict: 统计数据
        """
        # 筛选时间范围内的对话
        user_conversations = [
            conv for conv in self.conversations.values()
            if (conv.user_a_id == user_id or conv.user_b_id == user_id)
            and period_start <= conv.started_at <= period_end
        ]
        
        total_conversations = len(user_conversations)
        
        # 计算消息总数
        total_messages = sum(conv.message_count for conv in user_conversations)
        
        # 计算平均对话质量
        quality_scores = [
            conv.topic_depth_score for conv in user_conversations
            if conv.topic_depth_score is not None
        ]
        average_conversation_quality = statistics.mean(quality_scores) if quality_scores else 5.0
        
        # 计算情绪健康得分（基于情绪记录）
        emotion_health_score = self._calculate_emotion_health_score(user_id, period_start, period_end)
        
        # 计算社交能力得分
        social_skill_score = self._calculate_social_skill_score(user_conversations)
        
        # 统计最活跃的一天
        day_counts = {}
        for conv in user_conversations:
            day = conv.started_at.strftime('%Y-%m-%d')
            day_counts[day] = day_counts.get(day, 0) + 1
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        
        # 统计最活跃的场景
        scene_counts = {}
        for conv in user_conversations:
            scene_counts[conv.scene] = scene_counts.get(conv.scene, 0) + 1
        most_active_scene = max(scene_counts.items(), key=lambda x: x[1])[0] if scene_counts else None
        
        # 统计新建立的连接
        unique_partners = set()
        for conv in user_conversations:
            partner_id = conv.user_b_id if conv.user_a_id == user_id else conv.user_a_id
            unique_partners.add(partner_id)
        new_connections = len(unique_partners)
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'average_conversation_quality': average_conversation_quality,
            'emotion_health_score': emotion_health_score,
            'social_skill_score': social_skill_score,
            'most_active_day': most_active_day,
            'most_active_scene': most_active_scene,
            'new_connections': new_connections,
            'scene_distribution': scene_counts,
            'top_topics': self._extract_top_topics(user_conversations),
            'total_friends': new_connections,
            'longest_conversation_minutes': self._calculate_longest_conversation(user_conversations),
            'personality_evolution': {}
        }
    
    def _calculate_emotion_health_score(self, user_id: str, period_start: datetime, period_end: datetime) -> float:
        """
        计算情绪健康得分
        
        Args:
            user_id: 用户ID
            period_start: 开始时间
            period_end: 结束时间
            
        Returns:
            float: 情绪健康得分（0-10）
        """
        # 获取用户的情绪记录
        user_emotions = self.emotion_records.get(user_id, [])
        
        # 筛选时间范围内的记录
        period_emotions = [
            e for e in user_emotions
            if period_start <= e.timestamp <= period_end
        ]
        
        if not period_emotions:
            return 7.0  # 默认中等偏上
        
        # 计算正面情绪比例
        positive_count = sum(1 for e in period_emotions if e.emotion_type == 'positive')
        negative_count = sum(1 for e in period_emotions if e.emotion_type == 'negative')
        total_count = len(period_emotions)
        
        positive_ratio = positive_count / total_count if total_count > 0 else 0.5
        
        # 转换为0-10分
        score = positive_ratio * 10
        
        # 如果有持续负面情绪，降低分数
        if negative_count > total_count * 0.5:
            score *= 0.7
        
        return round(score, 2)
    
    def _calculate_social_skill_score(self, conversations: List[Conversation]) -> float:
        """
        计算社交能力得分
        
        Args:
            conversations: 对话列表
            
        Returns:
            float: 社交能力得分（0-10）
        """
        if not conversations:
            return 5.0  # 默认中等
        
        # 基于对话质量和数量计算
        quality_scores = [
            conv.topic_depth_score for conv in conversations
            if conv.topic_depth_score is not None
        ]
        
        avg_quality = statistics.mean(quality_scores) if quality_scores else 5.0
        
        # 对话数量因子（越多越好，但有上限）
        conversation_factor = min(len(conversations) / 10, 1.0)
        
        # 综合得分
        score = avg_quality * 0.7 + conversation_factor * 3.0
        
        return round(min(score, 10.0), 2)
    
    def _calculate_longest_conversation(self, conversations: List[Conversation]) -> float:
        """
        计算最长对话时长
        
        Args:
            conversations: 对话列表
            
        Returns:
            float: 最长对话时长（分钟）
        """
        if not conversations:
            return 0.0
        
        max_duration = 0.0
        for conv in conversations:
            if conv.ended_at and conv.started_at:
                duration = (conv.ended_at - conv.started_at).total_seconds() / 60
                max_duration = max(max_duration, duration)
        
        return round(max_duration, 2)
    
    def _extract_top_topics(self, conversations: List[Conversation]) -> List[str]:
        """
        提取热门话题
        
        Args:
            conversations: 对话列表
            
        Returns:
            List[str]: 热门话题列表
        """
        # 简化实现：基于场景统计
        scene_counts = {}
        for conv in conversations:
            scene_counts[conv.scene] = scene_counts.get(conv.scene, 0) + 1
        
        # 返回前3个热门场景
        sorted_scenes = sorted(scene_counts.items(), key=lambda x: x[1], reverse=True)
        return [scene for scene, _ in sorted_scenes[:3]]
    
    def _calculate_weekly_trend(self, user_id: str, period_start: datetime, period_end: datetime, metric_type: str) -> List[float]:
        """
        计算周度趋势
        
        Args:
            user_id: 用户ID
            period_start: 开始时间
            period_end: 结束时间
            metric_type: 指标类型（quality或emotion）
            
        Returns:
            List[float]: 周度趋势数据
        """
        weeks = []
        current = period_start
        
        while current < period_end:
            week_end = min(current + timedelta(days=7), period_end)
            
            # 计算该周的指标
            if metric_type == 'quality':
                week_stats = self._collect_statistics(user_id, current, week_end)
                weeks.append(week_stats['average_conversation_quality'])
            elif metric_type == 'emotion':
                score = self._calculate_emotion_health_score(user_id, current, week_end)
                weeks.append(score)
            
            current = week_end
        
        return weeks
    
    def _generate_highlights(self, stats: Dict, report_type: str) -> List[str]:
        """
        生成成长亮点
        
        Args:
            stats: 统计数据
            report_type: 报告类型
            
        Returns:
            List[str]: 成长亮点列表
        """
        highlights = []
        
        # 对话数量亮点
        if stats['total_conversations'] > 10:
            highlights.append(f"完成了{stats['total_conversations']}次深度对话，社交活跃度很高！")
        elif stats['total_conversations'] > 5:
            highlights.append(f"完成了{stats['total_conversations']}次对话，保持了良好的社交节奏")
        
        # 对话质量亮点
        if stats['average_conversation_quality'] >= 7.0:
            highlights.append(f"对话质量平均达到{stats['average_conversation_quality']:.1f}分，交流效果出色！")
        
        # 情绪健康亮点
        if stats['emotion_health_score'] >= 7.5:
            highlights.append(f"情绪健康得分{stats['emotion_health_score']:.1f}分，心理状态积极向上")
        
        # 社交能力亮点
        if stats['social_skill_score'] >= 7.0:
            highlights.append(f"社交能力得分{stats['social_skill_score']:.1f}分，沟通技巧不断提升")
        
        # 新连接亮点
        if stats.get('new_connections', 0) > 5:
            highlights.append(f"结识了{stats['new_connections']}位新伙伴，社交圈持续扩大")
        
        return highlights
    
    def _generate_suggestions(self, stats: Dict, report_type: str) -> List[str]:
        """
        生成改进建议
        
        Args:
            stats: 统计数据
            report_type: 报告类型
            
        Returns:
            List[str]: 改进建议列表
        """
        suggestions = []
        
        # 对话数量建议
        if stats['total_conversations'] < 3:
            suggestions.append("尝试增加对话频率，每周至少进行3-5次深度交流")
        
        # 对话质量建议
        if stats['average_conversation_quality'] < 6.0:
            suggestions.append("可以尝试更深入的话题，提升对话质量和深度")
        
        # 情绪健康建议
        if stats['emotion_health_score'] < 6.0:
            suggestions.append("注意情绪调节，必要时可以寻求心理支持")
        
        # 场景多样性建议
        scene_count = len(stats.get('scene_distribution', {}))
        if scene_count < 2:
            suggestions.append("尝试探索不同的社交场景，丰富社交体验")
        
        # 社交能力建议
        if stats['social_skill_score'] < 6.0:
            suggestions.append("多参与对话，积累社交经验，提升沟通技巧")
        
        return suggestions
    
    def _generate_visualization_data(self, stats: Dict, report_type: str) -> Dict:
        """
        生成可视化数据
        
        Args:
            stats: 统计数据
            report_type: 报告类型
            
        Returns:
            Dict: 可视化数据
        """
        visualization = {
            'conversation_count': stats['total_conversations'],
            'message_count': stats['total_messages'],
            'quality_score': stats['average_conversation_quality'],
            'emotion_score': stats['emotion_health_score'],
            'social_skill_score': stats['social_skill_score'],
            'scene_distribution': stats.get('scene_distribution', {}),
            'chart_type': 'bar' if report_type == 'weekly' else 'line'
        }
        
        return visualization
    
    def _generate_milestones(self, stats: Dict) -> List[str]:
        """
        生成成就里程碑
        
        Args:
            stats: 统计数据
            
        Returns:
            List[str]: 里程碑列表
        """
        milestones = []
        
        # 对话数量里程碑
        if stats['total_conversations'] >= 100:
            milestones.append("🎉 完成100次对话里程碑")
        elif stats['total_conversations'] >= 50:
            milestones.append("🎊 达成50次对话成就")
        
        # 好友数量里程碑
        if stats.get('total_friends', 0) >= 20:
            milestones.append("👥 结识20位成长伙伴")
        
        # 对话质量里程碑
        if stats['average_conversation_quality'] >= 8.0:
            milestones.append("⭐ 对话质量达到优秀水平")
        
        # 情绪健康里程碑
        if stats['emotion_health_score'] >= 8.5:
            milestones.append("😊 保持积极心态全年")
        
        return milestones
    
    def _generate_yearly_summary(self, stats: Dict) -> str:
        """
        生成年度总结
        
        Args:
            stats: 统计数据
            
        Returns:
            str: 年度总结文本
        """
        summary = f"""
        这一年，你在青春伴行平台上完成了{stats['total_conversations']}次深度对话，
        发送了{stats['total_messages']}条消息，结识了{stats.get('total_friends', 0)}位成长伙伴。
        你的对话质量平均达到{stats['average_conversation_quality']:.1f}分，
        情绪健康得分{stats['emotion_health_score']:.1f}分，
        社交能力得分{stats['social_skill_score']:.1f}分。
        这是充实而有意义的一年，期待你在新的一年继续成长！
        """
        return summary.strip()
    
    def _generate_html_report(self, report: GrowthReport) -> str:
        """
        生成HTML格式报告
        
        Args:
            report: 报告对象
            
        Returns:
            str: HTML内容
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>成长报告 - {report.report_type}</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>成长报告</h1>
            <p>报告类型: {report.report_type}</p>
            <p>统计周期: {report.period_start.strftime('%Y-%m-%d')} 至 {report.period_end.strftime('%Y-%m-%d')}</p>
            <h2>统计数据</h2>
            <ul>
                <li>对话总数: {report.total_conversations}</li>
                <li>消息总数: {report.total_messages}</li>
                <li>平均对话质量: {report.average_conversation_quality:.1f}</li>
                <li>情绪健康得分: {report.emotion_health_score:.1f}</li>
                <li>社交能力得分: {report.social_skill_score:.1f}</li>
            </ul>
            <h2>成长亮点</h2>
            <ul>
                {''.join(f'<li>{h}</li>' for h in report.highlights)}
            </ul>
            <h2>改进建议</h2>
            <ul>
                {''.join(f'<li>{s}</li>' for s in report.suggestions)}
            </ul>
        </body>
        </html>
        """
        return html
    
    def _generate_pdf_report(self, report: GrowthReport) -> bytes:
        """
        生成PDF格式报告
        
        Args:
            report: 报告对象
            
        Returns:
            bytes: PDF内容（模拟）
        """
        # 实际实现需要使用PDF生成库（如reportlab）
        # 这里返回模拟数据
        return b"PDF content placeholder"

    def get_user_reports(
        self,
        user_id: str,
        report_type: Optional[str] = None,
        limit: int = 10
    ) -> List[GrowthReport]:
        """
        获取用户的报告列表
        
        Args:
            user_id: 用户ID
            report_type: 报告类型过滤
            limit: 返回数量限制
            
        Returns:
            List[GrowthReport]: 报告列表
        """
        user_reports = [
            report for report in self._reports.values()
            if report.user_id == user_id
        ]
        
        # 类型过滤
        if report_type:
            user_reports = [
                report for report in user_reports
                if report.report_type == report_type
            ]
        
        # 按生成时间倒序排序
        user_reports.sort(key=lambda x: x.generated_at, reverse=True)
        
        return user_reports[:limit]
    
    def get_report(self, report_id: str) -> GrowthReport:
        """
        获取报告详情
        
        Args:
            report_id: 报告ID
            
        Returns:
            GrowthReport: 报告对象
        """
        if report_id not in self._reports:
            raise NotFoundError(f"Report not found: {report_id}")
        
        return self._reports[report_id]
    
    def export_report(self, report_id: str, format: str) -> str:
        """
        导出报告文件
        
        Args:
            report_id: 报告ID
            format: 导出格式 (pdf, json)
            
        Returns:
            str: 文件路径
        """
        report = self.get_report(report_id)
        
        if format not in ['pdf', 'json']:
            raise ValidationError(f"Unsupported format: {format}")
        
        # 简化版本：返回模拟的文件路径
        # 实际应该生成真实的文件
        file_path = f"/tmp/report_{report_id}.{format}"
        
        self.logger.info(f"Exported report {report_id} to {file_path}")
        
        return file_path
    
    def create_share_link(self, report_id: str) -> str:
        """
        创建报告分享链接
        
        Args:
            report_id: 报告ID
            
        Returns:
            str: 分享链接
        """
        report = self.get_report(report_id)
        
        # 生成分享令牌
        share_token = str(uuid.uuid4())
        
        # 构建分享链接
        share_link = f"https://youth-companion.com/reports/share/{share_token}"
        
        self.logger.info(f"Created share link for report {report_id}")
        
        return share_link
    
    def get_latest_report(self, user_id: str, report_type: str) -> GrowthReport:
        """
        获取最新报告
        
        Args:
            user_id: 用户ID
            report_type: 报告类型
            
        Returns:
            GrowthReport: 最新报告
        """
        reports = self.get_user_reports(user_id, report_type, limit=1)
        
        if not reports:
            raise NotFoundError(f"No {report_type} report found for user {user_id}")
        
        return reports[0]

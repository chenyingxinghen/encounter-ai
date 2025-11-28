"""成长报告功能测试"""
import pytest
from datetime import datetime, timedelta
import uuid

from src.services.report_service import ReportService
from src.models.growth_report import (
    WeeklyReport, MonthlyReport, AnnualReport,
    ReportGenerationRequest, ReportDownloadRequest, ReportShareRequest
)
from src.models.conversation import Conversation
from src.models.mental_health import EmotionState


@pytest.fixture
def report_service():
    """创建报告服务实例"""
    return ReportService()


@pytest.fixture
def sample_user_id():
    """创建示例用户ID"""
    return "test_user_001"


@pytest.fixture
def setup_test_data(report_service, sample_user_id):
    """设置测试数据"""
    # 创建对话数据
    for i in range(15):
        conv = Conversation(
            conversation_id=str(uuid.uuid4()),
            user_a_id=sample_user_id,
            user_b_id=f"user_{i+2:03d}",
            scene="考研自习室" if i % 2 == 0 else "兴趣社群",
            status="ended",
            started_at=datetime.now() - timedelta(days=i * 2),
            ended_at=datetime.now() - timedelta(days=i * 2, hours=-2),
            message_count=25 + i * 3,
            topic_depth_score=5.5 + i * 0.2,
            emotion_sync_score=0.65 + i * 0.015
        )
        report_service.conversations[conv.conversation_id] = conv
    
    # 创建情绪记录
    for i in range(30):
        emotion = EmotionState(
            user_id=sample_user_id,
            emotion_type="positive" if i % 4 != 0 else "negative",
            intensity=0.5 + (i % 6) * 0.08,
            detected_keywords=["学习", "成长"] if i % 4 != 0 else ["压力"],
            timestamp=datetime.now() - timedelta(days=i)
        )
        if sample_user_id not in report_service.emotion_records:
            report_service.emotion_records[sample_user_id] = []
        report_service.emotion_records[sample_user_id].append(emotion)
    
    return report_service


class TestWeeklyReport:
    """周报测试"""
    
    def test_generate_weekly_report(self, setup_test_data, sample_user_id):
        """测试生成周报"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        assert isinstance(report, WeeklyReport)
        assert report.report_type == "weekly"
        assert report.user_id == sample_user_id
        assert report.total_conversations >= 0
        assert report.total_messages >= 0
        assert 0 <= report.average_conversation_quality <= 10
        assert 0 <= report.emotion_health_score <= 10
        assert 0 <= report.social_skill_score <= 10
        assert report.new_connections >= 0
        assert isinstance(report.highlights, list)
        assert isinstance(report.suggestions, list)
        assert isinstance(report.visualization_data, dict)
    
    def test_weekly_report_time_range(self, setup_test_data, sample_user_id):
        """测试周报时间范围"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 验证时间范围为7天
        time_diff = report.period_end - report.period_start
        assert time_diff.days == 7
    
    def test_weekly_report_fields(self, setup_test_data, sample_user_id):
        """测试周报特定字段"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 周报特定字段
        assert hasattr(report, 'most_active_day')
        assert hasattr(report, 'most_active_scene')
        assert hasattr(report, 'new_connections')


class TestMonthlyReport:
    """月报测试"""
    
    def test_generate_monthly_report(self, setup_test_data, sample_user_id):
        """测试生成月报"""
        report_service = setup_test_data
        
        report = report_service.generate_monthly_report(sample_user_id)
        
        assert isinstance(report, MonthlyReport)
        assert report.report_type == "monthly"
        assert report.user_id == sample_user_id
        assert report.total_conversations >= 0
        assert isinstance(report.conversation_quality_trend, list)
        assert isinstance(report.emotion_health_trend, list)
        assert isinstance(report.top_topics, list)
        assert isinstance(report.scene_distribution, dict)
    
    def test_monthly_report_time_range(self, setup_test_data, sample_user_id):
        """测试月报时间范围"""
        report_service = setup_test_data
        
        report = report_service.generate_monthly_report(sample_user_id)
        
        # 验证时间范围为30天
        time_diff = report.period_end - report.period_start
        assert time_diff.days == 30
    
    def test_monthly_report_trends(self, setup_test_data, sample_user_id):
        """测试月报趋势数据"""
        report_service = setup_test_data
        
        report = report_service.generate_monthly_report(sample_user_id)
        
        # 趋势数据应该是列表
        assert isinstance(report.conversation_quality_trend, list)
        assert isinstance(report.emotion_health_trend, list)
        
        # 趋势数据中的值应该在合理范围内
        for score in report.conversation_quality_trend:
            assert 0 <= score <= 10
        
        for score in report.emotion_health_trend:
            assert 0 <= score <= 10


class TestAnnualReport:
    """年报测试"""
    
    def test_generate_annual_report(self, setup_test_data, sample_user_id):
        """测试生成年报"""
        report_service = setup_test_data
        
        report = report_service.generate_annual_report(sample_user_id)
        
        assert isinstance(report, AnnualReport)
        assert report.report_type == "annual"
        assert report.user_id == sample_user_id
        assert isinstance(report.milestones, list)
        assert isinstance(report.personality_evolution, dict)
        assert isinstance(report.yearly_summary, str)
        assert report.total_friends >= 0
        assert report.longest_conversation_minutes >= 0
    
    def test_annual_report_time_range(self, setup_test_data, sample_user_id):
        """测试年报时间范围"""
        report_service = setup_test_data
        
        report = report_service.generate_annual_report(sample_user_id)
        
        # 验证时间范围为365天
        time_diff = report.period_end - report.period_start
        assert time_diff.days == 365
    
    def test_annual_report_summary(self, setup_test_data, sample_user_id):
        """测试年报总结"""
        report_service = setup_test_data
        
        report = report_service.generate_annual_report(sample_user_id)
        
        # 年度总结应该包含关键信息
        assert len(report.yearly_summary) > 0
        assert isinstance(report.milestones, list)


class TestReportManagement:
    """报告管理测试"""
    
    def test_get_report(self, setup_test_data, sample_user_id):
        """测试获取报告"""
        report_service = setup_test_data
        
        # 生成报告
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 获取报告
        retrieved_report = report_service.get_report(report.report_id)
        
        assert retrieved_report is not None
        assert retrieved_report.report_id == report.report_id
        assert retrieved_report.user_id == sample_user_id
    
    def test_get_nonexistent_report(self, report_service):
        """测试获取不存在的报告"""
        result = report_service.get_report("nonexistent_id")
        assert result is None
    
    def test_list_user_reports(self, setup_test_data, sample_user_id):
        """测试列出用户报告"""
        report_service = setup_test_data
        
        # 生成多个报告
        report_service.generate_weekly_report(sample_user_id)
        report_service.generate_monthly_report(sample_user_id)
        report_service.generate_annual_report(sample_user_id)
        
        # 列出所有报告
        reports = report_service.list_user_reports(sample_user_id)
        
        assert len(reports) == 3
        assert all(r.user_id == sample_user_id for r in reports)
    
    def test_list_user_reports_by_type(self, setup_test_data, sample_user_id):
        """测试按类型列出用户报告"""
        report_service = setup_test_data
        
        # 生成多个报告
        report_service.generate_weekly_report(sample_user_id)
        report_service.generate_weekly_report(sample_user_id)
        report_service.generate_monthly_report(sample_user_id)
        
        # 只列出周报
        weekly_reports = report_service.list_user_reports(sample_user_id, report_type='weekly')
        
        assert len(weekly_reports) == 2
        assert all(r.report_type == 'weekly' for r in weekly_reports)


class TestReportDownload:
    """报告下载测试"""
    
    def test_download_report_json(self, setup_test_data, sample_user_id):
        """测试下载JSON格式报告"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        download_info = report_service.download_report(report.report_id, format='json')
        
        assert download_info['report_id'] == report.report_id
        assert download_info['format'] == 'json'
        assert download_info['content_type'] == 'application/json'
        assert 'filename' in download_info
        assert download_info['filename'].endswith('.json')
    
    def test_download_report_html(self, setup_test_data, sample_user_id):
        """测试下载HTML格式报告"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        download_info = report_service.download_report(report.report_id, format='html')
        
        assert download_info['format'] == 'html'
        assert download_info['content_type'] == 'text/html'
        assert download_info['filename'].endswith('.html')
        assert isinstance(download_info['content'], str)
        assert '<html>' in download_info['content']
    
    def test_download_report_pdf(self, setup_test_data, sample_user_id):
        """测试下载PDF格式报告"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        download_info = report_service.download_report(report.report_id, format='pdf')
        
        assert download_info['format'] == 'pdf'
        assert download_info['content_type'] == 'application/pdf'
        assert download_info['filename'].endswith('.pdf')
    
    def test_download_nonexistent_report(self, report_service):
        """测试下载不存在的报告"""
        with pytest.raises(ValueError, match="Report not found"):
            report_service.download_report("nonexistent_id", format='json')
    
    def test_download_invalid_format(self, setup_test_data, sample_user_id):
        """测试下载无效格式"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        with pytest.raises(ValueError, match="Unsupported format"):
            report_service.download_report(report.report_id, format='invalid')


class TestReportSharing:
    """报告分享测试"""
    
    def test_share_report_link(self, setup_test_data, sample_user_id):
        """测试分享报告链接"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        share_link = report_service.share_report(
            report.report_id,
            share_type='link',
            privacy_level='friends'
        )
        
        assert share_link.report_id == report.report_id
        assert share_link.user_id == sample_user_id
        assert share_link.share_type == 'link'
        assert share_link.privacy_level == 'friends'
        assert share_link.share_url.startswith('https://')
        assert share_link.expires_at is not None
        assert share_link.view_count == 0
    
    def test_share_report_different_types(self, setup_test_data, sample_user_id):
        """测试不同类型的分享"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 测试不同分享类型
        for share_type in ['link', 'image', 'social']:
            share_link = report_service.share_report(
                report.report_id,
                share_type=share_type,
                privacy_level='public'
            )
            assert share_link.share_type == share_type
    
    def test_share_report_privacy_levels(self, setup_test_data, sample_user_id):
        """测试不同隐私级别的分享"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 测试不同隐私级别
        for privacy_level in ['public', 'friends', 'private']:
            share_link = report_service.share_report(
                report.report_id,
                share_type='link',
                privacy_level=privacy_level
            )
            assert share_link.privacy_level == privacy_level
    
    def test_share_nonexistent_report(self, report_service):
        """测试分享不存在的报告"""
        with pytest.raises(ValueError, match="Report not found"):
            report_service.share_report(
                "nonexistent_id",
                share_type='link',
                privacy_level='friends'
            )


class TestVisualization:
    """可视化测试"""
    
    def test_visualize_growth_data(self, setup_test_data, sample_user_id):
        """测试可视化成长数据"""
        report_service = setup_test_data
        
        # 生成报告
        report_service.generate_weekly_report(sample_user_id)
        
        # 获取可视化数据
        viz_data = report_service.visualize_growth_data(sample_user_id)
        
        assert isinstance(viz_data, dict)
        assert 'conversation_count' in viz_data
        assert 'message_count' in viz_data
        assert 'quality_score' in viz_data
        assert 'emotion_score' in viz_data
        assert 'social_skill_score' in viz_data
    
    def test_visualize_no_reports(self, report_service, sample_user_id):
        """测试没有报告时的可视化"""
        viz_data = report_service.visualize_growth_data(sample_user_id)
        
        assert viz_data == {}


class TestReportContent:
    """报告内容测试"""
    
    def test_report_highlights_generation(self, setup_test_data, sample_user_id):
        """测试成长亮点生成"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        assert isinstance(report.highlights, list)
        # 亮点列表应该是列表类型（可能为空，取决于数据）
        assert len(report.highlights) >= 0
    
    def test_report_suggestions_generation(self, setup_test_data, sample_user_id):
        """测试改进建议生成"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        assert isinstance(report.suggestions, list)
        # 建议可能为空或有内容
        assert len(report.suggestions) >= 0
    
    def test_report_visualization_data(self, setup_test_data, sample_user_id):
        """测试可视化数据生成"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        assert isinstance(report.visualization_data, dict)
        assert 'conversation_count' in report.visualization_data
        assert 'quality_score' in report.visualization_data


class TestReportValidation:
    """报告验证测试"""
    
    def test_report_id_uniqueness(self, setup_test_data, sample_user_id):
        """测试报告ID唯一性"""
        report_service = setup_test_data
        
        report1 = report_service.generate_weekly_report(sample_user_id)
        report2 = report_service.generate_weekly_report(sample_user_id)
        
        assert report1.report_id != report2.report_id
    
    def test_report_timestamp(self, setup_test_data, sample_user_id):
        """测试报告时间戳"""
        report_service = setup_test_data
        
        before = datetime.now()
        report = report_service.generate_weekly_report(sample_user_id)
        after = datetime.now()
        
        assert before <= report.generated_at <= after
    
    def test_report_score_ranges(self, setup_test_data, sample_user_id):
        """测试报告分数范围"""
        report_service = setup_test_data
        
        report = report_service.generate_weekly_report(sample_user_id)
        
        # 所有分数应该在0-10范围内
        assert 0 <= report.average_conversation_quality <= 10
        assert 0 <= report.emotion_health_score <= 10
        assert 0 <= report.social_skill_score <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

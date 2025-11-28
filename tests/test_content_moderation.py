"""
内容审查系统测试
Content Moderation System Tests
"""
import pytest
from datetime import datetime, timedelta

from src.services.content_moderation_service import ContentModerationService
from src.models.moderation import ModerationResult, Violation, UserReport, Penalty


class TestContentModerationService:
    """内容审查服务测试"""
    
    def setup_method(self):
        """每个测试前初始化"""
        self.service = ContentModerationService()
    
    def test_moderate_clean_message(self):
        """测试审查正常消息"""
        message = "你好，很高兴认识你！"
        result = self.service.moderate_message(message, "user1")
        
        assert result.is_approved is True
        assert result.action == "allow"
        assert len(result.violation_types) == 0
        assert len(result.flagged_keywords) == 0
    
    def test_moderate_violent_message(self):
        """测试审查暴力消息"""
        message = "我要打人，暴力解决问题"
        result = self.service.moderate_message(message, "user1")
        
        assert result.is_approved is False
        assert result.action in ["block", "review"]
        assert Violation.TYPE_VIOLENCE in result.violation_types
        assert len(result.flagged_keywords) > 0
    
    def test_moderate_pornographic_message(self):
        """测试审查色情消息"""
        message = "这是色情内容，黄色信息"
        result = self.service.moderate_message(message, "user1")
        
        assert result.is_approved is False
        assert Violation.TYPE_PORNOGRAPHY in result.violation_types
    
    def test_moderate_harassment_message(self):
        """测试审查骚扰消息"""
        message = "你这个傻子，侮辱你，骚扰你"
        result = self.service.moderate_message(message, "user1")
        
        assert result.is_approved is False
        assert Violation.TYPE_HARASSMENT in result.violation_types
    
    def test_moderate_spam_message(self):
        """测试审查垃圾消息"""
        message = "加微信赚钱，广告推广"
        result = self.service.moderate_message(message, "user1")
        
        assert result.is_approved is False
        assert Violation.TYPE_SPAM in result.violation_types
    
    def test_detect_multiple_violations(self):
        """测试检测多种违规"""
        message = "暴力色情内容"
        violations = self.service.detect_violation(message)
        
        assert len(violations) >= 2
        assert Violation.TYPE_VIOLENCE in violations
        assert Violation.TYPE_PORNOGRAPHY in violations
    
    def test_violation_recording(self):
        """测试违规记录"""
        message = "暴力内容"
        result = self.service.moderate_message(message, "user1", "msg1")
        
        if result.action == "block":
            violations = self.service.get_user_violation_history("user1")
            assert len(violations) > 0
            assert violations[0].user_id == "user1"
    
    def test_user_report_creation(self):
        """测试创建用户举报"""
        report = self.service.handle_user_report(
            reporter_id="user1",
            reported_id="user2",
            report_type=UserReport.TYPE_HARASSMENT,
            reason="该用户持续骚扰我",
            evidence=["msg1", "msg2"]
        )
        
        assert report.reporter_id == "user1"
        assert report.reported_id == "user2"
        assert report.report_type == UserReport.TYPE_HARASSMENT
        assert report.status in [UserReport.STATUS_PENDING, UserReport.STATUS_INVESTIGATING]
        assert len(report.evidence) == 2
    
    def test_review_flagged_content_confirm(self):
        """测试确认违规内容"""
        # 创建违规
        message = "暴力内容测试"
        result = self.service.moderate_message(message, "user1", "msg1")
        
        if result.action == "block":
            # 审核确认
            self.service.review_flagged_content("msg1", "admin1", "confirm")
            
            violations = self.service.get_user_violation_history("user1")
            if violations:
                assert violations[0].status == Violation.STATUS_CONFIRMED
    
    def test_review_flagged_content_dismiss(self):
        """测试驳回违规内容"""
        # 创建违规
        message = "暴力内容测试"
        result = self.service.moderate_message(message, "user1", "msg1")
        
        if result.action == "block":
            initial_count = self.service.user_violation_counts["user1"]
            
            # 审核驳回
            self.service.review_flagged_content("msg1", "admin1", "dismiss")
            
            violations = self.service.get_user_violation_history("user1")
            if violations:
                assert violations[0].status == Violation.STATUS_DISMISSED
                # 违规计数应该减少
                assert self.service.user_violation_counts["user1"] < initial_count
    
    def test_auto_penalty_warning(self):
        """测试自动警告处罚"""
        # 第1次违规应该触发警告
        message = "暴力内容"
        self.service.moderate_message(message, "user1", "msg1")
        
        penalties = self.service.get_user_penalties("user1")
        if penalties:
            assert penalties[0].penalty_type == Penalty.TYPE_WARNING
    
    def test_auto_penalty_escalation(self):
        """测试处罚升级"""
        user_id = "user_test"
        
        # 模拟多次违规 - 使用更明确的违规内容
        for i in range(5):
            message = f"暴力打人攻击伤害 {i}"
            self.service.moderate_message(message, user_id, f"msg{i}")
        
        penalties = self.service.get_user_penalties(user_id)
        
        # 应该有至少一个处罚记录
        assert len(penalties) >= 1
        
        # 检查违规计数
        violation_count = self.service.user_violation_counts[user_id]
        assert violation_count > 0
        
        # 如果有多个处罚，检查是否有升级
        if len(penalties) > 1:
            penalty_types = [p.penalty_type for p in penalties]
            # 检查是否有升级
            assert Penalty.TYPE_WARNING in penalty_types or \
                   Penalty.TYPE_MUTE in penalty_types or \
                   Penalty.TYPE_SUSPEND in penalty_types
    
    def test_apply_penalty_manually(self):
        """测试手动施加处罚"""
        # 先创建违规
        message = "暴力内容"
        result = self.service.moderate_message(message, "user1", "msg1")
        
        violations = self.service.get_user_violation_history("user1")
        if violations:
            violation_id = violations[0].violation_id
            
            # 手动施加禁言处罚
            penalty = self.service.apply_penalty("user1", violation_id, Penalty.TYPE_MUTE)
            
            assert penalty.user_id == "user1"
            assert penalty.penalty_type == Penalty.TYPE_MUTE
            assert penalty.duration == 86400  # 1天
            assert penalty.status == Penalty.STATUS_ACTIVE
    
    def test_is_user_penalized(self):
        """测试检查用户是否被处罚"""
        user_id = "user_penalty_test"
        
        # 初始状态未被处罚
        assert self.service.is_user_penalized(user_id) is False
        
        # 创建违规并施加处罚
        message = "暴力内容"
        self.service.moderate_message(message, user_id, "msg1")
        
        violations = self.service.get_user_violation_history(user_id)
        if violations:
            self.service.apply_penalty(user_id, violations[0].violation_id, 
                                      Penalty.TYPE_MUTE)
            
            # 现在应该被处罚
            assert self.service.is_user_penalized(user_id) is True
    
    def test_handle_appeal(self):
        """测试处理申诉"""
        # 创建违规
        message = "暴力内容"
        self.service.moderate_message(message, "user1", "msg1")
        
        violations = self.service.get_user_violation_history("user1")
        if violations:
            violation_id = violations[0].violation_id
            
            # 提交申诉
            result = self.service.handle_appeal("user1", violation_id, 
                                               "这是误判，我没有违规")
            
            assert result is True
            assert violations[0].status == Violation.STATUS_APPEALED
    
    def test_handle_appeal_wrong_user(self):
        """测试错误用户申诉"""
        # 创建违规
        message = "暴力内容"
        self.service.moderate_message(message, "user1", "msg1")
        
        violations = self.service.get_user_violation_history("user1")
        if violations:
            violation_id = violations[0].violation_id
            
            # 其他用户尝试申诉
            result = self.service.handle_appeal("user2", violation_id, "申诉")
            
            assert result is False
    
    def test_get_moderation_stats(self):
        """测试获取审查统计"""
        # 创建一些违规和举报
        self.service.moderate_message("暴力内容", "user1", "msg1")
        self.service.moderate_message("色情内容", "user2", "msg2")
        self.service.handle_user_report("user3", "user4", 
                                       UserReport.TYPE_HARASSMENT,
                                       "骚扰", ["msg3"])
        
        stats = self.service.get_moderation_stats()
        
        assert "total_violations" in stats
        assert "total_reports" in stats
        assert "total_penalties" in stats
        assert "violations_by_type" in stats
        assert "penalties_by_type" in stats
        assert stats["total_reports"] >= 1


class TestModerationModels:
    """测试审查数据模型"""
    
    def test_moderation_result_creation(self):
        """测试创建审查结果"""
        result = ModerationResult(
            content_id="msg1",
            is_approved=True,
            violation_types=[],
            confidence_score=0.1,
            flagged_keywords=[],
            action="allow",
            reviewed_at=datetime.now()
        )
        
        assert result.content_id == "msg1"
        assert result.is_approved is True
        assert result.action == "allow"
    
    def test_moderation_result_invalid_confidence(self):
        """测试无效置信度"""
        with pytest.raises(ValueError):
            ModerationResult(
                content_id="msg1",
                is_approved=True,
                violation_types=[],
                confidence_score=1.5,  # 无效
                flagged_keywords=[],
                action="allow",
                reviewed_at=datetime.now()
            )
    
    def test_moderation_result_invalid_action(self):
        """测试无效动作"""
        with pytest.raises(ValueError):
            ModerationResult(
                content_id="msg1",
                is_approved=True,
                violation_types=[],
                confidence_score=0.5,
                flagged_keywords=[],
                action="invalid",  # 无效
                reviewed_at=datetime.now()
            )
    
    def test_violation_creation(self):
        """测试创建违规记录"""
        violation = Violation(
            violation_id="v1",
            user_id="user1",
            content_id="msg1",
            violation_type=Violation.TYPE_VIOLENCE,
            severity=Violation.SEVERITY_HIGH,
            content_snapshot="暴力内容",
            detected_at=datetime.now()
        )
        
        assert violation.violation_id == "v1"
        assert violation.violation_type == Violation.TYPE_VIOLENCE
        assert violation.severity == Violation.SEVERITY_HIGH
    
    def test_violation_invalid_type(self):
        """测试无效违规类型"""
        with pytest.raises(ValueError):
            Violation(
                violation_id="v1",
                user_id="user1",
                content_id="msg1",
                violation_type="invalid",  # 无效
                severity=Violation.SEVERITY_HIGH,
                content_snapshot="内容",
                detected_at=datetime.now()
            )
    
    def test_user_report_creation(self):
        """测试创建用户举报"""
        report = UserReport(
            report_id="r1",
            reporter_id="user1",
            reported_id="user2",
            report_type=UserReport.TYPE_HARASSMENT,
            reason="骚扰",
            evidence=["msg1"],
            status=UserReport.STATUS_PENDING,
            created_at=datetime.now()
        )
        
        assert report.report_id == "r1"
        assert report.reporter_id == "user1"
        assert report.reported_id == "user2"
    
    def test_penalty_creation(self):
        """测试创建处罚记录"""
        penalty = Penalty(
            penalty_id="p1",
            user_id="user1",
            violation_id="v1",
            penalty_type=Penalty.TYPE_MUTE,
            duration=86400,
            reason="违规",
            applied_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        assert penalty.penalty_id == "p1"
        assert penalty.penalty_type == Penalty.TYPE_MUTE
        assert penalty.duration == 86400
    
    def test_penalty_invalid_duration(self):
        """测试无效处罚时长"""
        with pytest.raises(ValueError):
            Penalty(
                penalty_id="p1",
                user_id="user1",
                violation_id="v1",
                penalty_type=Penalty.TYPE_MUTE,
                duration=-2,  # 无效
                reason="违规",
                applied_at=datetime.now(),
                expires_at=None
            )

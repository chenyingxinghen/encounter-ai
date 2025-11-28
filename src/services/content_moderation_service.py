"""
内容审查与监管服务
Content Moderation Service
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid
import re
from collections import defaultdict

from src.models.moderation import ModerationResult, Violation, UserReport, Penalty
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ContentModerationService:
    """内容审查与监管服务"""
    
    def __init__(self):
        """初始化服务"""
        # 违规关键词库
        self.keyword_library = self._build_keyword_library()
        
        # 存储违规记录
        self.violations: Dict[str, Violation] = {}
        
        # 存储用户举报
        self.reports: Dict[str, UserReport] = {}
        
        # 存储处罚记录
        self.penalties: Dict[str, Penalty] = {}
        
        # 用户违规计数
        self.user_violation_counts: Dict[str, int] = defaultdict(int)
        
        # 违规阈值配置
        self.violation_thresholds = {
            "warning": 1,  # 第1次违规：警告
            "mute": 3,     # 第3次违规：禁言
            "suspend": 5,  # 第5次违规：暂停
            "ban": 10      # 第10次违规：封号
        }
        
        logger.info("ContentModerationService initialized")
    
    def _build_keyword_library(self) -> Dict[str, List[str]]:
        """构建违规关键词库"""
        return {
            Violation.TYPE_VIOLENCE: [
                "暴力", "打人", "杀人", "伤害", "攻击", "殴打",
                "violence", "kill", "hurt", "attack", "beat"
            ],
            Violation.TYPE_PORNOGRAPHY: [
                "色情", "裸体", "性交", "黄色", "淫秽",
                "porn", "nude", "sex", "xxx"
            ],
            Violation.TYPE_HARASSMENT: [
                "骚扰", "侮辱", "辱骂", "威胁", "恐吓", "人身攻击",
                "harass", "insult", "threaten", "bully"
            ],
            Violation.TYPE_SPAM: [
                "广告", "推广", "加微信", "刷单", "兼职赚钱",
                "spam", "advertisement", "promotion"
            ],
            Violation.TYPE_POLITICAL: [
                "政治敏感", "反动", "颠覆", "分裂",
                "political", "subversion"
            ]
        }
    
    def moderate_message(self, message: str, user_id: str, 
                        message_id: Optional[str] = None) -> ModerationResult:
        """
        审查消息内容
        
        Args:
            message: 消息内容
            user_id: 用户ID
            message_id: 消息ID（可选）
            
        Returns:
            ModerationResult: 审查结果
        """
        if message_id is None:
            message_id = str(uuid.uuid4())
        
        # 检测违规内容
        violation_types = self.detect_violation(message)
        flagged_keywords = self._find_flagged_keywords(message)
        
        # 计算置信度（基于关键词匹配数量）
        confidence_score = min(len(flagged_keywords) * 0.3, 1.0)
        
        # 确定处理动作
        if not violation_types:
            action = "allow"
            is_approved = True
        elif confidence_score >= 0.8:
            action = "block"
            is_approved = False
            # 记录违规
            self._record_violation(user_id, message_id, message, 
                                  violation_types, "high")
        elif confidence_score >= 0.5:
            action = "review"
            is_approved = False
            # 记录违规待审核
            self._record_violation(user_id, message_id, message, 
                                  violation_types, "medium")
        else:
            action = "allow"
            is_approved = True
        
        result = ModerationResult(
            content_id=message_id,
            is_approved=is_approved,
            violation_types=violation_types,
            confidence_score=confidence_score,
            flagged_keywords=flagged_keywords,
            action=action,
            reviewed_at=datetime.now()
        )
        
        logger.info(f"Message moderated: user={user_id}, action={action}, "
                   f"violations={violation_types}")
        
        return result
    
    def detect_violation(self, content: str) -> List[str]:
        """
        检测违规内容类型
        
        Args:
            content: 内容文本
            
        Returns:
            List[str]: 违规类型列表
        """
        violations = []
        content_lower = content.lower()
        
        for violation_type, keywords in self.keyword_library.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if violation_type not in violations:
                        violations.append(violation_type)
                    break
        
        return violations
    
    def _find_flagged_keywords(self, content: str) -> List[str]:
        """查找触发的关键词"""
        flagged = []
        content_lower = content.lower()
        
        for keywords in self.keyword_library.values():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    flagged.append(keyword)
        
        return flagged
    
    def _record_violation(self, user_id: str, content_id: str, 
                         content: str, violation_types: List[str],
                         severity: str) -> Violation:
        """记录违规"""
        violation_id = str(uuid.uuid4())
        
        # 选择主要违规类型
        primary_type = violation_types[0] if violation_types else Violation.TYPE_SPAM
        
        violation = Violation(
            violation_id=violation_id,
            user_id=user_id,
            content_id=content_id,
            violation_type=primary_type,
            severity=severity,
            content_snapshot=content[:200],  # 保存前200字符
            detected_at=datetime.now(),
            status=Violation.STATUS_PENDING
        )
        
        self.violations[violation_id] = violation
        self.user_violation_counts[user_id] += 1
        
        # 检查是否需要自动处罚
        self._check_auto_penalty(user_id, violation_id)
        
        return violation
    
    def handle_user_report(self, reporter_id: str, reported_id: str,
                          report_type: str, reason: str,
                          evidence: List[str]) -> UserReport:
        """
        处理用户举报
        
        Args:
            reporter_id: 举报人ID
            reported_id: 被举报人ID
            report_type: 举报类型
            reason: 举报原因
            evidence: 证据列表
            
        Returns:
            UserReport: 举报记录
        """
        report_id = str(uuid.uuid4())
        
        report = UserReport(
            report_id=report_id,
            reporter_id=reporter_id,
            reported_id=reported_id,
            report_type=report_type,
            reason=reason,
            evidence=evidence,
            status=UserReport.STATUS_PENDING,
            created_at=datetime.now()
        )
        
        self.reports[report_id] = report
        
        logger.info(f"User report created: reporter={reporter_id}, "
                   f"reported={reported_id}, type={report_type}")
        
        # 启动审查流程
        self._start_report_review(report_id)
        
        return report
    
    def _start_report_review(self, report_id: str):
        """启动举报审查流程"""
        if report_id not in self.reports:
            return
        
        report = self.reports[report_id]
        report.status = UserReport.STATUS_INVESTIGATING
        
        logger.info(f"Report review started: report_id={report_id}")
    
    def review_flagged_content(self, content_id: str, reviewer_id: str,
                              decision: str) -> None:
        """
        审核标记的内容
        
        Args:
            content_id: 内容ID
            reviewer_id: 审核人员ID
            decision: 审核决定 ("confirm", "dismiss")
        """
        # 查找相关违规记录
        for violation in self.violations.values():
            if violation.content_id == content_id:
                violation.reviewed_by = reviewer_id
                
                if decision == "confirm":
                    violation.status = Violation.STATUS_CONFIRMED
                    logger.info(f"Violation confirmed: {violation.violation_id}")
                elif decision == "dismiss":
                    violation.status = Violation.STATUS_DISMISSED
                    # 减少用户违规计数
                    self.user_violation_counts[violation.user_id] -= 1
                    logger.info(f"Violation dismissed: {violation.violation_id}")
    
    def get_user_violation_history(self, user_id: str) -> List[Violation]:
        """
        获取用户违规历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Violation]: 违规记录列表
        """
        return [v for v in self.violations.values() if v.user_id == user_id]
    
    def apply_penalty(self, user_id: str, violation_id: str,
                     penalty_type: Optional[str] = None) -> Penalty:
        """
        施加处罚
        
        Args:
            user_id: 用户ID
            violation_id: 违规记录ID
            penalty_type: 处罚类型（可选，自动根据违规次数确定）
            
        Returns:
            Penalty: 处罚记录
        """
        penalty_id = str(uuid.uuid4())
        
        # 如果未指定处罚类型，根据违规次数自动确定
        if penalty_type is None:
            violation_count = self.user_violation_counts[user_id]
            penalty_type = self._determine_penalty_type(violation_count)
        
        # 确定处罚时长
        duration, expires_at = self._determine_penalty_duration(penalty_type)
        
        # 获取违规原因
        violation = self.violations.get(violation_id)
        reason = f"违规类型: {violation.violation_type}" if violation else "违规行为"
        
        penalty = Penalty(
            penalty_id=penalty_id,
            user_id=user_id,
            violation_id=violation_id,
            penalty_type=penalty_type,
            duration=duration,
            reason=reason,
            applied_at=datetime.now(),
            expires_at=expires_at,
            status=Penalty.STATUS_ACTIVE
        )
        
        self.penalties[penalty_id] = penalty
        
        logger.warning(f"Penalty applied: user={user_id}, type={penalty_type}, "
                      f"duration={duration}")
        
        return penalty
    
    def _determine_penalty_type(self, violation_count: int) -> str:
        """根据违规次数确定处罚类型"""
        if violation_count >= self.violation_thresholds["ban"]:
            return Penalty.TYPE_BAN
        elif violation_count >= self.violation_thresholds["suspend"]:
            return Penalty.TYPE_SUSPEND
        elif violation_count >= self.violation_thresholds["mute"]:
            return Penalty.TYPE_MUTE
        else:
            return Penalty.TYPE_WARNING
    
    def _determine_penalty_duration(self, penalty_type: str) -> tuple:
        """确定处罚时长"""
        durations = {
            Penalty.TYPE_WARNING: (0, None),  # 警告无时长
            Penalty.TYPE_MUTE: (86400, datetime.now() + timedelta(days=1)),  # 1天
            Penalty.TYPE_SUSPEND: (604800, datetime.now() + timedelta(days=7)),  # 7天
            Penalty.TYPE_BAN: (-1, None)  # 永久
        }
        return durations.get(penalty_type, (0, None))
    
    def _check_auto_penalty(self, user_id: str, violation_id: str):
        """检查是否需要自动处罚"""
        violation_count = self.user_violation_counts[user_id]
        
        # 达到阈值时自动处罚
        if violation_count in self.violation_thresholds.values():
            self.apply_penalty(user_id, violation_id)
    
    def get_user_penalties(self, user_id: str) -> List[Penalty]:
        """获取用户的处罚记录"""
        return [p for p in self.penalties.values() if p.user_id == user_id]
    
    def is_user_penalized(self, user_id: str) -> bool:
        """检查用户是否正在被处罚"""
        now = datetime.now()
        for penalty in self.penalties.values():
            if (penalty.user_id == user_id and 
                penalty.status == Penalty.STATUS_ACTIVE):
                # 检查是否过期
                if penalty.expires_at is None or penalty.expires_at > now:
                    return True
                else:
                    # 标记为过期
                    penalty.status = Penalty.STATUS_EXPIRED
        return False
    
    def handle_appeal(self, user_id: str, violation_id: str, 
                     appeal_reason: str) -> bool:
        """
        处理用户申诉
        
        Args:
            user_id: 用户ID
            violation_id: 违规记录ID
            appeal_reason: 申诉原因
            
        Returns:
            bool: 是否接受申诉
        """
        if violation_id not in self.violations:
            return False
        
        violation = self.violations[violation_id]
        
        if violation.user_id != user_id:
            return False
        
        # 更新违规状态为申诉中
        violation.status = Violation.STATUS_APPEALED
        
        logger.info(f"Appeal submitted: user={user_id}, "
                   f"violation={violation_id}, reason={appeal_reason}")
        
        return True
    
    def get_moderation_stats(self) -> Dict:
        """获取审查统计数据"""
        total_violations = len(self.violations)
        total_reports = len(self.reports)
        total_penalties = len(self.penalties)
        
        # 按类型统计违规
        violation_by_type = defaultdict(int)
        for v in self.violations.values():
            violation_by_type[v.violation_type] += 1
        
        # 按类型统计处罚
        penalty_by_type = defaultdict(int)
        for p in self.penalties.values():
            penalty_by_type[p.penalty_type] += 1
        
        return {
            "total_violations": total_violations,
            "total_reports": total_reports,
            "total_penalties": total_penalties,
            "violations_by_type": dict(violation_by_type),
            "penalties_by_type": dict(penalty_by_type),
            "users_with_violations": len(self.user_violation_counts)
        }

    def get_user_reports(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[UserReport]:
        """
        获取用户的举报记录
        
        Args:
            user_id: 用户ID
            status_filter: 状态过滤
            limit: 返回数量限制
            
        Returns:
            List[UserReport]: 举报记录列表
        """
        user_reports = [
            report for report in self._reports.values()
            if report.reporter_id == user_id
        ]
        
        # 状态过滤
        if status_filter:
            user_reports = [
                report for report in user_reports
                if report.status == status_filter
            ]
        
        # 按创建时间倒序排序
        user_reports.sort(key=lambda x: x.created_at, reverse=True)
        
        return user_reports[:limit]
    
    def get_report(self, report_id: str) -> UserReport:
        """
        获取举报详情
        
        Args:
            report_id: 举报ID
            
        Returns:
            UserReport: 举报对象
        """
        if report_id not in self._reports:
            raise NotFoundError(f"Report not found: {report_id}")
        
        return self._reports[report_id]
    
    def get_violation(self, violation_id: str) -> Violation:
        """
        获取违规记录
        
        Args:
            violation_id: 违规ID
            
        Returns:
            Violation: 违规记录
        """
        if violation_id not in self._violations:
            raise NotFoundError(f"Violation not found: {violation_id}")
        
        return self._violations[violation_id]
    
    def submit_appeal(
        self,
        violation_id: str,
        user_id: str,
        appeal_reason: str
    ) -> dict:
        """
        提交申诉
        
        Args:
            violation_id: 违规ID
            user_id: 用户ID
            appeal_reason: 申诉理由
            
        Returns:
            dict: 申诉结果
        """
        violation = self.get_violation(violation_id)
        
        # 验证用户权限
        if violation.user_id != user_id:
            raise ValidationError("User not authorized to appeal this violation")
        
        # 更新违规状态
        violation.status = "appealed"
        
        self.logger.info(f"Appeal submitted for violation {violation_id} by user {user_id}")
        
        return {
            "violation_id": violation_id,
            "status": "appealed",
            "appeal_reason": appeal_reason
        }
    
    def get_user_penalties(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[Penalty]:
        """
        获取用户的处罚记录
        
        Args:
            user_id: 用户ID
            status_filter: 状态过滤
            limit: 返回数量限制
            
        Returns:
            List[Penalty]: 处罚记录列表
        """
        user_penalties = [
            penalty for penalty in self._penalties.values()
            if penalty.user_id == user_id
        ]
        
        # 状态过滤
        if status_filter:
            user_penalties = [
                penalty for penalty in user_penalties
                if penalty.status == status_filter
            ]
        
        # 按应用时间倒序排序
        user_penalties.sort(key=lambda x: x.applied_at, reverse=True)
        
        return user_penalties[:limit]
    
    def get_penalty(self, penalty_id: str) -> Penalty:
        """
        获取处罚详情
        
        Args:
            penalty_id: 处罚ID
            
        Returns:
            Penalty: 处罚对象
        """
        if penalty_id not in self._penalties:
            raise NotFoundError(f"Penalty not found: {penalty_id}")
        
        return self._penalties[penalty_id]
    
    def get_user_moderation_status(self, user_id: str) -> dict:
        """
        获取用户的审查状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 审查状态信息
        """
        # 获取活跃的处罚
        active_penalties = [
            penalty for penalty in self._penalties.values()
            if penalty.user_id == user_id and penalty.status == "active"
        ]
        
        # 获取违规历史
        violations = self.get_user_violation_history(user_id)
        
        # 判断当前状态
        is_muted = any(p.penalty_type == "mute" for p in active_penalties)
        is_suspended = any(p.penalty_type == "suspend" for p in active_penalties)
        is_banned = any(p.penalty_type == "ban" for p in active_penalties)
        
        return {
            "user_id": user_id,
            "is_muted": is_muted,
            "is_suspended": is_suspended,
            "is_banned": is_banned,
            "active_penalties": len(active_penalties),
            "total_violations": len(violations),
            "penalties": active_penalties
        }

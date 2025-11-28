"""API依赖项"""
from src.services.user_profile_service import UserProfileService
from src.services.matching_service import MatchingService
from src.services.conversation_service import ConversationService
from src.services.report_service import ReportService
from src.services.content_moderation_service import ContentModerationService
from src.services.dialogue_assistant_service import DialogueAssistantService
from src.services.profile_update_service import ProfileUpdateService

# 创建共享的服务实例
user_profile_service = UserProfileService()
matching_service = MatchingService(user_profile_service=user_profile_service)
conversation_service = ConversationService()
report_service = ReportService()
content_moderation_service = ContentModerationService()
dialogue_assistant_service = DialogueAssistantService()
profile_update_service = ProfileUpdateService(
    user_profile_service=user_profile_service,
    matching_service=matching_service
)


def get_user_profile_service() -> UserProfileService:
    """获取用户画像服务实例"""
    return user_profile_service


def get_matching_service() -> MatchingService:
    """获取匹配服务实例"""
    return matching_service


def get_conversation_service() -> ConversationService:
    """获取对话服务实例"""
    return conversation_service


def get_report_service() -> ReportService:
    """获取报告服务实例"""
    return report_service


def get_content_moderation_service() -> ContentModerationService:
    """获取内容审查服务实例"""
    return content_moderation_service


def get_dialogue_assistant_service() -> DialogueAssistantService:
    """获取对话助手服务实例"""
    return dialogue_assistant_service


def get_profile_update_service() -> ProfileUpdateService:
    """获取画像更新服务实例"""
    return profile_update_service

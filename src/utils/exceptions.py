"""自定义异常类"""


class YouthCompanionException(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseError(YouthCompanionException):
    """数据库错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class ValidationError(YouthCompanionException):
    """数据验证错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(YouthCompanionException):
    """认证错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(YouthCompanionException):
    """授权错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "AUTHORIZATION_ERROR")


class NotFoundError(YouthCompanionException):
    """资源未找到错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND_ERROR")


class AIModelError(YouthCompanionException):
    """AI模型错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "AI_MODEL_ERROR")


class MatchingError(YouthCompanionException):
    """匹配算法错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "MATCHING_ERROR")


class ContentModerationError(YouthCompanionException):
    """内容审查错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "CONTENT_MODERATION_ERROR")


class ConversationNotFoundError(NotFoundError):
    """对话未找到错误"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.code = "CONVERSATION_NOT_FOUND"


class InvalidConversationStateError(YouthCompanionException):
    """无效的对话状态错误"""
    
    def __init__(self, message: str):
        super().__init__(message, "INVALID_CONVERSATION_STATE")


class UnauthorizedAccessError(AuthorizationError):
    """未授权访问错误"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.code = "UNAUTHORIZED_ACCESS"

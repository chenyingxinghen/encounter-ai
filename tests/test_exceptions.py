"""测试异常类"""
import pytest
from src.utils.exceptions import (
    YouthCompanionException,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    AIModelError,
    MatchingError,
    ContentModerationError
)


def test_base_exception():
    """测试基础异常类"""
    exc = YouthCompanionException("测试错误", "TEST_ERROR")
    assert exc.message == "测试错误"
    assert exc.code == "TEST_ERROR"
    assert str(exc) == "测试错误"


def test_database_error():
    """测试数据库错误"""
    exc = DatabaseError("数据库连接失败")
    assert exc.code == "DATABASE_ERROR"
    assert exc.message == "数据库连接失败"


def test_validation_error():
    """测试验证错误"""
    exc = ValidationError("数据格式错误")
    assert exc.code == "VALIDATION_ERROR"


def test_authentication_error():
    """测试认证错误"""
    exc = AuthenticationError("认证失败")
    assert exc.code == "AUTHENTICATION_ERROR"


def test_not_found_error():
    """测试未找到错误"""
    exc = NotFoundError("资源不存在")
    assert exc.code == "NOT_FOUND_ERROR"


def test_ai_model_error():
    """测试AI模型错误"""
    exc = AIModelError("模型推理失败")
    assert exc.code == "AI_MODEL_ERROR"


def test_matching_error():
    """测试匹配错误"""
    exc = MatchingError("匹配算法失败")
    assert exc.code == "MATCHING_ERROR"


def test_content_moderation_error():
    """测试内容审查错误"""
    exc = ContentModerationError("内容审查失败")
    assert exc.code == "CONTENT_MODERATION_ERROR"

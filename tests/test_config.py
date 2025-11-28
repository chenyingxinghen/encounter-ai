"""测试配置模块"""
import pytest
from src.config import settings


def test_settings_loaded():
    """测试配置是否正确加载"""
    assert settings.app_name == "青春伴行平台"
    assert settings.app_version == "0.1.0"
    assert isinstance(settings.debug, bool)


def test_database_config():
    """测试数据库配置"""
    assert settings.mysql_host is not None
    assert settings.mysql_port > 0
    assert settings.mongodb_host is not None
    assert settings.redis_host is not None


def test_security_config():
    """测试安全配置"""
    assert settings.secret_key is not None
    assert len(settings.secret_key) > 0
    assert settings.algorithm == "HS256"

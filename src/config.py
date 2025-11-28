"""应用配置管理"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    app_name: str = "青春伴行平台"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "youth_companion"
    
    # MongoDB配置
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_database: str = "youth_companion"
    mongodb_user: Optional[str] = None
    mongodb_password: Optional[str] = None
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 安全配置
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI模型配置
    bert_model_path: str = "bert-base-chinese"
    chatglm_model_path: str = "THUDM/chatglm3-6b"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

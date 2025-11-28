"""主应用入口"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.utils.logger import setup_logger
from src.utils.error_handler import (
    youth_companion_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from src.utils.exceptions import YouthCompanionException
from src.database import init_db, mongodb, redis_cache
from src.api.user_api import router as user_router
from src.api.auth_api import router as auth_router
from src.api.matching_api import router as matching_router
from src.api.conversation_api import router as conversation_router
from src.api.report_api import router as report_router
from src.api.moderation_api import router as moderation_router
import logging

# 初始化日志系统
setup_logger()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="""
    青春伴行 - 基于AI技术的大学生深度社交匹配平台
    
    ## 功能模块
    
    * **用户管理** - 用户注册、登录、画像构建
    * **认证授权** - JWT令牌认证
    * **智能匹配** - 基于多维度画像的智能匹配算法
    * **对话管理** - 实时对话、消息发送、历史记录
    * **成长报告** - 周报、月报、年报生成与分享
    * **内容审查** - 违规检测、用户举报、申诉处理
    
    ## 技术栈
    
    * FastAPI - 高性能异步Web框架
    * MySQL - 关系型数据库
    * MongoDB - 文档数据库
    * Redis - 缓存系统
    * BERT - 人格识别模型
    * ChatGLM - 对话生成模型
    """,
    contact={
        "name": "青春伴行团队",
        "email": "support@youth-companion.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(YouthCompanionException, youth_companion_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(matching_router)
app.include_router(conversation_router)
app.include_router(report_router)
app.include_router(moderation_router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    
    try:
        # 初始化MySQL数据库
        init_db()
        logger.info("MySQL数据库初始化完成")
        
        # 连接MongoDB
        mongodb.connect()
        logger.info("MongoDB连接完成")
        
        # 连接Redis
        redis_cache.connect()
        logger.info("Redis连接完成")
        
        logger.info("所有数据库连接初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("关闭应用...")
    
    # 关闭数据库连接
    mongodb.close()
    redis_cache.close()
    
    logger.info("应用已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

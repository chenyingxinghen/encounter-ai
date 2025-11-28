"""MongoDB数据库连接管理"""
from pymongo import MongoClient
from pymongo.database import Database
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB连接管理类"""
    
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
    
    def connect(self):
        """连接MongoDB"""
        try:
            # 构建连接URL
            if settings.mongodb_user and settings.mongodb_password:
                mongo_url = (
                    f"mongodb://{settings.mongodb_user}:{settings.mongodb_password}"
                    f"@{settings.mongodb_host}:{settings.mongodb_port}/"
                )
            else:
                mongo_url = f"mongodb://{settings.mongodb_host}:{settings.mongodb_port}/"
            
            self.client = MongoClient(mongo_url)
            self.db = self.client[settings.mongodb_database]
            
            # 测试连接
            self.client.server_info()
            logger.info("MongoDB连接成功")
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
    
    def close(self):
        """关闭MongoDB连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
    
    def get_collection(self, collection_name: str):
        """获取集合"""
        if not self.db:
            raise RuntimeError("MongoDB未连接")
        return self.db[collection_name]


# 全局MongoDB实例
mongodb = MongoDB()


def get_mongodb() -> Database:
    """获取MongoDB数据库实例"""
    if not mongodb.db:
        mongodb.connect()
    return mongodb.db

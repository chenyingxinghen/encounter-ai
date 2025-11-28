"""Redis缓存连接管理"""
from redis import Redis
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存管理类"""
    
    def __init__(self):
        self.client: Redis = None
    
    def connect(self):
        """连接Redis"""
        try:
            self.client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            
            # 测试连接
            self.client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def close(self):
        """关闭Redis连接"""
        if self.client:
            self.client.close()
            logger.info("Redis连接已关闭")
    
    def get(self, key: str):
        """获取缓存值"""
        if not self.client:
            raise RuntimeError("Redis未连接")
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: int = None):
        """设置缓存值"""
        if not self.client:
            raise RuntimeError("Redis未连接")
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str):
        """删除缓存值"""
        if not self.client:
            raise RuntimeError("Redis未连接")
        return self.client.delete(key)


# 全局Redis实例
redis_cache = RedisCache()


def get_redis() -> Redis:
    """获取Redis客户端实例"""
    if not redis_cache.client:
        redis_cache.connect()
    return redis_cache.client

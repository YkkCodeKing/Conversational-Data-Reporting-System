import json
from typing import Any, Dict, Optional

import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class CacheManager:
    """
    两级缓存管理器：L1(内存字典) + L2(Redis)
    提供基本的 get, set, delete 方法
    """
    def __init__(self):
        self._l1_cache: Dict[str, Any] = {}
        self._redis_client: Optional[redis.Redis] = None

    async def initialize(self):
        """初始化 Redis 连接"""
        try:
            self._redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            # 尝试 ping 测试连接
            await self._redis_client.ping()
            logger.info("Redis initialized successfully (L2 cache active).")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis L2 cache: {e}. Falling back to L1 only.")
            self._redis_client = None

    async def close(self):
        """关闭 Redis 连接"""
        if self._redis_client:
            await self._redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存：先查 L1，再查 L2"""
        # 1. 查 L1
        if key in self._l1_cache:
            return self._l1_cache[key]
        
        # 2. 查 L2
        if self._redis_client:
            try:
                val = await self._redis_client.get(key)
                if val is not None:
                    # 将 L2 结果回写到 L1
                    try:
                        parsed_val = json.loads(val)
                    except json.JSONDecodeError:
                        parsed_val = val
                    self._l1_cache[key] = parsed_val
                    return parsed_val
            except Exception as e:
                logger.error(f"Redis get error for {key}: {e}")
        
        return None

    async def set(self, key: str, value: Any, expire_seconds: int = 3600):
        """设置缓存：同时写入 L1 和 L2"""
        self._l1_cache[key] = value

        if self._redis_client:
            try:
                if isinstance(value, (dict, list)):
                    val_str = json.dumps(value)
                else:
                    val_str = str(value)
                await self._redis_client.setex(key, expire_seconds, val_str)
            except Exception as e:
                logger.error(f"Redis set error for {key}: {e}")

    async def delete(self, key: str):
        """删除缓存"""
        self._l1_cache.pop(key, None)
        if self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error for {key}: {e}")
                
    def clear_l1(self):
        """仅清理 L1 本地缓存"""
        self._l1_cache.clear()

# 全局单例 CacheManager
cache_manager = CacheManager()

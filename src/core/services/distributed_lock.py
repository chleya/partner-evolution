"""
Redis分布式锁 - 解决心跳与LangGraph冲突
解决PM审查中提到的"定时器冲突"问题
"""
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class DistributedLock:
    """
    Redis分布式锁
    
    用于：
    1. 心跳触发前检查Agent状态
    2. 防止多任务并发冲突
    """
    
    DEFAULT_TIMEOUT = 30  # 默认30秒超时
    DEFAULT_RETRY = 3     # 默认重试3次
    DEFAULT_DELAY = 0.2   # 默认重试间隔200ms
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._connected = False
    
    async def connect(self, connection_string: str = None) -> bool:
        """连接Redis"""
        if self._connected:
            return True
        
        try:
            import redis.asyncio as aioredis
            self.redis = await aioredis.from_url(
                connection_string or "redis://localhost:6379",
                decode_responses=True
            )
            self._connected = True
            logger.info("Connected to Redis")
            return True
        except ImportError:
            logger.warning("redis not installed")
            return False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return False
    
    async def acquire(
        self,
        key: str,
        timeout: int = DEFAULT_TIMEOUT,
        retry: int = DEFAULT_RETRY,
        delay: float = DEFAULT_DELAY
    ) -> bool:
        """获取锁
        
        Args:
            key: 锁键名
            timeout: 锁超时时间(秒)
            retry: 重试次数
            delay: 重试间隔(秒)
            
        Returns:
            是否成功获取锁
        """
        if not self.redis:
            logger.warning("Redis not connected, lock unavailable")
            return True  # 无Redis时允许执行
        
        lock_key = f"lock:{key}"
        
        for _ in range(retry):
            try:
                # 尝试设置锁 (PX=超时毫秒, NX=不存在时设置)
                result = await self.redis.set(
                    lock_key,
                    "locked",
                    px=timeout * 1000,
                    nx=True
                )
                
                if result:
                    logger.debug(f"Acquired lock: {key}")
                    return True
                
                # 锁已被持有，等待后重试
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.warning(f"Lock acquire error: {e}")
                return True  # 错误时允许执行
        
        logger.warning(f"Failed to acquire lock: {key} (max retries)")
        return False
    
    async def release(self, key: str) -> bool:
        """释放锁"""
        if not self.redis:
            return True
        
        lock_key = f"lock:{key}"
        
        try:
            await self.redis.delete(lock_key)
            logger.debug(f"Released lock: {key}")
            return True
        except Exception as e:
            logger.warning(f"Lock release error: {e}")
            return False
    
    async def is_locked(self, key: str) -> bool:
        """检查锁是否被持有"""
        if not self.redis:
            return False
        
        lock_key = f"lock:{key}"
        
        try:
            return await self.redis.exists(lock_key) > 0
        except:
            return False
    
    async def get_ttl(self, key: str) -> int:
        """获取锁剩余TTL(毫秒)"""
        if not self.redis:
            return 0
        
        lock_key = f"lock:{key}"
        
        try:
            return await self.redis.pttl(lock_key)
        except:
            return 0


# 上下文管理器支持
class LockContext:
    """锁上下文管理器"""
    
    def __init__(self, lock: DistributedLock, key: str, timeout: int = 30):
        self.lock = lock
        self.key = key
        self.timeout = timeout
        self.acquired = False
    
    async def __aenter__(self):
        self.acquired = await self.lock.acquire(self.key, self.timeout)
        return self.acquired
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            await self.lock.release(self.key)


# 全局实例
_distributed_lock = None

def get_distributed_lock(redis_client=None) -> DistributedLock:
    """获取分布式锁实例"""
    global _distributed_lock
    if _distributed_lock is None:
        _distributed_lock = DistributedLock(redis_client)
    return _distributed_lock


# 便捷函数
async def with_lock(key: str, func, timeout: int = 30):
    """带锁执行函数"""
    lock = get_distributed_lock()
    
    async with LockContext(lock, key, timeout):
        return await func()


import asyncio

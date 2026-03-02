"""
性能优化模块
- 缓存层
- 连接池
- 异步处理
"""
import asyncio
import functools
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)


class LRUCache:
    """
    LRU缓存 - 线程安全
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # 秒
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            if key not in self._cache:
                return None
            
            # 检查过期
            if self._is_expired(key):
                self._remove(key)
                return None
            
            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            return self._cache[key]

    def set(self, key: str, value: Any):
        """设置缓存"""
        with self._lock:
            # 如果已存在，移除旧值
            if key in self._cache:
                self._remove(key)
            
            # 如果达到最大容量，移除最旧的
            while len(self._cache) >= self.max_size:
                oldest = next(iter(self._cache))
                self._remove(oldest)
            
            self._cache[key] = value
            self._timestamps[key] = time.time()

    def _is_expired(self, key: str) -> bool:
        """检查是否过期"""
        if key not in self._timestamps:
            return True
        return (time.time() - self._timestamps[key]) > self.ttl

    def _remove(self, key: str):
        """移除缓存项"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class AsyncExecutor:
    """
    异步执行器
    支持后台任务调度
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Any] = {}

    def submit(self, fn: Callable, *args, **kwargs) -> Any:
        """提交任务"""
        future = self.executor.submit(fn, *args, **kwargs)
        return future

    def submit_with_callback(self, fn: Callable, callback: Callable, *args, **kwargs):
        """提交任务并带回调"""
        def wrapped():
            try:
                result = fn(*args, **kwargs)
                if callback:
                    callback(result)
                return result
            except Exception as e:
                logger.error(f"Task error: {e}")
                raise
        
        return self.executor.submit(wrapped)

    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        self.executor.shutdown(wait=wait)


class RateLimiter:
    """
    限流器 - 令牌桶算法
    """
    
    def __init__(self, rate: int = 10, per: int = 60):
        """
        rate: 每per秒允许的请求数
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """获取令牌"""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # 补充令牌
            self.tokens = min(
                self.rate,
                self.tokens + elapsed * (self.rate / self.per)
            )
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False

    def wait_for_token(self, tokens: int = 1):
        """等待获取令牌"""
        while not self.acquire(tokens):
            time.sleep(0.1)


class PerformanceMonitor:
    """
    性能监控器
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def record(self, name: str, value: float):
        """记录指标"""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(value)
            
            # 保留最近1000条
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]

    def get_stats(self, name: str) -> Dict:
        """获取统计"""
        with self._lock:
            values = self.metrics.get(name, [])
            if not values:
                return {}
            
            sorted_values = sorted(values)
            return {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p50": sorted_values[len(values) // 2],
                "p95": sorted_values[int(len(values) * 0.95)],
                "p99": sorted_values[int(len(values) * 0.99)]
            }

    def get_all_stats(self) -> Dict:
        """获取所有统计"""
        return {name: self.get_stats(name) for name in self.metrics}


def timed(fn: Callable) -> Callable:
    """计时装饰器"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{fn.__name__} took {elapsed*1000:.2f}ms")
        return result
    return wrapper


def cached(cache: LRUCache):
    """缓存装饰器"""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{fn.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            result = cache.get(key)
            if result is not None:
                return result
            
            # 执行函数
            result = fn(*args, **kwargs)
            
            # 存入缓存
            cache.set(key, result)
            return result
        return wrapper
    return decorator


class ConnectionPool:
    """
    连接池 - 通用实现
    """
    
    def __init__(self, factory: Callable, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self._pool: list = []
        self._lock = threading.Lock()
        self._created = 0

    def get(self):
        """获取连接"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            
            if self._created < self.max_size:
                self._created += 1
                return self.factory()
            
            # 等待并重试
            time.sleep(0.1)
            return self.get()

    def release(self, conn):
        """释放连接"""
        with self._lock:
            if len(self._pool) < self.max_size:
                self._pool.append(conn)
            else:
                # 关闭多余连接
                if hasattr(conn, 'close'):
                    conn.close()

    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._pool:
                if hasattr(conn, 'close'):
                    conn.close()
            self._pool.clear()

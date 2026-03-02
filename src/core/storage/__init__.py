"""
存储模块
支持PostgreSQL + JSON降级
"""
from src.core.storage.postgres_manager import (
    StorageManager,
    PostgresManager,
    JSONFallback,
    get_storage_manager
)

__all__ = [
    'StorageManager',
    'PostgresManager', 
    'JSONFallback',
    'get_storage_manager'
]

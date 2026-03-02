"""
PostgreSQL数据库管理器
支持pgvector向量存储 + 优雅降级到JSON
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# 尝试导入PostgreSQL驱动
try:
    import psycopg2
    import numpy as np
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("PostgreSQL driver not available, using JSON fallback")


@dataclass
class DBConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    user: str = "ai_partner"
    password: str = ""
    database: str = "ai_partner_db"


class PostgresManager:
    """PostgreSQL管理器"""
    
    def __init__(self, config: DBConfig = None):
        self.config = config or DBConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "ai_partner"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_DATABASE", "ai_partner_db")
        )
        self.conn = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        if not POSTGRES_AVAILABLE:
            logger.info("PostgreSQL driver not available")
            return
            
        try:
            self.conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database
            )
            self.conn.autocommit = True
            logger.info(f"PostgreSQL connected to {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            self.conn = None
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self.conn:
            return False
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def execute(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询"""
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                results = cursor.fetchall()
                return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """执行查询，返回单条"""
        results = self.execute(query, params)
        return results[0] if results else None
    
    def execute_write(self, query: str, params: tuple = None) -> bool:
        """执行写入"""
        if not self.conn:
            return False
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
            return True
        except Exception as e:
            logger.error(f"Write failed: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


class JSONFallback:
    """JSON文件降级方案"""
    
    def __init__(self, data_dir: str = "data/storage"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, table: str) -> Path:
        return self.data_dir / f"{table}.json"
    
    def load(self, table: str) -> List[Dict]:
        """加载数据"""
        path = self._get_file_path(table)
        if not path.exists():
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save(self, table: str, data: List[Dict]) -> bool:
        """保存数据"""
        path = self._get_file_path(table)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False
    
    def append(self, table: str, item: Dict) -> bool:
        """追加数据"""
        data = self.load(table)
        data.append(item)
        return self.save(table, data)
    
    def update(self, table: str, id_field: str, item: Dict) -> bool:
        """更新数据"""
        data = self.load(table)
        for i, row in enumerate(data):
            if row.get(id_field) == item.get(id_field):
                data[i] = item
                return self.save(table, data)
        return self.append(table, item)
    
    def delete(self, table: str, id_field: str, item_id: str) -> bool:
        """删除数据"""
        data = self.load(table)
        data = [row for row in data if row.get(id_field) != item_id]
        return self.save(table, data)
    
    def query(self, table: str, filter_func=None) -> List[Dict]:
        """查询数据"""
        data = self.load(table)
        if filter_func:
            data = [row for row in data if filter_func(row)]
        return data


class StorageManager:
    """统一存储管理器 - 支持PostgreSQL和JSON降级"""
    
    def __init__(self, config: DBConfig = None):
        self.config = config
        
        # 自动探测PostgreSQL连接（自动降级）
        self.use_db = False
        self.db = None
        
        # 尝试连接PostgreSQL
        if POSTGRES_AVAILABLE:
            try:
                self.db = PostgresManager(config)
                if self.db.is_connected():
                    self.use_db = True
                    logger.info("PostgreSQL connected, using DB storage")
                else:
                    logger.warning("PostgreSQL connection failed, using JSON fallback")
                    self.db = None
            except Exception as e:
                logger.warning(f"PostgreSQL init failed: {e}, using JSON fallback")
                self.db = None
        else:
            logger.info("PostgreSQL driver not available, using JSON fallback")
        
        # 降级方案
        self.json_fallback = JSONFallback()
        
        # 记录启动日志
        if self.use_db:
            logger.info("Storage: PostgreSQL mode")
        else:
            logger.info("Storage: JSON fallback mode")
    
    # ============== 记忆操作 ==============
    
    def save_memory(self, memory: Dict) -> bool:
        """保存记忆"""
        if self.use_db:
            return self._save_memory_db(memory)
        return self.json_fallback.append("memories", memory)
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        if self.use_db:
            return self._get_memory_db(memory_id)
        data = self.json_fallback.query("memories", lambda x: x.get("id") == memory_id)
        return data[0] if data else None
    
    def get_memories_by_tier(self, tier: str, limit: int = 100) -> List[Dict]:
        """按层级获取记忆"""
        if self.use_db:
            return self._get_memories_by_tier_db(tier, limit)
        data = self.json_fallback.query("memories", lambda x: x.get("tier") == tier)
        return data[:limit]
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索记忆"""
        if self.use_db:
            return self._search_memories_db(query, limit)
        # JSON简单搜索
        data = self.json_fallback.query("memories", 
            lambda x: query.lower() in x.get("content", "").lower())
        return data[:limit]
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if self.use_db:
            return self._delete_memory_db(memory_id)
        return self.json_fallback.delete("memories", "id", memory_id)
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        if self.use_db:
            return self._get_memory_stats_db()
        
        data = self.json_fallback.load("memories")
        by_tier = {}
        for item in data:
            tier = item.get("tier", "unknown")
            if tier not in by_tier:
                by_tier[tier] = {"count": 0, "total_confidence": 0}
            by_tier[tier]["count"] += 1
            by_tier[tier]["total_confidence"] += item.get("confidence", 0)
        
        for tier in by_tier:
            count = by_tier[tier]["count"]
            by_tier[tier]["avg_confidence"] = by_tier[tier]["total_confidence"] / count if count > 0 else 0
            del by_tier[tier]["total_confidence"]
        
        return {"total": len(data), "by_tier": by_tier}
    
    # ============== PostgreSQL实现 ==============
    
    def _save_memory_db(self, memory: Dict) -> bool:
        query = """
            INSERT INTO memories (id, tier, memory_type, content, confidence, importance, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                confidence = EXCLUDED.confidence,
                importance = EXCLUDED.importance,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
        """
        params = (
            memory.get("id", ""),
            memory.get("tier", "recall"),
            memory.get("type", "general"),
            memory.get("content", ""),
            memory.get("confidence", 1.0),
            memory.get("importance", 0.5),
            json.dumps(memory.get("metadata", {}))
        )
        return self.db.execute_write(query, params)
    
    def _get_memory_db(self, memory_id: str) -> Optional[Dict]:
        query = "SELECT * FROM memories WHERE id = %s"
        return self.db.execute_one(query, (memory_id,))
    
    def _get_memories_by_tier_db(self, tier: str, limit: int) -> List[Dict]:
        query = "SELECT * FROM memories WHERE tier = %s ORDER BY created_at DESC LIMIT %s"
        return self.db.execute(query, (tier, limit))
    
    def _search_memories_db(self, query: str, limit: int) -> List[Dict]:
        # 简单LIKE搜索
        search_query = f"%{query}%"
        sql = "SELECT * FROM memories WHERE content LIKE %s LIMIT %s"
        return self.db.execute(sql, (search_query, limit))
    
    def _delete_memory_db(self, memory_id: str) -> bool:
        query = "DELETE FROM memories WHERE id = %s"
        return self.db.execute_write(query, (memory_id,))
    
    def _get_memory_stats_db(self) -> Dict:
        query = """
            SELECT tier, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM memories GROUP BY tier
        """
        results = self.db.execute(query)
        
        by_tier = {}
        total = 0
        for row in results:
            tier = row.get("tier", "unknown")
            by_tier[tier] = {"count": row.get("count", 0), "avg_confidence": row.get("avg_confidence", 0)}
            total += row.get("count", 0)
        
        return {"total": total, "by_tier": by_tier}
    
    # ============== 信念操作 (v2.2准备) ==============
    
    def save_belief(self, belief: Dict) -> bool:
        """保存信念（带去重和演化支持）"""
        content = belief.get("content", "")
        new_confidence = belief.get("confidence", 0.5)
        
        # 获取演化字段
        parent_id = belief.get("parent_id")
        version = belief.get("version", 1)
        
        # JSON模式下的去重检查
        if not self.use_db:
            existing = self.json_fallback.query("beliefs", lambda x: x.get("content") == content)
            if existing:
                # 取更高的confidence
                existing_belief = existing[0]
                old_confidence = existing_belief.get("confidence", 0)
                if new_confidence > old_confidence:
                    existing_belief["confidence"] = new_confidence
                    existing_belief["updated_at"] = datetime.now().isoformat()
                    existing_belief["version"] = existing_belief.get("version", 1) + 1
                return True  # 已存在，不重复添加
        
        # PostgreSQL模式
        if self.use_db:
            # 先检查是否存在相似内容
            check_query = "SELECT id, confidence, version FROM beliefs WHERE content = %s AND status = 'active'"
            existing = self.db.execute(check_query, (content,))
            
            if existing and len(existing) > 0:
                # 存在，取更高的confidence
                old_confidence = existing[0].get("confidence", 0)
                if new_confidence > old_confidence:
                    old_version = existing[0].get("version", 1)
                    update_query = "UPDATE beliefs SET confidence = %s, updated_at = NOW(), version = %s WHERE id = %s"
                    self.db.execute_write(update_query, (new_confidence, old_version + 1, existing[0].get("id")))
                return True  # 已存在，不重复插入
                    update_query = "UPDATE beliefs SET confidence = %s, updated_at = NOW() WHERE id = %s"
                    self.db.execute_write(update_query, (new_confidence, existing[0].get("id")))
                return True  # 已存在，不重复插入
            
            # 不存在，插入新记录
            query = """
                INSERT INTO beliefs (id, content, belief_type, confidence, evidence, stance, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            return self.db.execute_write(query, (
                belief.get("id", ""),
                belief.get("content", ""),
                belief.get("type", "factual"),
                belief.get("confidence", 0.5),
                json.dumps(belief.get("evidence", [])),
                belief.get("stance", "neutral"),
                belief.get("status", "active")
            ))
        
        return self.json_fallback.append("beliefs", belief)
    
    def get_beliefs(self, status: str = "active") -> List[Dict]:
        """获取信念"""
        if self.use_db:
            query = "SELECT * FROM beliefs WHERE status = %s ORDER BY confidence DESC"
            return self.db.execute(query, (status,))
        # JSON模式: 过滤status为active的，或没有status字段的(兼容旧数据)
        return self.json_fallback.query("beliefs", lambda x: x.get("status") == status or "status" not in x)
    
    # ============== 自主目标操作 (v2.2准备) ==============
    
    def save_goal(self, goal: Dict) -> bool:
        """保存目标"""
        if self.use_db:
            query = """
                INSERT INTO autonomous_goals (id, title, description, goal_type, priority, progress, status, source, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    progress = EXCLUDED.progress,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """
            return self.db.execute_write(query, (
                goal.get("id", ""),
                goal.get("title", ""),
                goal.get("description", ""),
                goal.get("type", "exploration"),
                goal.get("priority", 3),
                goal.get("progress", 0.0),
                goal.get("status", "pending"),
                goal.get("source", "self_initiated")
            ))
        return self.json_fallback.append("goals", goal)
    
    def get_goals(self, status: str = None) -> List[Dict]:
        """获取目标"""
        if self.use_db:
            if status:
                query = "SELECT * FROM autonomous_goals WHERE status = %s ORDER BY priority"
                return self.db.execute(query, (status,))
            query = "SELECT * FROM autonomous_goals ORDER BY priority"
            return self.db.execute(query)
        if status:
            return self.json_fallback.query("goals", lambda x: x.get("status") == status)
        return self.json_fallback.load("goals")
    
    # ============== 反对记录操作 ==============
    
    def save_opposition(self, opposition: Dict) -> bool:
        """保存反对记录"""
        if self.use_db:
            query = """
                INSERT INTO oppositions 
                (user_input, opposing_belief_id, belief_content, belief_confidence, severity, response_text, user_resolution, trace_id, user_id, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            return self.db.execute_write(query, (
                opposition.get("user_input", ""),
                opposition.get("opposing_belief_id"),
                opposition.get("belief_content", ""),
                opposition.get("belief_confidence", 0),
                opposition.get("severity", "gentle"),
                opposition.get("response_text", ""),
                opposition.get("user_resolution", "pending"),
                opposition.get("trace_id"),
                opposition.get("user_id", "default_user"),
                json.dumps(opposition.get("metadata", {}))
            ))
        return self.json_fallback.append("oppositions", opposition)
    
    def get_oppositions(self, limit: int = 10) -> List[Dict]:
        """获取反对记录"""
        if self.use_db:
            query = "SELECT * FROM oppositions ORDER BY created_at DESC LIMIT %s"
            return self.db.execute(query, (limit,))
        return self.json_fallback.load("oppositions")[-limit:]


# 全局实例
_storage_manager = None

def get_storage_manager() -> StorageManager:
    """获取存储管理器"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager

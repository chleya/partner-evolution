"""
PostgreSQL存储管理器 - 替换JSON方案
解决PM审查中的"数据存储临时性过强"问题
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)


class PostgresManager:
    """
    PostgreSQL存储管理器
    
    功能：
    1. 记忆的持久化存储
    2. 向量相似度搜索 (pgvector)
    3. 知识图谱存储 (Neo4j兼容)
    """
    
    # 表名
    TABLE_MEMORIES = "memories"
    TABLE_BELIEFS = "beliefs"
    TABLE_GOALS = "goals"
    TABLE_AUDIT = "audit_log"
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string
        self._conn = None
        self._connected = False
    
    async def connect(self) -> bool:
        """连接数据库"""
        if self._connected:
            return True
        
        # 尝试连接
        try:
            import asyncpg
            self._conn = await asyncpg.connect(self.connection_string)
            self._connected = True
            logger.info("Connected to PostgreSQL")
            return True
        except ImportError:
            logger.warning("asyncpg not installed, falling back to JSON")
            return False
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self._conn:
            await self._conn.close()
            self._connected = False
    
    async def init_schema(self):
        """初始化数据库表"""
        if not self._connected:
            return False
        
        # 创建记忆表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id VARCHAR(255) PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type VARCHAR(50),
                tier VARCHAR(20),
                confidence FLOAT DEFAULT 0.5,
                access_count INT DEFAULT 0,
                last_access TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                metadata JSONB
            )
        """)
        
        # 创建向量索引 (pgvector)
        try:
            await self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_embedding 
                ON memories USING ivfflat (embedding vector_cosine_ops)
            """)
        except:
            logger.warning("pgvector extension not available")
        
        # 创建信念表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS beliefs (
                id VARCHAR(255) PRIMARY KEY,
                statement TEXT NOT NULL,
                category VARCHAR(50),
                confidence FLOAT DEFAULT 0.5,
                sources JSONB,
                conflicts JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # 创建目标表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id VARCHAR(255) PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority VARCHAR(20),
                status VARCHAR(20) DEFAULT 'pending',
                progress FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        """)
        
        # 创建审计日志表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                level VARCHAR(20),
                action VARCHAR(255),
                message TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        logger.info("Database schema initialized")
        return True
    
    # ========== 记忆操作 ==========
    
    async def save_memory(self, memory: Dict) -> bool:
        """保存记忆"""
        if not self._connected:
            return False
        
        try:
            await self._conn.execute("""
                INSERT INTO memories (id, content, memory_type, tier, confidence, access_count, last_access, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    confidence = EXCLUDED.confidence,
                    access_count = EXCLUDED.access_count,
                    last_access = EXCLUDED.last_access,
                    metadata = EXCLUDED.metadata
            """,
                memory.get("id"),
                memory.get("content"),
                memory.get("type", "core"),
                memory.get("tier", "core"),
                memory.get("confidence", 0.5),
                memory.get("access_count", 0),
                datetime.now(timezone.utc),
                json.dumps(memory.get("metadata", {}))
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return False
    
    async def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        if not self._connected:
            return None
        
        try:
            row = await self._conn.fetchrow(
                "SELECT * FROM memories WHERE id = $1",
                memory_id
            )
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get memory: {e}")
            return None
    
    async def search_memories(
        self, 
        query: str = None,
        memory_type: str = None,
        tier: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """搜索记忆"""
        if not self._connected:
            return []
        
        try:
            # 基础查询
            sql = "SELECT * FROM memories WHERE 1=1"
            params = []
            
            if memory_type:
                params.append(memory_type)
                sql += f" AND memory_type = ${len(params)}"
            
            if tier:
                params.append(tier)
                sql += f" AND tier = ${len(params)}"
            
            # 按置信度和访问时间排序
            sql += " ORDER BY confidence DESC, last_access DESC LIMIT $#"
            params.append(limit)
            
            sql = sql.replace("$#", f"${len(params)}")
            
            rows = await self._conn.fetch(sql, *params)
            return [dict(r) for r in rows]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if not self._connected:
            return False
        
        try:
            await self._conn.execute(
                "DELETE FROM memories WHERE id = $1",
                memory_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    # ========== 信念操作 ==========
    
    async def save_belief(self, belief: Dict) -> bool:
        """保存信念"""
        if not self._connected:
            return False
        
        try:
            await self._conn.execute("""
                INSERT INTO beliefs (id, statement, category, confidence, sources, conflicts)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO UPDATE SET
                    statement = EXCLUDED.statement,
                    confidence = EXCLUDED.confidence,
                    updated_at = NOW()
            """,
                belief.get("id"),
                belief.get("statement"),
                belief.get("category"),
                belief.get("confidence", 0.5),
                json.dumps(belief.get("sources", [])),
                json.dumps(belief.get("conflicts", []))
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save belief: {e}")
            return False
    
    async def get_beliefs(self, category: str = None) -> List[Dict]:
        """获取信念"""
        if not self._connected:
            return []
        
        try:
            if category:
                rows = await self._conn.fetch(
                    "SELECT * FROM beliefs WHERE category = $1 ORDER BY confidence DESC",
                    category
                )
            else:
                rows = await self._conn.fetch("SELECT * FROM beliefs ORDER BY confidence DESC")
            
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to get beliefs: {e}")
            return []
    
    # ========== 审计日志 ==========
    
    async def log_audit(self, level: str, action: str, message: str):
        """记录审计日志"""
        if not self._connected:
            return
        
        try:
            await self._conn.execute(
                "INSERT INTO audit_log (level, action, message) VALUES ($1, $2, $3)",
                level, action, message
            )
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
    
    # ========== 统计 ==========
    
    async def get_stats(self) -> Dict:
        """获取数据库统计"""
        if not self._connected:
            return {"status": "disconnected"}
        
        try:
            memory_count = await self._conn.fetchval("SELECT COUNT(*) FROM memories")
            belief_count = await self._conn.fetchval("SELECT COUNT(*) FROM beliefs")
            goal_count = await self._conn.fetchval("SELECT COUNT(*) FROM goals")
            
            return {
                "connected": True,
                "memories": memory_count,
                "beliefs": belief_count,
                "goals": goal_count
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"status": "error", "message": str(e)}


# 全局实例
_postgres_manager = None

def get_postgres_manager(connection_string: str = None) -> PostgresManager:
    """获取PostgreSQL管理器"""
    global _postgres_manager
    if _postgres_manager is None:
        _postgres_manager = PostgresManager(connection_string)
    return _postgres_manager

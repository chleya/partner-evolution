# Partner-Evolution v2.0 技术实施执行手册

**版本**: v2.1  
**编制日期**: 2026-03-02  
**目标**: 生产级可靠性提升

---

## 一、实施概述

### 1.1 改进目标

本次实施旨在将Partner-Evolution v2.0从原型验证阶段提升到生产级可靠性标准。

### 1.2 改进清单

| 优先级 | 任务 | 预计工作量 | 依赖 |
|--------|------|------------|------|
| P0 | 存储层迁移（JSON → PostgreSQL+pgvector） | 4小时 | 无 |
| P0 | 向量检索优化（HNSW索引） | 2小时 | 任务1 |
| P1 | 代码质量审计 | 3小时 | 无 |
| P2 | Grafana可视化集成 | 2小时 | 无 |

### 1.3 技术栈要求

- PostgreSQL 15 + pgvector
- Python 3.10+
- Redis 7
- Grafana (可选)

---

## 二、任务一：存储层迁移

### 2.1 目标

将数据存储从JSON文件迁移到PostgreSQL + pgvector，实现生产级数据持久化。

### 2.2 当前状态

```
data/
├── memory/
│   ├── unified_memory.json      # 当前记忆存储
│   └── vectors/
│       ├── vector_index.json
│       └── vectors.npz
```

### 2.3 实施步骤

#### 步骤1：更新数据库表结构

在 `schema.sql` 中添加新表：

```sql
-- 记忆表（增强版）
CREATE TABLE IF NOT EXISTS memories (
    id VARCHAR(100) PRIMARY KEY,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('core', 'recall', 'archival')),
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    last_edited TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT embedding_dim CHECK (vector_dims(embedding) = 1024)
);

-- HNSW向量索引（核心层）
CREATE INDEX IF NOT EXISTS memory_core_embedding_idx ON memories 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64)
WHERE tier = 'core';

-- HNSW向量索引（回忆层）
CREATE INDEX IF NOT EXISTS memory_recall_embedding_idx ON memories 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64)
WHERE tier = 'recall';

-- 信念表（v2.2准备）
CREATE TABLE IF NOT EXISTS beliefs (
    id VARCHAR(100) PRIMARY KEY,
    content TEXT NOT NULL,
    belief_type VARCHAR(50) NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    evidence JSONB DEFAULT '[]',
    stance VARCHAR(20) DEFAULT 'neutral',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    challenge_history JSONB DEFAULT '[]'
);

-- 自主目标表（v2.2准备）
CREATE TABLE IF NOT EXISTS autonomous_goals (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    goal_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 3,
    progress FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    source VARCHAR(50) DEFAULT 'self_initiated',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### 步骤2：创建数据库连接管理模块

创建文件 `src/core/storage/postgres_manager.py`：

```python
"""
PostgreSQL数据库管理器
支持pgvector向量存储
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DBConfig:
    """数据库配置"""
    host: str
    port: int
    user: str
    password: str
    database: str


class PostgresManager:
    """PostgreSQL管理器"""
    
    def __init__(self, config: DBConfig = None):
        if config is None:
            config = DBConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER", "ai_partner"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_DATABASE", "ai_partner_db")
            )
        self.config = config
        self.conn = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database
            )
            self.conn.autocommit = True
            logger.info("PostgreSQL connected")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            self.conn = None
    
    def execute(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询"""
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """执行查询，返回单条"""
        results = self.execute(query, params)
        return results[0] if results else None
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


class MemoryStorage:
    """记忆存储层 - PostgreSQL实现"""
    
    def __init__(self, postgres_manager: PostgresManager):
        self.db = postgres_manager
    
    # ============== 记忆操作 ==============
    
    def save_memory(
        self,
        memory_id: str,
        tier: str,
        memory_type: str,
        content: str,
        embedding: np.ndarray = None,
        confidence: float = 1.0,
        importance: float = 0.5,
        metadata: Dict = None
    ) -> bool:
        """保存记忆"""
        if not self.db.conn:
            return False
        
        embedding_list = embedding.tolist() if embedding is not None else None
        
        query = """
            INSERT INTO memories (id, tier, memory_type, content, embedding, confidence, importance, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = COALESCE(EXCLUDED.embedding, memories.embedding),
                confidence = EXCLUDED.confidence,
                importance = EXCLUDED.importance,
                metadata = EXCLUDED.metadata,
                last_edited = NOW()
        """
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(query, (
                    memory_id, tier, memory_type, content, 
                    embedding_list, confidence, importance,
                    json.dumps(metadata or {})
                ))
            return True
        except Exception as e:
            logger.error(f"Save memory failed: {e}")
            return False
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取单条记忆"""
        query = "SELECT * FROM memories WHERE id = %s"
        return self.db.execute_one(query, (memory_id,))
    
    def get_memories_by_tier(self, tier: str, limit: int = 100) -> List[Dict]:
        """按层级获取记忆"""
        query = """
            SELECT * FROM memories 
            WHERE tier = %s 
            ORDER BY last_accessed DESC 
            LIMIT %s
        """
        return self.db.execute(query, (tier, limit))
    
    def search_by_vector(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        tier: str = None,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """向量相似度搜索"""
        if not self.db.conn:
            return []
        
        vector_list = query_vector.tolist()
        
        tier_filter = f"AND tier = '{tier}'" if tier else ""
        min_filter = f"AND similarity >= {min_similarity}" if min_similarity > 0 else ""
        
        query = f"""
            SELECT id, tier, memory_type, content, confidence, importance,
                   1 - (embedding <=> %s::vector) as similarity
            FROM memories
            WHERE embedding IS NOT NULL {tier_filter} {min_filter}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        try:
            return self.db.execute(query, (vector_list, vector_list, top_k))
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def update_access_time(self, memory_id: str) -> bool:
        """更新访问时间"""
        query = """
            UPDATE memories 
            SET last_accessed = NOW(), access_count = access_count + 1
            WHERE id = %s
        """
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(query, (memory_id,))
            return True
        except Exception as e:
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        query = "DELETE FROM memories WHERE id = %s"
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(query, (memory_id,))
            return True
        except Exception as e:
            return False
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        query = """
            SELECT 
                tier,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                SUM(access_count) as total_access
            FROM memories
            GROUP BY tier
        """
        results = self.db.execute(query)
        
        stats = {"total": 0, "by_tier": {}, "avg_confidence": 0}
        total_confidence = 0
        total_count = 0
        
        for row in results:
            tier = row["tier"]
            count = row["count"]
            stats["by_tier"][tier] = {
                "count": count,
                "avg_confidence": row["avg_confidence"],
                "total_access": row["total_access"]
            }
            total_count += count
            total_confidence += row["avg_confidence"] * count
        
        stats["total"] = total_count
        stats["avg_confidence"] = total_confidence / total_count if total_count > 0 else 0
        
        return stats
    
    # ============== 数据迁移 ==============
    
    def import_from_json(self, json_path: str) -> int:
        """从JSON文件导入数据"""
        import json
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Load JSON failed: {e}")
            return 0
        
        imported = 0
        for item in data:
            self.save_memory(
                memory_id=item.get("id", f"import_{imported}"),
                tier=item.get("tier", "recall"),
                memory_type=item.get("type", "general"),
                content=item.get("content", ""),
                embedding=np.array(item.get("embedding", [0] * 1024)) if "embedding" in item else None,
                confidence=item.get("confidence", 1.0),
                importance=item.get("importance", 0.5),
                metadata=item.get("metadata", {})
            )
            imported += 1
        
        logger.info(f"Imported {imported} memories from JSON")
        return imported


# 全局实例
_postgres_manager = None
_memory_storage = None

def get_postgres_manager() -> PostgresManager:
    """获取PostgreSQL管理器"""
    global _postgres_manager
    if _postgres_manager is None:
        _postgres_manager = PostgresManager()
    return _postgres_manager

def get_memory_storage() -> MemoryStorage:
    """获取记忆存储"""
    global _memory_storage
    if _memory_storage is None:
        _memory_storage = MemoryStorage(get_postgres_manager())
    return _memory_storage
```

#### 步骤3：更新MemoryManager

修改 `src/core/memory/memory_manager.py`，添加数据库支持：

```python
# 在MemoryManager类中添加：
class MemoryManager:
    def __init__(self, config: Dict = None):
        # ... 现有初始化代码 ...
        
        # 数据库存储（可选）
        self.use_db = os.getenv("USE_DB", "false").lower() == "true"
        if self.use_db:
            try:
                from src.core.storage.postgres_manager import get_memory_storage
                self.db_storage = get_memory_storage()
                logger.info("Using PostgreSQL storage")
            except Exception as e:
                logger.warning(f"DB storage init failed: {e}")
                self.db_storage = None
        else:
            self.db_storage = None
    
    def save_to_db(self, memory: Dict) -> bool:
        """保存到数据库"""
        if not self.db_storage:
            return False
        
        return self.db_storage.save_memory(
            memory_id=memory.get("id", ""),
            tier=memory.get("tier", "recall"),
            memory_type=memory.get("type", "general"),
            content=memory.get("content", ""),
            embedding=memory.get("embedding"),
            confidence=memory.get("confidence", 1.0),
            importance=memory.get("importance", 0.5),
            metadata=memory.get("metadata", {})
        )
    
    def search_in_db(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict]:
        """在数据库中搜索"""
        if not self.db_storage:
            return []
        
        return self.db_storage.search_by_vector(query_vector, top_k)
```

#### 步骤4：创建数据迁移脚本

创建 `scripts/migrate_to_postgres.py`：

```python
#!/usr/bin/env python3
"""
数据迁移脚本：将JSON数据迁移到PostgreSQL
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from src.core.storage.postgres_manager import get_postgres_manager, get_memory_storage

def main():
    print("=" * 60)
    print("Partner-Evolution 数据迁移工具")
    print("=" * 60)
    
    # 连接数据库
    print("\n[1] 连接数据库...")
    db = get_postgres_manager()
    
    if not db.conn:
        print("  错误：无法连接到PostgreSQL")
        print("  请确保PostgreSQL正在运行")
        return
    
    print("  OK: 已连接到PostgreSQL")
    
    # 获取存储
    storage = get_memory_storage()
    
    # 迁移数据
    print("\n[2] 迁移记忆数据...")
    memory_file = "data/memory/unified_memory.json"
    
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        for item in data:
            success = storage.save_memory(
                memory_id=item.get("id", f"migrated_{imported}"),
                tier=item.get("tier", "recall"),
                memory_type=item.get("type", "general"),
                content=item.get("content", ""),
                confidence=item.get("confidence", 1.0),
                importance=item.get("importance", 0.5)
            )
            if success:
                imported += 1
        
        print(f"  OK: 已导入 {imported} 条记忆")
    else:
        print(f"  跳过：{memory_file} 不存在")
    
    # 显示统计
    print("\n[3] 数据库统计...")
    stats = storage.get_memory_stats()
    print(f"  总记忆数: {stats['total']}")
    for tier, info in stats['by_tier'].items():
        print(f"  - {tier}: {info['count']} 条 (平均置信度: {info['avg_confidence']:.2f})")
    
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### 2.4 验证步骤

```bash
# 1. 启动PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ai_partner_db \
  -v postgres-data:/var/lib/postgresql/data \
  pgvector/pgvector:pg15

# 2. 初始化表结构
psql -h localhost -U ai_partner -d ai_partner_db -f schema.sql

# 3. 运行迁移
python scripts/migrate_to_postgres.py

# 4. 验证
python -c "
from src.core.storage.postgres_manager import get_memory_storage
s = get_memory_storage()
print(s.get_memory_stats())
"
```

---

## 三、任务二：向量检索优化

### 3.1 目标

引入HNSW索引，提升向量检索效率和准确率。

### 3.2 实施步骤

#### 步骤1：更新向量存储模块

修改 `src/core/memory/vector_store.py`：

```python
"""
向量存储 - 优化版
支持HNSW索引和多种相似度计算
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """向量存储"""
    
    def __init__(
        self,
        dimension: int = 1024,
        index_type: str = "hnsw",  # hnsw, flat, ivf
        metric: str = "cosine"
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.metric = metric
        self.vectors = []
        self.metadata = []
        
        # HNSW参数
        self.ef_construction = 64
        self.ef_search = 32
        self.m = 16
        
        # 初始化索引
        self._init_index()
    
    def _init_index(self):
        """初始化索引"""
        if self.index_type == "hnsw":
            try:
                import hnswlib
                self.index = hnswlib.HNSWIndex(
                    space='cosine',
                    dim=self.dimension
                )
                self.index.init_index(
                    max_elements=10000,
                    ef_construction=self.ef_construction,
                    M=self.m
                )
                self.index.set_ef(self.ef_search)
                logger.info("HNSW index initialized")
            except ImportError:
                logger.warning("hnswlib not installed, using numpy")
                self.index = None
        else:
            self.index = None
    
    def add_vector(
        self,
        vector: np.ndarray,
        metadata: Dict = None
    ) -> int:
        """添加向量"""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}")
        
        idx = len(self.vectors)
        self.vectors.append(vector.astype(np.float32))
        self.metadata.append(metadata or {})
        
        if self.index is not None and hasattr(self.index, 'add_items'):
            self.index.add_items(vector.reshape(1, -1), [idx])
        
        return idx
    
    def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        min_score: float = 0.0
    ) -> List[Tuple[int, float, Dict]]:
        """搜索相似向量"""
        if len(query) != self.dimension:
            raise ValueError(f"Query dimension must be {self.dimension}")
        
        query = query.astype(np.float32).reshape(1, -1)
        
        if self.index is not None and hasattr(self.index, 'knn_query'):
            # HNSW搜索
            labels, distances = self.index.knn_query(query, k=top_k)
            
            results = []
            for i, label in enumerate(labels[0]):
                score = 1 - distances[0][i]  # 转换为相似度
                if score >= min_score:
                    results.append((int(label), score, self.metadata[int(label)]))
        else:
            # 暴力搜索
            scores = []
            for i, v in enumerate(self.vectors):
                score = self._cosine_similarity(query.flatten(), v)
                if score >= min_score:
                    scores.append((i, score, self.metadata[i]))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            results = scores[:top_k]
        
        return results
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算余弦相似度"""
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))
    
    def save(self, path: str):
        """保存索引"""
        if self.index is not None and hasattr(self.index, 'save_index'):
            self.index.save_index(path)
        
        # 保存元数据
        import json
        meta_path = path.replace('.bin', '_meta.json')
        with open(meta_path, 'w') as f:
            json.dump({
                'vectors': self.vectors,
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)
    
    def load(self, path: str):
        """加载索引"""
        if self.index is not None and hasattr(self.index, 'load_index'):
            self.index.load_index(path)
        
        import json
        meta_path = path.replace('.bin', '_meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                data = json.load(f)
                self.vectors = [np.array(v) for v in data['vectors']]
                self.metadata = data['metadata']


# 依赖安装
REQUIREMENTS = """
# 向量检索优化
hnswlib>=0.8.0
"""
```

### 3.3 验证步骤

```python
# 测试向量搜索性能
import time
import numpy as np
from src.core.memory.vector_store import VectorStore

# 创建索引
store = VectorStore(dimension=384, index_type="hnsw")

# 添加10000条向量
for i in range(10000):
    vec = np.random.randn(384).astype(np.float32)
    store.add_vector(vec, {"id": f"vec_{i}"})

# 搜索测试
query = np.random.randn(384).astype(np.float32)

start = time.time()
results = store.search(query, top_k=10)
elapsed = time.time() - start

print(f"搜索时间: {elapsed*1000:.2f}ms")
print(f"结果数: {len(results)}")
```

---

## 四、任务三：代码质量审计

### 4.1 目标

确保代码质量，发现并修复潜在问题。

### 4.2 审计清单

| 检查项 | 工具 | 命令 |
|--------|------|------|
| 语法检查 | py_compile | `python -m py_compile <file>` |
| 类型检查 | mypy | `mypy src/` |
| 代码风格 | black | `black --check src/` |
| 安全扫描 | bandit | `bandit -r src/` |
| 复杂度 | radon | `radon cc src/` |

### 4.3 常用修复

```python
# 1. 异常处理完善
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # 优雅降级
    result = fallback_value

# 2. 资源清理
try:
    resource = acquire_resource()
    use(resource)
finally:
    resource.release()  # 或使用 context manager

# 3. 输入验证
def process_input(data: Dict) -> bool:
    if not isinstance(data, dict):
        return False
    if "required_field" not in data:
        return False
    # ... 更多验证
```

---

## 五、任务四：Grafana集成（可选）

### 5.1 目标

将系统指标接入Grafana可视化。

### 5.2 配置文件

创建 `grafana/provisioning/dashboards/partner_evolution.json`：

```json
{
  "dashboard": {
    "title": "Partner-Evolution 监控",
    "tags": ["partner-evolution"],
    "timezone": "browser",
    "panels": [
      {
        "title": "请求量",
        "type": "graph",
        "targets": [
          {
            "expr": "partner_evolution_requests_total",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(partner_evolution_errors_total[5m])",
            "legendFormat": "{{type}}"
          }
        ]
      },
      {
        "title": "响应延迟",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, partner_evolution_latency_seconds_bucket)",
            "legendFormat": "p95"
          }
        ]
      }
    ]
  }
}
```

---

## 六、部署指南

### 6.1 Docker Compose（生产）

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

### 6.2 环境变量

```bash
# 数据库
export DB_HOST=postgres
export DB_PORT=5432
export DB_USER=ai_partner
export DB_PASSWORD=your_secure_password
export DB_DATABASE=ai_partner_db

# Redis
export REDIS_HOST=redis
export REDIS_PORT=6379

# LLM
export LLM_API_KEY=your_minimax_api_key

# 功能开关
export USE_DB=true
```

---

## 七、测试验证

### 7.1 单元测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定模块测试
python -m pytest tests/test_phase1.py -v
python -m pytest tests/test_week2_*.py -v
```

### 7.2 集成测试

```bash
# 启动服务
python main.py &

# 测试API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/status
```

### 7.3 性能测试

```bash
# 压力测试
python -c "
import requests
import time

url = 'http://localhost:5000/api/status'
start = time.time()

for i in range(100):
    requests.get(url)

elapsed = time.time() - start
print(f'100 requests in {elapsed:.2f}s')
print(f'Average: {elapsed/100*1000:.2f}ms')
"
```

---

## 八、回滚方案

### 8.1 数据库回滚

```sql
-- 删除新表，保留旧数据
DROP TABLE IF EXISTS memories CASCADE;
DROP TABLE IF EXISTS beliefs CASCADE;
DROP TABLE IF EXISTS autonomous_goals CASCADE;
```

### 8.2 代码回滚

```bash
# 回滚到上一个版本
git checkout HEAD~1 -- src/

# 或使用Docker回滚
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml pull <previous-tag>
docker-compose -f docker-compose.prod.yml up -d
```

---

## 九、检查清单

### 实施前

- [ ] PostgreSQL已安装/启动
- [ ] 数据库用户已创建
- [ ] 备份当前数据

### 实施中

- [ ] schema.sql已执行
- [ ] 数据迁移完成
- [ ] 向量索引已优化

### 实施后

- [ ] 所有测试通过
- [ ] API响应正常
- [ ] 监控数据正常

---

**编制**: MiniMax Agent  
**审核**: 待Chen Leiyang审核  
**版本**: v2.1-实施手册

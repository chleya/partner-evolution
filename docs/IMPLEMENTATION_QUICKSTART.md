# Partner-Evolution v2.1 执行手册 - 速查版

## 任务清单

| 优先级 | 任务 | 预计时间 |
|--------|------|----------|
| P0 | 存储层迁移 (JSON→PostgreSQL) | 4小时 |
| P0 | 向量检索优化 (HNSW) | 2小时 |
| P1 | 代码质量审计 | 3小时 |
| P2 | Grafana集成 | 2小时 |

---

## 快速开始

### 1. 启动PostgreSQL

```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ai_partner_db \
  pgvector/pgvector:pg15
```

### 2. 初始化数据库

```bash
psql -h localhost -U postgres -d ai_partner_db -f schema.sql
```

### 3. 运行迁移

```bash
python scripts/migrate_to_postgres.py
```

### 4. 验证

```bash
python main.py &
curl http://localhost:5000/api/health
```

---

## 核心文件

| 文件 | 用途 |
|------|------|
| `schema.sql` | 数据库表结构 |
| `src/core/storage/postgres_manager.py` | 数据库管理器 |
| `scripts/migrate_to_postgres.py` | 数据迁移脚本 |
| `src/core/memory/vector_store.py` | 向量存储(HNSW) |
| `grafana/` | 可视化配置 |

---

## 常见问题

**Q: PostgreSQL连接失败?**
A: 检查容器是否运行 `docker ps`

**Q: 向量索引加载慢?**
A: 首次加载正常，后续会缓存

**Q: 数据迁移丢失?**
A: 先备份 `data/memory/` 目录

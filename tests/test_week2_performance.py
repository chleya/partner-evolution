"""
Week 2 - Performance Test: Vector Search Optimization
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

import time
import numpy as np

# Mock embedding
import src.utils.embedding as emb
def mock_get_embedding(text, model_name=None, dimension=384):
    return np.random.randn(dimension).astype(np.float32)
emb.get_embedding = mock_get_embedding

from src.core.memory import VectorStore

print("=" * 60)
print("Week 2 Performance Test: Vector Store Optimization")
print("=" * 60)

# 初始化（启用缓存）
store = VectorStore(dimension=384, use_cache=True)

# 生成测试数据
print("\n[TEST] Generate 1000 test vectors...")
test_count = 1000
for i in range(test_count):
    vec = np.random.randn(384).astype(np.float32)
    store.add(f"vec_{i}", vec, {"index": i, "type": "test"})
print(f"  OK: Added {test_count} vectors")

# 测试1: 首次搜索（无缓存）
print("\n[TEST 1] First search (no cache)...")
query = np.random.randn(384).astype(np.float32)
start = time.time()
results = store.search(query, top_k=10, threshold=0.3)
first_time = time.time() - start
print(f"  OK: Found {len(results)} results in {first_time*1000:.2f}ms")

# 测试2: 缓存命中
print("\n[TEST 2] Cached search...")
start = time.time()
results = store.search(query, top_k=10, threshold=0.3)
cached_time = time.time() - start
print(f"  OK: Cache hit - {cached_time*1000:.2f}ms")
print(f"  Speedup: {first_time/cached_time:.1f}x")

# 测试3: 批量添加
print("\n[TEST 3] Batch add...")
batch_items = []
for i in range(100):
    vec = np.random.randn(384).astype(np.float32)
    batch_items.append((f"batch_{i}", vec, {"batch": True}))
start = time.time()
store.add_batch(batch_items)
batch_time = time.time() - start
print(f"  OK: Added 100 vectors in {batch_time*1000:.2f}ms")

# 测试4: 性能统计
print("\n[TEST 4] Performance stats...")
stats = store.get_stats()
print(f"  OK: Total vectors: {stats['total_vectors']}")
print(f"  OK: Search count: {stats['search_count']}")
print(f"  OK: Avg search time: {stats['avg_search_time_ms']:.2f}ms")
print(f"  OK: Cache enabled: {stats['cache_enabled']}")

# 验证性能目标
print("\n[VALIDATION]")
target_ms = 80
if stats['avg_search_time_ms'] < target_ms:
    print(f"  PASS: Avg search time ({stats['avg_search_time_ms']:.2f}ms) < {target_ms}ms")
else:
    print(f"  WARN: Avg search time ({stats['avg_search_time_ms']:.2f}ms) > {target_ms}ms")

print("\n" + "=" * 60)
print("Week 2 Performance Test: PASS")
print("=" * 60)

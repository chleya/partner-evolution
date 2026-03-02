"""
第一阶段测试脚本 - 记忆系统 (简化版，无需下载模型)
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

# Mock embedding function to avoid downloading model
import numpy as np
import src.utils.embedding as emb

original_get_embedding = emb.get_embedding

def mock_get_embedding(text, model_name=None, dimension=384):
    """Mock embedding - returns random vector"""
    return np.random.randn(dimension).astype(np.float32)

emb.get_embedding = mock_get_embedding

from src.core.memory import MemoryManager, MemoryTier

print("=" * 50)
print("Phase 1 Test: Memory System")
print("=" * 50)

# 初始化记忆管理器
print("\n[1] Initialize Memory Manager...")
memory = MemoryManager(
    base_path=r'F:\ai_partner_evolution\data\memory',
    config={"dimension": 384, "top_k": 5, "threshold": 0.3}
)
print(f"OK: Memory Manager initialized")
print(f"   Version: {memory.unified_memory.get('version')}")

# 添加对话记录
print("\n[2] Add conversation...")
conv_id = memory.add_conversation(
    user="Chen Leiyang",
    content="优化AI助手能力，让它成为真正的伙伴",
    intent="enhancement",
    outcome="completed",
    quality_score=0.85
)
print(f"OK: Added conversation: {conv_id}")

# 添加实体
print("\n[3] Add entities...")
entity_id = memory.add_entity(
    entity_type="project",
    name="NeuralSite",
    aliases=["智网六维时空施工管理系统", "施工管理系统"],
    attributes={"location": r"F:\drawing_3d", "stage": "Stage4", "status": "active"},
    confidence=0.95
)
print(f"OK: Added entity: {entity_id}")

entity_id2 = memory.add_entity(
    entity_type="project",
    name="Evo-Swarm",
    aliases=["演化智能体", "思维链系统"],
    attributes={"location": r"F:\skill\evo_swarm", "github": "https://github.com/chleya/Evo-Swarm"},
    confidence=0.95
)
print(f"OK: Added entity: {entity_id2}")

# 添加关联
print("\n[4] Add relation...")
memory.add_relation(
    from_entity_name="NeuralSite",
    to_entity_name="Evo-Swarm",
    relation_type="collaborates_with",
    description="Evo-Swarm提供思维链能力支撑NeuralSite",
    strength=0.8
)
print(f"OK: Added relation")

# 添加任务
print("\n[5] Add task...")
task_id = memory.add_task_record(
    project="Partner-Evolution",
    description="实现记忆系统v2.0",
    status="in_progress"
)
print(f"OK: Added task: {task_id}")

# 更新任务进度
print("\n[6] Update task progress...")
memory.update_task_progress(task_id, 0.6)
print(f"OK: Task progress updated to 60%")

# 测试向量检索
print("\n[7] Test vector search (mock)...")
result = memory.paginate_memory("AI助手 优化 能力", max_tokens=1000)
print(f"OK: Search completed")
print(f"   Retrieved memories: {len(result['context_memories'])}")

# 关键词搜索
print("\n[8] Keyword search...")
search_result = memory.search_memory("NeuralSite")
print(f"OK: Search completed")
print(f"   Found entities: {len(search_result['entities'])}")
for e in search_result['entities']:
    print(f"   - {e['name']} ({e['type']})")

# 获取能力状态
print("\n[9] Update capability...")
memory.update_capability("vector_search", level=3, confidence=0.8)
caps = memory.get_capabilities()
print(f"OK: Capability updated")
print(f"   Current capabilities: {list(caps.keys())}")

# 获取记忆统计
print("\n[10] Memory statistics...")
full = memory.get_full_memory()
layers = full.get('layers', {})
raw = layers.get('raw_memory', {})
sem = layers.get('semantic_memory', {})
print(f"OK: Memory stats:")
print(f"   Conversations: {len(raw.get('conversations', []))}")
print(f"   Tasks: {len(raw.get('task_records', []))}")
print(f"   Entities: {len(sem.get('entities', []))}")
print(f"   Relations: {len(sem.get('relations', []))}")

# 测试遗忘曲线
print("\n[11] Test forgetting curve...")
memory.apply_forgetting()
print(f"OK: Forgetting applied")

# 查看数据文件
import os
print("\n[12] Data files created:")
data_dir = r'F:\ai_partner_evolution\data\memory'
for f in os.listdir(data_dir):
    fpath = os.path.join(data_dir, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        print(f"   {f}: {size} bytes")

print("\n" + "=" * 50)
print("SUCCESS: Phase 1 Test Passed!")
print("=" * 50)

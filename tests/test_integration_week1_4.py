"""
Week 1-4 完整集成测试
验证所有模块协同工作
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

import numpy as np

# Mock embedding
import src.utils.embedding as emb
def mock_get_embedding(text, model_name=None, dimension=384):
    return np.random.randn(dimension).astype(np.float32)
emb.get_embedding = mock_get_embedding

from src.core.memory import MemoryManager, MemoryTier
from src.core.thinking import ThinkEngine, ThinkingMode
from src.core.orchestration import SupervisorAgent, LangGraphWorkflow

print("=" * 70)
print("INTEGRATION TEST: Week 1-4 Complete")
print("=" * 70)

# ==================== 模块1: 记忆系统 ====================
print("\n[MODULE 1] Memory System")
print("-" * 50)

memory = MemoryManager(
    base_path=r'F:\ai_partner_evolution\data\memory',
    config={"dimension": 384, "top_k": 5, "threshold": 0.3}
)

# 添加项目实体
memory.add_entity("project", "NeuralSite", ["智网"], {"stage": "Stage4"}, 0.95)
memory.add_entity("project", "Evo-Swarm", ["演化智能体"], {"status": "active"}, 0.95)
memory.add_entity("project", "Partner-Evolution", ["PE"], {"phase": "Week4"}, 0.9)

# 添加记忆
conv_id = memory.add_conversation("Chen", "开始Week 4测试", "test", "completed", 0.8)
task_id = memory.add_task_record("Partner-Evolution", "完成集成测试", "in_progress")

print(f"  OK: Entities: {len(memory.unified_memory['layers']['semantic_memory']['entities'])}")
print(f"  OK: Conversations: {len(memory.unified_memory['layers']['raw_memory']['conversations'])}")

# ==================== 模块2: 思考引擎 ====================
print("\n[MODULE 2] Thinking Engine")
print("-" * 50)

thinker = ThinkEngine(memory, config={"target_daily_thinks": 5, "enable_mar": True})

# 执行MAR反思
context = {
    "task": "完成集成测试",
    "project": "Partner-Evolution",
    "projects": {
        "Partner-Evolution": {"status": "in_progress", "progress": 0.8}
    }
}
result = thinker.think(ThinkingMode.MAR_REFLECTION, context)

print(f"  OK: MAR Confidence: {result.get('confidence')}")
print(f"  OK: Perspectives: {len(result.get('mar_result', {}).get('perspectives', []))}")
print(f"  OK: Total thinks: {thinker.stats['total_thinks']}")

# ==================== 模块3: 编排系统 ====================
print("\n[MODULE 3] Orchestration System")
print("-" * 50)

supervisor = SupervisorAgent()
workflow = LangGraphWorkflow(supervisor)

# 执行工作流
task = "分析NeuralSite截图，结合Evo-Swarm给出部署方案"
workflow_result = workflow.run(task, {"priority": "high"})

print(f"  OK: Workflow steps: {len(workflow_result['state']['thinking_results']) + 2}")
print(f"  OK: Projects: {workflow_result['result']['final_result']['projects_involved']}")
print(f"  OK: Checkpoints: {len(workflow.checkpoints)}")

# ==================== 跨模块协作 ====================
print("\n[MODULE 4] Cross-Module Integration")
print("-" * 50)

# 记忆 → 思考：使用记忆上下文
memory_context = memory.paginate_memory("Week 4 测试")
print(f"  OK: Retrieved memories: {len(memory_context['context_memories'])}")

# 思考 → 记忆：保存反思结果
memory.add_conversation(
    "System",
    f"MAR反思结果: {result.get('summary')}",
    "reflection",
    "completed",
    result.get('confidence', 0.5)
)
print(f"  OK: Reflection saved to memory")

# 编排 → 记忆：记录工作流
memory.add_task_record(
    "Partner-Evolution",
    f"完成工作流: {task}",
    "completed"
)
print(f"  OK: Workflow saved to memory")

# ==================== 统计 ====================
print("\n[MODULE 5] System Statistics")
print("-" * 50)

# 记忆统计
full_memory = memory.get_full_memory()
print(f"  Memory Version: {full_memory.get('version')}")
print(f"  Entities: {len(full_memory['layers']['semantic_memory']['entities'])}")
print(f"  Relations: {len(full_memory['layers']['semantic_memory']['relations'])}")

# 思考统计
stats = thinker.get_stats()
print(f"  Total Thinks: {stats['total_thinks']}")
print(f"  MAR Reflections: {stats['mar_reflections']}")

# 编排统计
projects = supervisor.get_available_projects()
print(f"  Active Projects: {len(projects)}")
print(f"  Workflows Run: {len(supervisor.workflow_history)}")

# ==================== 验证 ====================
print("\n[VALIDATION]")
print("-" * 50)

checks = [
    ("Memory System", len(full_memory['layers']['semantic_memory']['entities']) >= 3),
    ("Thinking Engine", stats['total_thinks'] >= 1),
    ("MAR Framework", stats['mar_reflections'] >= 1),
    ("Supervisor", len(projects) >= 3),
    ("Workflow", workflow_result is not None),
    ("Integration", len(memory_context['context_memories']) >= 1),
]

all_passed = True
for name, passed in checks:
    status = "PASS" if passed else "FAIL"
    print(f"  {name}: {status}")
    if not passed:
        all_passed = False

print("\n" + "=" * 70)
print("INTEGRATION TEST SUMMARY")
print("=" * 70)
print(f"  Modules Tested: 5")
print(f"  Checks Passed: {sum(1 for _, p in checks if p)}/{len(checks)}")
print(f"  Status: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
print("=" * 70)

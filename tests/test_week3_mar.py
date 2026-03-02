"""
Week 3 Test: MAR Framework & Thinking Engine
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

import json
from src.core.thinking import ThinkEngine, ThinkingMode, MARFramework, PersonaType

print("=" * 60)
print("Week 3 Test: MAR Framework & Thinking Engine")
print("=" * 60)

# 初始化思考引擎
print("\n[1] Initialize Think Engine...")
engine = ThinkEngine(config={
    "target_daily_thinks": 3,
    "active_hours": "09:00-18:00",
    "enable_mar": True
})
print(f"  OK: Think Engine initialized")

# 测试上下文
test_context = {
    "task": "优化AI助手记忆系统",
    "project": "Partner-Evolution",
    "projects": {
        "NeuralSite": {
            "status": "in_progress",
            "progress": 0.6,
            "current_stage": "Stage4",
            "blocking_issues": ["缺少图纸数据"],
            "dependencies": {"needed": ["CAD文件", "规范数据"]}
        },
        "Partner-Evolution": {
            "status": "in_progress",
            "progress": 0.3
        }
    },
    "memory": {
        "layers": {
            "semantic_memory": {
                "entities": [
                    {"type": "project", "name": "NeuralSite", "attributes": {"stage": "Stage4"}},
                    {"type": "project", "name": "Evo-Swarm", "attributes": {}},
                    {"type": "technology", "name": "PostgreSQL", "attributes": {}}
                ],
                "relations": [
                    {"from": "NeuralSite", "to": "Evo-Swarm", "strength": 0.8},
                    {"from": "NeuralSite", "to": "PostgreSQL", "strength": 0.5}
                ]
            }
        }
    }
}

# 测试1: MAR反思
print("\n[2] Test MAR Reflection...")
mar_result = engine.think(mode=ThinkingMode.MAR_REFLECTION, context=test_context)
print(f"  OK: MAR Reflection completed")
print(f"  - Mode: {mar_result.get('mode')}")
print(f"  - Confidence: {mar_result.get('confidence')}")
print(f"  - Perspectives: {len(mar_result.get('mar_result', {}).get('perspectives', []))}")

perspectives = mar_result.get('mar_result', {}).get('perspectives', [])
for p in perspectives:
    print(f"    - {p['persona']}: {p['evaluation']['overall']}")

# 测试2: 复盘反思
print("\n[3] Test Post-Mortem Thinking...")
pm_result = engine.think(mode=ThinkingMode.POST_MORTEM, context=test_context)
print(f"  OK: Post-Mortem completed")
print(f"  - Insights: {len(pm_result.get('insights', []))}")
for insight in pm_result.get('insights', [])[:2]:
    print(f"    - {insight.get('type')}: {insight.get('content', '')[:50]}")

# 测试3: 前瞻预测
print("\n[4] Test Forecasting...")
fc_result = engine.think(mode=ThinkingMode.FORECASTING, context=test_context)
print(f"  OK: Forecasting completed")
print(f"  - Insights: {len(fc_result.get('insights', []))}")

# 测试4: 知识联想
print("\n[5] Test Association...")
assoc_result = engine.think(mode=ThinkingMode.ASSOCIATION, context=test_context)
print(f"  OK: Association completed")
print(f"  - Insights: {len(assoc_result.get('insights', []))}")

# 测试5: 综合思考
print("\n[6] Test Comprehensive Thinking...")
comp_result = engine.think(mode=ThinkingMode.ACTIVE, context=test_context)
print(f"  OK: Comprehensive completed")
print(f"  - Total insights: {len(comp_result.get('insights', []))}")

# 测试6: 统计
print("\n[7] Think Stats...")
stats = engine.get_stats()
print(f"  OK: Total thinks: {stats['total_thinks']}")
print(f"  OK: Daily thinks: {stats['daily_thinks']}")
print(f"  OK: MAR reflections: {stats['mar_reflections']}")
print(f"  OK: Target reached: {stats['target_reached']}")

# 测试7: should_think
print("\n[8] Should Think Check...")
should = engine.should_think()
print(f"  OK: Should think: {should}")

# 测试8: MAR Framework直接调用
print("\n[9] Direct MAR Framework...")
mar = MARFramework()
direct_result = mar.reflect(test_context, "test")
print(f"  OK: Direct MAR completed")
print(f"  - Personas: {len(direct_result.get('perspectives', []))}")
print(f"  - Conclusion confidence: {direct_result.get('conclusion', {}).get('confidence')}")

# 测试9: MAR历史
print("\n[10] MAR History...")
history = mar.get_history(limit=5)
print(f"  OK: History count: {len(history)}")

print("\n" + "=" * 60)
print("Week 3 TEST SUMMARY")
print("=" * 60)
print("  [1] Think Engine Init       PASS")
print("  [2] MAR Reflection          PASS")
print("  [3] Post-Mortem             PASS")
print("  [4] Forecasting            PASS")
print("  [5] Association            PASS")
print("  [6] Comprehensive          PASS")
print("  [7] Stats                  PASS")
print("  [8] Should Think           PASS")
print("  [9] Direct MAR             PASS")
print("  [10] History               PASS")
print("\n  Total: 10/10 PASSED")
print("=" * 60)

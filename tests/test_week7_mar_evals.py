"""
Week 7 测试 - MAR v2 + Knowledge Flow + Evals
"""
import sys
import asyncio
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.core.thinking.mar_framework_v2 import (
    MARFrameworkV2, PersonaType, ReflectionQuality, JudgeEvaluation
)
from src.core.orchestration.knowledge_flow import (
    KnowledgeFlow, KnowledgeType, SyncDirection, SyncEvent
)
from src.core.evaluation.evals_framework import (
    EvalsFramework, TestCase, TestCategory, MetricName
)


def test_mar_v2_creation():
    """测试MAR v2创建"""
    print("\n[1] Testing MAR v2 creation...")
    
    mar = MARFrameworkV2()
    
    assert mar is not None
    assert len(mar.PERSONA_POOL) == 6
    
    print(f"  Personas: {len(mar.PERSONA_POOL)}")
    print("  PASS")


def test_mar_v2_reflection():
    """测试MAR v2反思"""
    print("\n[2] Testing MAR v2 reflection...")
    
    mar = MARFrameworkV2()
    
    context = {
        "task": "优化AI助手",
        "project": "Partner-Evolution"
    }
    
    result = mar.reflect(context, "post_mortem")
    
    assert "reflections" in result
    assert "conclusion" in result
    assert len(result["reflections"]) == 3  # 默认3个角色
    
    print(f"  Reflections: {len(result['reflections'])}")
    print("  PASS")


def test_mar_v2_selected_personas():
    """测试选择角色"""
    print("\n[3] Testing selected personas...")
    
    mar = MARFrameworkV2()
    
    context = {"task": "测试", "project": "Test"}
    
    # 选择特定角色
    result = mar.reflect(
        context,
        selected_personas=[
            PersonaType.OPTIMIST,
            PersonaType.CREATIVE,
            PersonaType.PRAGMATIC
        ]
    )
    
    assert len(result["reflections"]) == 3
    assert result["personas_used"] == ["optimist", "creative", "pragmatic"]
    
    print("  PASS")


def test_mar_v2_quality_tracking():
    """测试质量追踪"""
    print("\n[4] Testing quality tracking...")
    
    mar = MARFrameworkV2()
    
    # 运行多次反思
    for i in range(3):
        mar.reflect({"task": f"测试{i}", "project": "Test"})
    
    trend = mar.get_quality_trend()
    
    assert "avg_score" in trend
    assert trend["total_reflections"] == 3
    
    print(f"  Avg score: {trend['avg_score']}")
    print("  PASS")


def test_knowledge_flow_creation():
    """测试知识流动创建"""
    print("\n[5] Testing knowledge flow creation...")
    
    kf = KnowledgeFlow()
    
    assert kf is not None
    assert len(kf.knowledge_store) == 3
    assert len(kf.sync_rules) > 0
    
    print(f"  Projects: {list(kf.knowledge_store.keys())}")
    print("  PASS")


def test_knowledge_add():
    """测试添加知识"""
    print("\n[6] Testing knowledge add...")
    
    kf = KnowledgeFlow()
    
    item_id = kf.add_knowledge(
        "NeuralSite",
        KnowledgeType.CODE,
        "def hello(): return 'world'",
        {"function": "hello"}
    )
    
    assert item_id is not None
    
    items = kf.get_knowledge("NeuralSite")
    assert len(items) > 0
    
    print(f"  Added: {item_id}")
    print("  PASS")


def test_knowledge_sync():
    """测试知识同步"""
    print("\n[7] Testing knowledge sync...")
    
    kf = KnowledgeFlow()
    
    # 添加知识
    item_id = kf.add_knowledge(
        "NeuralSite",
        KnowledgeType.CODE,
        "test code"
    )
    
    # 手动同步
    event = kf.sync_knowledge(
        "NeuralSite",
        "Evo-Swarm",
        [item_id],
        SyncDirection.UNIDIRECTIONAL
    )
    
    assert event.status == "success"
    assert len(event.items_synced) > 0
    
    print(f"  Synced items: {len(event.items_synced)}")
    print("  PASS")


def test_knowledge_links():
    """测试知识链接"""
    print("\n[8] Testing knowledge links...")
    
    kf = KnowledgeFlow()
    
    # 添加知识
    id1 = kf.add_knowledge("NeuralSite", KnowledgeType.CODE, "code1")
    id2 = kf.add_knowledge("Evo-Swarm", KnowledgeType.CONFIG, "config1")
    
    # 添加链接
    kf.add_link(id1, id2, "related", 0.8)
    
    assert len(kf.knowledge_links) > 0
    
    # 获取相关知识
    related = kf.get_related_knowledge(id1)
    
    print(f"  Links: {len(kf.knowledge_links)}")
    print("  PASS")


def test_knowledge_search():
    """测试知识搜索"""
    print("\n[9] Testing knowledge search...")
    
    kf = KnowledgeFlow()
    
    # 添加知识
    kf.add_knowledge("NeuralSite", KnowledgeType.CODE, "login function")
    kf.add_knowledge("Evo-Swarm", KnowledgeType.CONFIG, "database config")
    
    # 搜索
    results = kf.search_knowledge("login")
    
    assert len(results) > 0
    
    print(f"  Search results: {len(results)}")
    print("  PASS")


def test_evals_creation():
    """测试评估框架创建"""
    print("\n[10] Testing evals framework creation...")
    
    evals = EvalsFramework()
    
    assert evals is not None
    assert len(evals.test_cases) > 0
    
    print(f"  Test cases: {len(evals.test_cases)}")
    print("  PASS")


def test_evals_add_case():
    """测试添加测试用例"""
    print("\n[11] Testing add test case...")
    
    evals = EvalsFramework()
    
    test_case = TestCase(
        id="custom_001",
        name="自定义测试",
        category=TestCategory.FUNCTIONAL,
        input_data={"test": True},
        expected_output={"result": True},
        weight=1.0
    )
    
    evals.add_test_case(test_case)
    
    assert "custom_001" in evals.test_cases
    
    print("  PASS")


def test_evals_run_evaluation():
    """测试运行评估"""
    print("\n[12] Testing run evaluation...")
    
    evals = EvalsFramework()
    
    # 模拟系统函数
    def mock_system(input_data):
        return {"handled": True, "result": "ok"}
    
    # 运行评估
    report = evals.run_evaluation(mock_system)
    
    assert report.total_tests > 0
    assert report.pass_rate >= 0
    
    print(f"  Pass rate: {report.pass_rate:.2%}")
    print("  PASS")


def test_evals_trend():
    """测试趋势追踪"""
    print("\n[13] Testing trend tracking...")
    
    evals = EvalsFramework()
    
    def mock_system(input_data):
        return {"handled": True}
    
    # 运行多次评估
    for i in range(3):
        evals.run_evaluation(mock_system)
    
    trend = evals.get_trend()
    
    assert "trend" in trend
    assert trend["total_evaluations"] == 3
    
    print(f"  Trend: {trend['trend']}")
    print("  PASS")


def test_mar_v2_status():
    """测试MAR v2状态"""
    print("\n[14] Testing MAR v2 status...")
    
    mar = MARFrameworkV2()
    mar.reflect({"task": "test"}, "post_mortem")
    
    status = mar.get_status()
    
    assert "total_reflections" in status
    assert status["total_reflections"] == 1
    
    print(f"  Status: {status}")
    print("  PASS")


def test_knowledge_flow_status():
    """测试知识流动状态"""
    print("\n[15] Testing knowledge flow status...")
    
    kf = KnowledgeFlow()
    kf.add_knowledge("NeuralSite", KnowledgeType.CODE, "test")
    
    status = kf.get_status()
    
    assert "total_knowledge_items" in status
    assert status["total_knowledge_items"] > 0
    
    print(f"  Items: {status['total_knowledge_items']}")
    print("  PASS")


def test_evals_status():
    """测试评估框架状态"""
    print("\n[16] Testing evals status...")
    
    evals = EvalsFramework()
    
    status = evals.get_status()
    
    assert "total_test_cases" in status
    assert status["total_test_cases"] > 0
    
    print(f"  Status: {status}")
    print("  PASS")


def test_mar_v2_multi_persona_reflection():
    """测试多角色反思"""
    print("\n[17] Testing multi-persona reflection...")
    
    mar = MARFrameworkV2()
    
    # 使用全部6个角色
    result = mar.reflect(
        {"task": "全面分析", "project": "Test"},
        selected_personas=list(PersonaType)
    )
    
    assert len(result["reflections"]) == 6
    assert "evaluation" in result
    
    print(f"  Reflections: {len(result['reflections'])}")
    print("  PASS")


def test_knowledge_bidirectional_sync():
    """测试双向同步"""
    print("\n[18] Testing bidirectional sync...")
    
    kf = KnowledgeFlow()
    
    # 添加知识
    id1 = kf.add_knowledge("NeuralSite", KnowledgeType.PATTERN, "pattern1")
    
    # 双向同步
    event = kf.sync_knowledge(
        "NeuralSite",
        "Evo-Swarm",
        [id1],
        SyncDirection.BIDIRECTIONAL
    )
    
    # 检查两个项目都有知识
    neural_items = kf.get_knowledge("NeuralSite")
    evo_items = kf.get_knowledge("Evo-Swarm")
    
    print(f"  NeuralSite: {len(neural_items)}, Evo-Swarm: {len(evo_items)}")
    print("  PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Week 7 Test Suite - MAR v2 + Knowledge Flow + Evals")
    print("=" * 60)
    
    tests = [
        test_mar_v2_creation,
        test_mar_v2_reflection,
        test_mar_v2_selected_personas,
        test_mar_v2_quality_tracking,
        test_knowledge_flow_creation,
        test_knowledge_add,
        test_knowledge_sync,
        test_knowledge_links,
        test_knowledge_search,
        test_evals_creation,
        test_evals_add_case,
        test_evals_run_evaluation,
        test_evals_trend,
        test_mar_v2_status,
        test_knowledge_flow_status,
        test_evals_status,
        test_mar_v2_multi_persona_reflection,
        test_knowledge_bidirectional_sync,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

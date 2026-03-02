"""
Week 5 测试 - LangGraph + Supervisor
"""
import sys
import asyncio
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.core.orchestration.supervisor import (
    SupervisorAgent, Task, TaskType, ProjectRole,
    NeuralSiteAdapter, EvoSwarmAdapter, VisualCoTAdapter
)
from src.core.orchestration.langgraph_workflow import (
    LangGraphWorkflow
)


def test_supervisor_task_classification():
    """测试任务分类"""
    print("\n[1] Testing task classification...")
    
    supervisor = SupervisorAgent()
    
    # 测试各种任务类型
    test_cases = [
        ("design login", TaskType.DESIGN),
        ("write code", TaskType.CODE),
        ("run test", TaskType.TEST),
        ("deploy", TaskType.DEPLOY),
        ("analyze", TaskType.ANALYZE),
        ("research", TaskType.RESEARCH),
    ]
    
    for desc, expected_type in test_cases:
        task = supervisor.analyze_task(desc)
        assert task.task_type == expected_type, f"Expected {expected_type}, got {task.task_type}"
        print(f"  OK: '{desc}' -> {task.task_type.value}")
    
    print("  PASS")


def test_supervisor_routing():
    """测试任务路由"""
    print("\n[2] Testing task routing...")
    
    supervisor = SupervisorAgent()
    
    # 测试路由
    task = supervisor.analyze_task("analyze NeuralSite status", {"projects": ["NeuralSite"]})
    
    assert len(task.required_roles) > 0
    assert ProjectRole.EXECUTOR in task.required_roles
    
    print(f"  Required roles: {[r.value for r in task.required_roles]}")
    print("  PASS")


def test_supervisor_execution():
    """测试任务执行"""
    print("\n[3] Testing supervisor execution...")
    
    supervisor = SupervisorAgent()
    
    # 同步执行测试
    result = asyncio.run(supervisor.execute("design a button"))
    
    assert "task_id" in result
    assert "results" in result
    assert result["success"] == True
    
    print(f"  Result: {result['results'][0]['result']}")
    print("  PASS")


def test_adapter_status():
    """测试适配器状态"""
    print("\n[4] Testing adapter status...")
    
    supervisor = SupervisorAgent()
    
    # 获取状态
    status = asyncio.run(supervisor.get_status())
    
    assert "NeuralSite" in status
    assert "Evo-Swarm" in status
    assert "VisualCoT" in status
    
    for name, info in status.items():
        print(f"  - {name}: {info['role']} ({info['healthy']})")
    
    print("  PASS")


def test_langgraph_workflow():
    """测试LangGraph工作流"""
    print("\n[5] Testing LangGraph workflow...")
    
    workflow = LangGraphWorkflow()
    
    # 创建状态
    state = workflow.create_state("test task", {"context": "test"})
    
    assert "task_description" in state
    assert state["current_step"] == "init"
    
    print(f"  State created: {state['task_description']}")
    print("  PASS")


def test_langgraph_step_execution():
    """测试步骤执行"""
    print("\n[6] Testing step execution...")
    
    workflow = LangGraphWorkflow()
    workflow.create_state("test task")
    
    # 执行步骤
    state = workflow.execute_step("analyze", {"finding": "test result"})
    
    assert state["current_step"] == "analyze"
    assert state["finding"] == "test result"
    
    print("  PASS")


def test_checkpoint_save():
    """测试检查点保存"""
    print("\n[7] Testing checkpoint save...")
    
    workflow = LangGraphWorkflow()
    workflow.create_state("test task")
    workflow.execute_step("step1", {"result": "data"})
    
    # 检查点已自动保存
    assert len(workflow.checkpoints) > 0
    print(f"  Checkpoints saved: {len(workflow.checkpoints)}")
    print("  PASS")


def test_checkpoint_restore():
    """测试检查点恢复"""
    print("\n[8] Testing checkpoint restore...")
    
    workflow = LangGraphWorkflow()
    workflow.create_state("test task")
    workflow.execute_step("step1", {"result": "data1"})
    workflow.execute_step("step2", {"result": "data2"})
    
    # 保存当前索引
    original_step = workflow.current_state["current_step"]
    
    # 恢复到上一个检查点
    restored = workflow.restore_checkpoint(-2)
    
    assert restored is not None
    print(f"  Current step: {workflow.current_state['current_step']}")
    print("  PASS")


def test_supervisor_multiproject():
    """测试多项目协作"""
    print("\n[9] Testing multi-project coordination...")
    
    supervisor = SupervisorAgent()
    
    # 协调多项目
    result = asyncio.run(supervisor.execute(
        "integrate NeuralSite and VisualCoT",
        {"projects": ["NeuralSite", "VisualCoT"]}
    ))
    
    assert len(result["results"]) >= 2
    print(f"  Coordinated {len(result['results'])} projects")
    print("  PASS")


def test_langgraph_error_handling():
    """测试错误处理"""
    print("\n[10] Testing error handling...")
    
    workflow = LangGraphWorkflow()
    workflow.create_state("test task")
    
    # 添加错误
    workflow.add_error("Test error")
    
    assert len(workflow.current_state["errors"]) > 0
    assert workflow.current_state["retry_count"] == 1
    
    print("  PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Week 5 Test Suite - LangGraph + Supervisor")
    print("=" * 60)
    
    tests = [
        test_supervisor_task_classification,
        test_supervisor_routing,
        test_supervisor_execution,
        test_adapter_status,
        test_langgraph_workflow,
        test_langgraph_step_execution,
        test_checkpoint_save,
        test_checkpoint_restore,
        test_supervisor_multiproject,
        test_langgraph_error_handling,
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

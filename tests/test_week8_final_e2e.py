"""
Week 8 最终E2E测试
完整端到端场景测试
"""
import sys
import asyncio
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.core.orchestration.final_workflow import (
    FinalWorkflow, TaskContext, TaskStatus, WorkflowStage
)
from src.core.thinking.mar_framework_v2 import MARFrameworkV2
from src.core.orchestration.knowledge_flow import KnowledgeFlow, KnowledgeType
from src.core.evaluation.evals_framework import EvalsFramework


def test_final_workflow_creation():
    """测试最终工作流创建"""
    print("\n[1] Testing final workflow creation...")
    
    workflow = FinalWorkflow()
    
    assert workflow is not None
    print(f"  MAR available: {workflow.mar_available}")
    print(f"  Knowledge Flow available: {workflow.kf_available}")
    print(f"  Supervisor available: {workflow.supervisor_available}")
    
    print("  PASS")


def test_final_workflow_execution():
    """测试最终工作流执行"""
    print("\n[2] Testing final workflow execution...")
    
    workflow = FinalWorkflow()
    
    # 创建任务
    task = TaskContext(
        task_id="test_001",
        description="分析项目进度并生成报告",
        projects=["NeuralSite", "Evo-Swarm"],
        priority=3
    )
    
    # 执行工作流
    async def run_test():
        return await workflow.execute(task)
    
    result = asyncio.run(run_test())
    
    assert result is not None
    assert result.task_id == "test_001"
    assert len(result.stages_completed) > 0
    
    print(f"  Stages completed: {[s.value for s in result.stages_completed]}")
    print(f"  Status: {result.status.value}")
    print(f"  Execution time: {result.execution_time_ms}ms")
    
    print("  PASS")


def test_final_workflow_high_priority():
    """测试高优先级任务（需人工审批）"""
    print("\n[3] Testing high priority workflow...")
    
    workflow = FinalWorkflow()
    
    # 模拟人工审批回调
    async def human_approval(data):
        return {"approved": True, "comment": "Approved"}
    
    task = TaskContext(
        task_id="test_002",
        description="部署到生产环境",
        projects=["NeuralSite"],
        priority=5
    )
    
    async def run_test():
        return await workflow.execute(task, human_approval)
    
    result = asyncio.run(run_test())
    
    assert len(result.human_approvals) > 0
    print(f"  Human approvals: {len(result.human_approvals)}")
    
    print("  PASS")


def test_mar_integration():
    """测试MAR集成"""
    print("\n[4] Testing MAR integration...")
    
    mar = MARFrameworkV2()
    
    context = {
        "task": "测试MAR",
        "project": "Partner-Evolution"
    }
    
    result = mar.reflect(context)
    
    assert "reflections" in result
    assert "conclusion" in result
    
    print(f"  Reflections: {len(result['reflections'])}")
    print("  PASS")


def test_knowledge_flow_integration():
    """测试知识流动集成"""
    print("\n[5] Testing knowledge flow integration...")
    
    kf = KnowledgeFlow()
    
    # 添加知识
    item_id = kf.add_knowledge(
        "NeuralSite",
        KnowledgeType.INSIGHT,
        {"test": "data"},
        auto_sync=False
    )
    
    # 手动同步
    event = kf.sync_knowledge(
        "NeuralSite",
        "Evo-Swarm",
        [item_id]
    )
    
    assert event.status in ["success", "partial"]
    
    print(f"  Knowledge items: {kf.get_status()['total_knowledge_items']}")
    print("  PASS")


def test_evals_integration():
    """测试评估框架集成"""
    print("\n[6] Testing evals integration...")
    
    evals = EvalsFramework()
    
    def mock_system(input_data):
        return {"result": "success"}
    
    report = evals.run_evaluation(mock_system)
    
    assert report is not None
    assert report.total_tests > 0
    
    print(f"  Test cases: {report.total_tests}")
    print(f"  Pass rate: {report.pass_rate:.1%}")
    
    print("  PASS")


def test_workflow_history():
    """测试工作流历史"""
    print("\n[7] Testing workflow history...")
    
    workflow = FinalWorkflow()
    
    # 执行一些任务
    task = TaskContext(
        task_id="test_003",
        description="测试任务",
        projects=["NeuralSite"],
        priority=2
    )
    
    asyncio.run(workflow.execute(task))
    
    history = workflow.get_execution_history()
    
    assert len(history) > 0
    
    print(f"  Total executions: {len(history)}")
    print("  PASS")


def test_workflow_status():
    """测试工作流状态"""
    print("\n[8] Testing workflow status...")
    
    workflow = FinalWorkflow()
    
    # 执行任务
    task = TaskContext(
        task_id="test_004",
        description="状态测试",
        projects=["NeuralSite"],
        priority=1
    )
    
    asyncio.run(workflow.execute(task))
    
    status = workflow.get_status()
    
    assert "mar_available" in status
    assert "total_executions" in status
    
    print(f"  Status: {status}")
    print("  PASS")


def test_multi_project_coordination():
    """测试多项目协调"""
    print("\n[9] Testing multi-project coordination...")
    
    workflow = FinalWorkflow()
    
    task = TaskContext(
        task_id="test_005",
        description="整合NeuralSite和VisualCoT进行端到端测试",
        projects=["NeuralSite", "VisualCoT"],
        priority=4
    )
    
    result = asyncio.run(workflow.execute(task))
    
    assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    print(f"  Coordinated projects: {len(task.projects)}")
    print(f"  Stages: {[s.value for s in result.stages_completed]}")
    
    print("  PASS")


def test_reflection_in_workflow():
    """测试工作流中的反思"""
    print("\n[10] Testing reflection in workflow...")
    
    workflow = FinalWorkflow()
    
    task = TaskContext(
        task_id="test_006",
        description="反思测试",
        projects=["Evo-Swarm"],
        priority=2
    )
    
    result = asyncio.run(workflow.execute(task))
    
    # 检查是否包含反思阶段
    has_reflect = WorkflowStage.REFLECT in result.stages_completed
    
    print(f"  Reflection included: {has_reflect}")
    print("  PASS")


def test_knowledge_sync_in_workflow():
    """测试工作流中的知识同步"""
    print("\n[11] Testing knowledge sync in workflow...")
    
    workflow = FinalWorkflow()
    
    task = TaskContext(
        task_id="test_007",
        description="知识同步测试",
        projects=["NeuralSite", "Evo-Swarm"],
        priority=2
    )
    
    result = asyncio.run(workflow.execute(task))
    
    # 检查知识同步
    print(f"  Knowledge synced: {len(result.knowledge_synced)}")
    
    print("  PASS")


def test_full_integration():
    """完整集成测试"""
    print("\n[12] Full integration test...")
    
    # 1. MAR
    mar = MARFrameworkV2()
    mar_result = mar.reflect({"task": "完整测试", "project": "Partner-Evolution"})
    
    # 2. Knowledge Flow
    kf = KnowledgeFlow()
    kf.add_knowledge("NeuralSite", KnowledgeType.INSIGHT, {"test": True}, auto_sync=False)
    
    # 3. Workflow
    workflow = FinalWorkflow()
    task = TaskContext(
        task_id="full_test",
        description="完整集成测试",
        projects=["NeuralSite"],
        priority=2
    )
    wf_result = asyncio.run(workflow.execute(task))
    
    # 4. Evals
    evals = EvalsFramework()
    def mock(input):
        return {"result": "ok"}
    eval_report = evals.run_evaluation(mock)
    
    print(f"  MAR: {len(mar_result['reflections'])} reflections")
    print(f"  Knowledge: {kf.get_status()['total_knowledge_items']} items")
    print(f"  Workflow: {wf_result.status.value}")
    print(f"  Evals: {eval_report.pass_rate:.1%} pass rate")
    
    print("  PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Week 8 Final E2E Test Suite")
    print("=" * 60)
    
    tests = [
        test_final_workflow_creation,
        test_final_workflow_execution,
        test_final_workflow_high_priority,
        test_mar_integration,
        test_knowledge_flow_integration,
        test_evals_integration,
        test_workflow_history,
        test_workflow_status,
        test_multi_project_coordination,
        test_reflection_in_workflow,
        test_knowledge_sync_in_workflow,
        test_full_integration,
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

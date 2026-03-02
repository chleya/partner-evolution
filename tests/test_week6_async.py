"""
Week 6 测试 - Async Workflow + Enhanced Observability
"""
import sys
import asyncio
import time
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.core.orchestration.async_workflow import AsyncWorkflow, RedisCache
from src.core.services.enhanced_observability import EnhancedObservabilityService, get_observability_service


def test_async_workflow_creation():
    """测试异步工作流创建"""
    print("\n[1] Testing async workflow creation...")
    
    workflow = AsyncWorkflow("test_workflow")
    
    assert workflow.name == "test_workflow"
    assert len(workflow.nodes) == 0
    
    print("  PASS")


def test_async_node_add():
    """测试异步节点添加"""
    print("\n[2] Testing async node add...")
    
    workflow = AsyncWorkflow("test")
    
    async def handler(state):
        return {"result": "done"}
    
    workflow.add_node(
        "step1",
        handler,
        timeout=10,
        retry=2,
        checkpoint=True,
        human_in_loop=False
    )
    
    assert "step1" in workflow.nodes
    node = workflow.nodes["step1"]
    assert node.timeout == 10
    assert node.retry == 2
    assert node.checkpoint == True
    
    print("  PASS")


def test_async_node_execution():
    """测试异步节点执行"""
    print("\n[3] Testing async node execution...")
    
    workflow = AsyncWorkflow("test")
    
    async def handler(state):
        await asyncio.sleep(0.01)  # 模拟异步操作
        return {"result": "hello"}
    
    workflow.add_node("step1", handler)
    workflow.set_entry_point("step1")
    
    result = asyncio.run(workflow.run({"task": "test"}))
    
    assert result["status"] == "completed"
    assert result["result"]["result"] == "hello"
    
    print("  PASS")


def test_checkpoint_save():
    """测试检查点保存"""
    print("\n[4] Testing checkpoint save...")
    
    workflow = AsyncWorkflow("test")
    
    async def handler(state):
        return {"data": "value"}
    
    workflow.add_node("step1", handler, checkpoint=True)
    workflow.set_entry_point("step1")
    
    asyncio.run(workflow.run({"task": "test"}))
    
    assert len(workflow.checkpoints) > 0
    checkpoint = workflow.save_checkpoint()
    assert checkpoint is not None
    
    print(f"  Checkpoints: {len(workflow.checkpoints)}")
    print("  PASS")


def test_checkpoint_restore():
    """测试检查点恢复"""
    print("\n[5] Testing checkpoint restore...")
    
    workflow = AsyncWorkflow("test")
    
    async def handler(state):
        return {"data": "value"}
    
    workflow.add_node("step1", handler)
    workflow.set_entry_point("step1")
    
    asyncio.run(workflow.run({"task": "test"}))
    
    # 保存检查点
    checkpoint = workflow.save_checkpoint()
    
    # 创建新工作流并恢复
    workflow2 = AsyncWorkflow("test2")
    workflow2.restore_checkpoint(checkpoint)
    
    assert workflow2.current_state is not None
    assert workflow2.current_state.get("task") == "test"
    
    print("  PASS")


def test_edge_addition():
    """测试边添加"""
    print("\n[6] Testing edge addition...")
    
    workflow = AsyncWorkflow("test")
    
    async def handler(state):
        return state
    
    workflow.add_node("step1", handler)
    workflow.add_node("step2", handler)
    workflow.add_edge("step1", "step2")
    workflow.set_entry_point("step1")
    
    assert len(workflow.edges) == 1
    assert ("step1", "step2") in workflow.edges
    
    print("  PASS")


def test_observability_service():
    """测试观测性服务"""
    print("\n[7] Testing observability service...")
    
    service = EnhancedObservabilityService()
    
    # 记录请求
    service.record_request("/api/test", 50.0, success=True)
    service.record_request("/api/test", 30.0, success=True)
    service.record_error("timeout", "/api/error")
    
    # 记录Token
    service.record_tokens(100, 50)
    
    # 记录思考
    service.record_think("deep", 0.85)
    
    # 获取指标
    metrics = service.get_metrics()
    
    assert metrics["summary"]["total_requests"] == 2  # success only
    assert metrics["summary"]["total_errors"] == 1
    
    print(f"  Requests: {metrics['summary']['total_requests']}")
    print(f"  Error rate: {metrics['summary']['error_rate_percent']}%")
    print("  PASS")


def test_prometheus_export():
    """测试Prometheus导出"""
    print("\n[8] Testing Prometheus export...")
    
    service = EnhancedObservabilityService()
    service.record_request("/api/test", 50.0)
    
    prom_output = service.get_prometheus_metrics()
    
    assert "partner_evolution_requests_total" in prom_output
    assert "partner_evolution_latency_seconds" in prom_output
    
    print(f"  Prometheus output:\n{prom_output[:200]}...")
    print("  PASS")


def test_trace_recording():
    """测试追踪记录"""
    print("\n[9] Testing trace recording...")
    
    service = EnhancedObservabilityService()
    
    # 开始追踪
    trace_id = service.start_trace("test_trace", "test_operation", {"key": "value"})
    
    # 添加跨度
    service.add_span(trace_id, "step1", 10.0)
    service.add_span(trace_id, "step2", 20.0)
    
    # 结束追踪
    service.end_trace(trace_id, "ok")
    
    traces = service.get_traces()
    
    assert len(traces) > 0
    trace = traces[0]
    assert trace["trace_id"] == trace_id
    assert len(trace["spans"]) == 2
    
    print(f"  Trace spans: {len(trace['spans'])}")
    print("  PASS")


def test_hallucination_detection():
    """测试幻觉检测记录"""
    print("\n[10] Testing hallucination detection...")
    
    service = EnhancedObservabilityService()
    
    service.record_hallucination_check(True)
    service.record_hallucination_check(False)
    service.record_hallucination_check(False)
    
    metrics = service.get_metrics()
    
    counters = metrics["metrics"]["counters"]
    hallucination_count = sum(v for k, v in counters.items() if "hallucination" in k and "result" in k and "hallucination" in k)
    
    print(f"  Hallucination checks recorded")
    print("  PASS")


def test_workflow_status():
    """测试工作流状态"""
    print("\n[11] Testing workflow status...")
    
    workflow = AsyncWorkflow("test_status")
    
    async def handler(state):
        return state
    
    workflow.add_node("step1", handler)
    workflow.set_entry_point("step1")
    
    asyncio.run(workflow.run({"task": "test"}))
    
    status = workflow.get_status()
    
    assert status["name"] == "test_status"
    assert "step1" in status["nodes"]
    assert status["checkpoints_count"] > 0
    
    print(f"  Status: {status['status']}")
    print("  PASS")


def test_observability_status():
    """测试观测性状态"""
    print("\n[12] Testing observability status...")
    
    service = EnhancedObservabilityService()
    service.record_request("/api/test", 50.0)
    
    status = service.get_status()
    
    assert "status" in status
    assert "uptime_seconds" in status
    assert status["status"] in ["healthy", "degraded"]
    
    print(f"  Status: {status['status']}")
    print("  PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Week 6 Test Suite - Async Workflow + Observability")
    print("=" * 60)
    
    tests = [
        test_async_workflow_creation,
        test_async_node_add,
        test_async_node_execution,
        test_checkpoint_save,
        test_checkpoint_restore,
        test_edge_addition,
        test_observability_service,
        test_prometheus_export,
        test_trace_recording,
        test_hallucination_detection,
        test_workflow_status,
        test_observability_status,
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

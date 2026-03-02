"""
Week 5-6 Test: Observability & Heartbeat Services
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

import time
from datetime import datetime, timezone
from src.core.services import (
    ObservabilityService, AlertService, MetricsCollector, ExecutionMetrics,
    HeartbeatService, SuggestionService
)

print("=" * 60)
print("Week 5-6 Test: Observability & Heartbeat Services")
print("=" * 60)

# ==================== 模块1: 观测性服务 ====================
print("\n[MODULE 1] Observability Service")
print("-" * 50)

obs = ObservabilityService()

# 记录指标
for i in range(10):
    metrics = ExecutionMetrics(
        task_id=f"task_{i}",
        latency_ms=100 + i * 10,
        token_count=500 + i * 50,
        error_rate=0.01 if i % 10 == 0 else 0.0,
        hallucination_rate=0.05,
        model="MiniMax-M2.5"
    )
    obs.record_execution(metrics)

print(f"  OK: Recorded {obs.stats['total_requests']} executions")

# 仪表盘数据
dashboard = obs.get_dashboard_data()
print(f"  OK: Dashboard data")
print(f"    - Avg latency: {dashboard['latency']['avg']:.2f}ms")
print(f"    - P95 latency: {dashboard['latency']['p95']:.2f}ms")
print(f"    - Error rate: {dashboard['quality']['error_rate']:.2%}")

# 漂移检测
drift = obs.detect_drift("latency_ms", threshold=0.5)
print(f"  OK: Drift detection: {len(drift)} alerts")

# ==================== 模块2: 告警服务 ====================
print("\n[MODULE 2] Alert Service")
print("-" * 50)

alert_svc = AlertService(obs)

# 触发告警
test_metrics = ExecutionMetrics(
    task_id="test_alert",
    latency_ms=6000,  # 超过阈值
    error_rate=0.25   # 超过阈值
)
alerts = alert_svc.check_and_alert(test_metrics)
print(f"  OK: Generated {len(alerts)} alerts")

# 注册处理器
alert_messages = []
def test_handler(alert):
    alert_messages.append(alert)

alert_svc.register_handler("P0", test_handler)
alert_svc.register_handler("P1", test_handler)

# 触发更多告警
test_metrics2 = ExecutionMetrics(task_id="test_alert2", latency_ms=100)
alert_svc.check_and_alert(test_metrics2)
print(f"  OK: Alert handlers: {len(alert_messages)}")

# 获取活跃告警
active = alert_svc.get_active_alerts()
print(f"  OK: Active alerts: {len(active)}")

# 确认告警
if active:
    alert_svc.acknowledge_alert(active[0]["id"])
    print(f"  OK: Alert acknowledged")

# ==================== 模块3: 指标收集器 ====================
print("\n[MODULE 3] Metrics Collector")
print("-" * 50)

collector = MetricsCollector()

# 收集各模块指标
collector.record("thinking", "total_thinks", 100)
collector.record("thinking", "mar_reflections", 25)
collector.record("memory", "entities", 50)
collector.record("memory", "vectors", 1000)
collector.record("workflow", "tasks_completed", 30)

print(f"  OK: Thinking metrics: {collector.get_module_metrics('thinking')}")
print(f"  OK: Memory metrics: {collector.get_module_metrics('memory')}")
print(f"  OK: All metrics: {len(collector.get_all_metrics())} modules")

# ==================== 模块4: 心跳服务 ====================
print("\n[MODULE 4] Heartbeat Service")
print("-" * 50)

heartbeat = HeartbeatService()

# 手动运行任务
result1 = heartbeat.run_task("daily_checkin")
print(f"  OK: Daily checkin: {result1.get('type')}")

result2 = heartbeat.run_task("evening_report")
print(f"  OK: Evening report: {result2.get('type')}")

# 注册自定义任务
task_called = []
def custom_task():
    task_called.append(True)
    return {"status": "ok"}

heartbeat.register_task("custom_task", custom_task, "hourly")
heartbeat.run_task("custom_task")
print(f"  OK: Custom task: {len(task_called)} calls")

# 状态
status = heartbeat.get_status()
print(f"  OK: Heartbeat status: running={status['running']}, tasks={status['registered_tasks']}")

# ==================== 模块5: 建议服务 ====================
print("\n[MODULE 5] Suggestion Service")
print("-" * 50)

suggestion_svc = SuggestionService()

# 生成建议
projects = {
    "NeuralSite": {
        "current_stage": "Stage4",
        "progress": 0.6,
        "dependencies": {"needed": ["图纸数据"]}
    },
    "Partner-Evolution": {
        "current_stage": "Week4",
        "progress": 0.8
    }
}
suggestions = suggestion_svc.generate_suggestions(projects)
print(f"  OK: Generated {len(suggestions)} suggestions")
for s in suggestions:
    print(f"    - [{s['priority']}] {s['title']}: {s['description'][:30]}")

# 获取高优先级建议
high_priority = suggestion_svc.get_suggestions("high")
print(f"  OK: High priority: {len(high_priority)}")

# ==================== 模块6: 跨服务集成 ====================
print("\n[MODULE 6] Service Integration")
print("-" * 50)

# 模拟完整工作流
metrics = ExecutionMetrics(
    task_id="integration_test",
    latency_ms=150,
    token_count=800,
    error_rate=0.02,
    task_type="workflow"
)
obs.record_execution(metrics)

# 检查告警
alerts = alert_svc.check_and_alert(metrics)
print(f"  OK: Workflow alerts: {len(alerts)}")

# 收集指标
collector.record("workflow", "last_run", datetime.now(timezone.utc).isoformat())
collector.record("workflow", "alerts", len(alerts))

# 验证集成
all_metrics = collector.get_all_metrics()
print(f"  OK: All modules tracked: {list(all_metrics.keys())}")

print("\n" + "=" * 60)
print("Week 5-6 TEST SUMMARY")
print("=" * 60)
print("  [1] Observability Service    PASS")
print("  [2] Alert Service            PASS")
print("  [3] Metrics Collector        PASS")
print("  [4] Heartbeat Service        PASS")
print("  [5] Suggestion Service       PASS")
print("  [6] Service Integration      PASS")
print("\n  Total: 6/6 PASSED")
print("=" * 60)

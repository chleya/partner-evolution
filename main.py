"""
主入口文件 - Partner-Evolution API
"""
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.memory import MemoryManager
from src.core.thinking import ThinkEngine, ThinkingMode
from src.core.orchestration import SupervisorAgent, LangGraphWorkflow
from src.core.services import ObservabilityService, AlertService, HeartbeatService
from src.core.optimization import LRUCache, PerformanceMonitor

app = Flask(__name__)
CORS(app)

# 初始化各模块
print("Initializing Partner-Evolution...")

# 缓存
cache = LRUCache(max_size=1000, ttl=300)
perf_monitor = PerformanceMonitor()

# 观测性服务
observability = ObservabilityService()
alert_service = AlertService(observability)

# 记忆系统
memory = MemoryManager(
    base_path=os.getenv("MEMORY_PATH", "data/memory"),
    config={"dimension": 384}
)

# 思考引擎
thinker = ThinkEngine(memory, config={"target_daily_thinks": 3})

# 编排系统
supervisor = SupervisorAgent()
workflow = LangGraphWorkflow(supervisor)

# 心跳服务
heartbeat = HeartbeatService()

print("Partner-Evolution initialized successfully!")


# ==================== API Routes ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "timestamp": None  # Will be added by framework
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    return jsonify({
        "memory": {
            "entities": len(memory.unified_memory["layers"]["semantic_memory"]["entities"]),
            "conversations": len(memory.unified_memory["layers"]["raw_memory"]["conversations"]),
        },
        "thinking": thinker.get_stats(),
        "projects": [p["name"] for p in supervisor.get_available_projects()],
        "observability": observability.get_metrics_summary()
    })


# ==================== Memory API ====================

@app.route('/api/memory/conversation', methods=['POST'])
def add_conversation():
    """添加对话"""
    data = request.json
    conv_id = memory.add_conversation(
        user=data.get("user", "user"),
        content=data.get("content", ""),
        intent=data.get("intent", "general"),
        outcome=data.get("outcome", "pending")
    )
    return jsonify({"id": conv_id, "status": "created"})


@app.route('/api/memory/entity', methods=['POST'])
def add_entity():
    """添加实体"""
    data = request.json
    entity_id = memory.add_entity(
        entity_type=data.get("type", "concept"),
        name=data.get("name", ""),
        aliases=data.get("aliases", []),
        attributes=data.get("attributes", {}),
        confidence=data.get("confidence", 0.5)
    )
    return jsonify({"id": entity_id, "status": "created"})


@app.route('/api/memory/search', methods=['GET'])
def search_memory():
    """搜索记忆"""
    keyword = request.args.get("q", "")
    results = memory.search_memory(keyword)
    return jsonify(results)


@app.route('/api/memory/retrieve', methods=['POST'])
def retrieve_memory():
    """向量检索记忆"""
    data = request.json
    query = data.get("query", "")
    result = memory.paginate_memory(query)
    return jsonify(result)


# ==================== Thinking API ====================

@app.route('/api/thinking/reflection', methods=['POST'])
def do_reflection():
    """执行反思"""
    data = request.json
    result = thinker.think(
        mode=ThinkingMode.MAR_REFLECTION,
        context=data.get("context", {})
    )
    return jsonify(result)


@app.route('/api/thinking/stats', methods=['GET'])
def thinking_stats():
    """思考统计"""
    return jsonify(thinker.get_stats())


# ==================== Workflow API ====================

@app.route('/api/workflow/execute', methods=['POST'])
def execute_workflow():
    """执行工作流"""
    data = request.json
    result = workflow.run(
        task_description=data.get("task", ""),
        context=data.get("context", {})
    )
    return jsonify(result)


@app.route('/api/workflow/status', methods=['GET'])
def workflow_status():
    """工作流状态"""
    state = workflow.get_state()
    return jsonify(state if state else {"status": "idle"})


# ==================== Metrics API ====================

@app.route('/api/metrics/dashboard', methods=['GET'])
def metrics_dashboard():
    """指标仪表盘"""
    return jsonify(observability.get_dashboard_data())


@app.route('/api/metrics/summary', methods=['GET'])
def metrics_summary():
    """指标摘要"""
    return jsonify(observability.get_metrics_summary())


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """获取告警"""
    level = request.args.get("level")
    return jsonify(alert_service.get_active_alerts(level))


# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"
    
    print(f"Starting Partner-Evolution API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)

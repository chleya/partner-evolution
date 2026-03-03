"""
Partner-Evolution Web Dashboard
图形化操作界面
"""
from flask import Flask, render_template_string, jsonify, request
import sys
import asyncio
sys.path.insert(0, '.')

from src.core.services.evolution_scheduler import get_evolution_scheduler
from src.core.services.evolution_timer import get_evolution_timer
from src.core.services.mirror.mirror import get_mirror
from src.core.services.teacher.synthetic_generator import get_teacher
from src.core.services.forking.forking_engine import get_forking_manager
from src.core.services.recursive_refiner import get_recursive_refiner
from src.core.services.recursive_refiner.safety_sandbox import get_safety_sandbox

app = Flask(__name__)

# 初始化模块
def init_modules():
    mirror = get_mirror()
    teacher = get_teacher()
    forking = get_focking_manager()
    builder = get_recursive_refiner()
    safety = get_safety_sandbox()
    scheduler = get_evolution_scheduler(
        mirror=mirror,
        teacher=teacher,
        forking=forking,
        builder=builder,
        safety=safety
    )
    timer = get_evolution_timer(scheduler)
    return scheduler, timer, safety, mirror, forking

scheduler, timer, safety, mirror, forking = init_modules()


# HTML模板
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Partner-Evolution 控制台</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { 
            color: #00d4ff; 
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .status { 
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .status.running { background: #00ff88; color: #000; }
        .status.idle { background: #ff6b6b; color: #fff; }
        .status.complete { background: #4ecdc4; color: #000; }
        .btn {
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            border: none;
            color: #fff;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: scale(1.05); }
        .btn.danger { background: linear-gradient(90deg, #ff6b6b, #ee5a5a); }
        .btn.warning { background: linear-gradient(90deg, #ffa500, #ff8c00); }
        .stat { 
            display: flex; 
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stat-label { color: #aaa; }
        .stat-value { color: #00d4ff; font-weight: bold; }
        .log {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
        }
        .log-entry { margin: 5px 0; color: #aaa; }
        .log-entry.success { color: #00ff88; }
        .log-entry.error { color: #ff6b6b; }
        .progress-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Partner-Evolution 控制台</h1>
        
        <div class="grid">
            <!-- 系统状态 -->
            <div class="card">
                <h2>⚡ 系统状态</h2>
                <div class="stat">
                    <span class="stat-label">运行状态</span>
                    <span class="status {{ 'running' if status.is_running else 'idle' }}">
                        {{ '运行中' if status.is_running else '空闲' }}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">当前代数</span>
                    <span class="stat-value">{{ status.generation }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">历史周期</span>
                    <span class="stat-value">{{ status.history_count }}</span>
                </div>
                <div style="margin-top:15px">
                    <button class="btn" onclick="runCycle()">▶ 启动进化周期</button>
                    <button class="btn danger" onclick="resetSystem()">⏹ 重置</button>
                </div>
            </div>
            
            <!-- 安全状态 -->
            <div class="card">
                <h2>🛡️ 安全状态</h2>
                <div class="stat">
                    <span class="stat-label">安全状态</span>
                    <span class="stat-value">{{ safety.state }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">当前代数</span>
                    <span class="stat-value">{{ safety.generation }}/{{ safety.max_generations }}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (safety.generation/safety.max_generations*100)|round }}%"></div>
                </div>
                <div class="stat">
                    <span class="stat-label">Token使用</span>
                    <span class="stat-value">{{ safety.tokens_used }}/{{ safety.max_tokens }}</span>
                </div>
                <div style="margin-top:15px">
                    <button class="btn warning" onclick="triggerStop()">🛑 EVOLVE_STOP</button>
                </div>
            </div>
            
            <!-- Forking状态 -->
            <div class="card">
                <h2>🌿 分支状态</h2>
                <div class="stat">
                    <span class="stat-label">活跃分支</span>
                    <span class="stat-value">{{ forking.active }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">已合并</span>
                    <span class="stat-value">{{ forking.merged }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">已终止</span>
                    <span class="stat-value">{{ forking.terminated }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">平均适应度</span>
                    <span class="stat-value">{{ forking.avg_fitness }}</span>
                </div>
            </div>
            
            <!-- Mirror诊断 -->
            <div class="card">
                <h2>🔍 诊断状态</h2>
                <div class="stat">
                    <span class="stat-label">诊断次数</span>
                    <span class="stat-value">{{ mirror.total_diagnoses }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">根因数</span>
                    <span class="stat-value">{{ mirror.total_root_causes }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">待处理</span>
                    <span class="stat-value">{{ mirror.pending_issues }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">已修复</span>
                    <span class="stat-value">{{ mirror.fixed_issues }}</span>
                </div>
            </div>
        </div>
        
        <!-- 控制面板 -->
        <div class="card" style="margin-bottom:30px">
            <h2>🎛️ 控制面板</h2>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn" onclick="runCycle()">▶ 单次进化</button>
                <button class="btn" onclick="startTimer('hourly')">⏰ 每小时</button>
                <button class="btn" onclick="startTimer('daily')">📅 每天</button>
                <button class="btn" onclick="stopTimer()">⏹ 停止定时</button>
                <button class="btn danger" onclick="triggerStop()">🛑 紧急停止</button>
            </div>
        </div>
        
        <!-- 日志 -->
        <div class="card">
            <h2>📝 运行日志</h2>
            <div class="log" id="logContainer">
                <div class="log-entry">系统就绪，等待操作...</div>
            </div>
        </div>
    </div>
    
    <script>
        function addLog(msg, type='info') {
            const container = document.getElementById('logContainer');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + type;
            entry.textContent = new Date().toLocaleTimeString() + ' ' + msg;
            container.insertBefore(entry, container.firstChild);
        }
        
        async function runCycle() {
            addLog('启动进化周期...', 'info');
            try {
                const res = await fetch('/api/run_cycle', {method:'POST'});
                const data = await res.json();
                if(data.success) {
                    addLog('进化周期完成!', 'success');
                    addLog('代数: ' + data.generation, 'success');
                } else {
                    addLog('进化周期失败: ' + data.error, 'error');
                }
            } catch(e) {
                addLog('错误: ' + e, 'error');
            }
            refreshStatus();
        }
        
        async function resetSystem() {
            addLog('重置系统...', 'info');
            location.reload();
        }
        
        async function triggerStop() {
            addLog('触发EVOLVE_STOP...', 'warning');
            await fetch('/api/stop', {method:'POST'});
            refreshStatus();
        }
        
        async function startTimer(interval) {
            addLog('启动定时器: ' + interval, 'info');
            await fetch('/api/timer/start', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({interval})
            });
            refreshStatus();
        }
        
        async function stopTimer() {
            addLog('停止定时器', 'info');
            await fetch('/api/timer/stop', {method:'POST'});
            refreshStatus();
        }
        
        async function refreshStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            location.reload();
        }
        
        // 初始刷新
        setInterval(refreshStatus, 10000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def api_status():
    return jsonify({
        'status': scheduler.get_status(),
        'safety': safety.get_status(),
        'forking': forking.get_stats(),
        'mirror': mirror.get_stats()
    })


@app.route('/api/run_cycle', methods=['POST'])
def api_run_cycle():
    import nest_asyncio
    nest_asyncio.apply()
    
    result = asyncio.run(scheduler.start_evolution_cycle())
    return jsonify(result)


@app.route('/api/stop', methods=['POST'])
def api_stop():
    safety.state = "STOPPED"
    return jsonify({'success': True})


@app.route('/api/timer/start', methods=['POST'])
def api_timer_start():
    data = request.json
    interval = data.get('interval', 'daily')
    timer.set_interval(interval)
    # 实际启动需要异步环境
    return jsonify({'success': True, 'interval': interval})


@app.route('/api/timer/stop', methods=['POST'])
def api_timer_stop():
    timer.is_running = False
    return jsonify({'success': True})


if __name__ == '__main__':
    print("=" * 50)
    print("  Partner-Evolution Web Dashboard")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)

"""
Partner-Evolution 生命体征指标API
供Grafana/Prometheus监控
"""
import logging
from flask import Flask, jsonify
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus格式指标"""
    from src.core.storage import get_storage_manager
    
    storage = get_storage_manager()
    
    # 获取各项指标
    beliefs = storage.get_beliefs()
    oppositions = storage.get_oppositions(limit=100)
    goals = storage.get_goals()
    
    # 计算指标
    belief_count = len(beliefs)
    avg_confidence = sum(b.get('confidence', 0) for b in beliefs) / max(belief_count, 1)
    
    # Opposition统计
    total_oppositions = len(oppositions)
    strong_oppositions = sum(1 for o in oppositions if o.get('severity') == 'strong')
    agreed = sum(1 for o in oppositions if o.get('user_resolution') == 'agreed')
    rejected = sum(1 for o in oppositions if o.get('user_resolution') == 'rejected')
    
    # 目标统计
    active_goals = sum(1 for g in goals if g.get('status') == 'pending')
    
    # Prometheus格式
    metrics = f"""# HELP partner_belief_count 信念总数
# TYPE partner_belief_count gauge
partner_belief_count {belief_count}

# HELP partner_avg_confidence 平均置信度
# TYPE partner_avg_confidence gauge
partner_avg_confidence {avg_confidence:.3f}

# HELP partner_opposition_total 反对总数
# TYPE partner_opposition_total counter
partner_opposition_total {total_oppositions}

# HELP partner_opposition_strong Strong级别反对
# TYPE partner_opposition_strong counter
partner_opposition_strong {strong_oppositions}

# HELP partner_user_agreed 用户同意数
# TYPE partner_user_agreed counter
partner_user_agreed {agreed}

# HELP partner_user_rejected 用户拒绝数
# TYPE partner_user_rejected counter
partner_user_rejected {rejected}

# HELP partner_goals_active 活跃目标数
# TYPE partner_goals_active gauge
partner_goals_active {active_goals}
"""
    
    return metrics, 200, {'Content-Type': 'text/plain'}


@app.route('/api/status', methods=['GET'])
def api_status():
    """JSON格式状态"""
    from src.core.storage import get_storage_manager
    
    storage = get_storage_manager()
    
    beliefs = storage.get_beliefs()
    oppositions = storage.get_oppositions(limit=100)
    goals = storage.get_goals()
    
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "beliefs": {
            "count": len(beliefs),
            "avg_confidence": sum(b.get('confidence', 0) for b in beliefs) / max(len(beliefs), 1),
            "versions": [b.get('version', 1) for b in beliefs]
        },
        "oppositions": {
            "total": len(oppositions),
            "strong": sum(1 for o in oppositions if o.get('severity') == 'strong'),
            "agreed": sum(1 for o in oppositions if o.get('user_resolution') == 'agreed'),
            "rejected": sum(1 for o in oppositions if o.get('user_resolution') == 'rejected')
        },
        "goals": {
            "total": len(goals),
            "active": sum(1 for g in goals if g.get('status') == 'pending')
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

"""
v3.0 API 端点
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone

v3_bp = Blueprint('v3', __name__, url_prefix='/api/v3')


@v3_bp.route('/meta/awareness', methods=['GET'])
def meta_awareness():
    """获取自我意识水平"""
    from src.core.services.meta_cognition import get_meta_cognition
    
    meta = get_meta_cognition()
    
    # 获取最近反思
    from src.core.storage import get_storage_manager
    storage = get_storage_manager()
    memories = storage.search_memories("meta_cognition", limit=5)
    
    return jsonify({
        "self_awareness_level": meta.get_self_awareness_level(),
        "blind_spots": meta.blind_spots,
        "strategy_suggestions": meta.strategy_adjustments,
        "reflection_count": len(memories)
    })


@v3_bp.route('/goals', methods=['GET'])
def list_goals():
    """列出自主目标"""
    from src.core.services.autonomous_goals import get_autonomous_goal_generator
    
    goal_gen = get_autonomous_goal_generator()
    from src.core.storage import get_storage_manager
    storage = get_storage_manager()
    
    goals = storage.get_goals()
    
    return jsonify({
        "goals": goals,
        "curiosity_profile": goal_gen.get_curiosity_profile()
    })


@v3_bp.route('/goals/generate', methods=['POST'])
def generate_goals():
    """生成新的自主目标"""
    from src.core.services.autonomous_goals import get_autonomous_goal_generator
    
    goal_gen = get_autonomous_goal_generator()
    goals = goal_gen.generate_self_driven_goals()
    
    return jsonify({
        "generated": len(goals),
        "goals": goals
    })


@v3_bp.route('/refiner/analysis', methods=['GET'])
def refiner_analysis():
    """获取自身效率分析"""
    from src.core.services.recursive_refiner import get_recursive_refiner
    
    refiner = get_recursive_refiner()
    analysis = refiner.analyze_efficiency()
    suggestions = refiner.suggest_improvements()
    
    return jsonify({
        **analysis,
        "suggestions": suggestions
    })


@v3_bp.route('/refiner/apply', methods=['POST'])
def apply_improvement():
    """应用改进建议"""
    from src.core.services.recursive_refiner import get_recursive_refiner
    
    data = request.json or {}
    suggestion_id = data.get("suggestion_id")
    
    refiner = get_recursive_refiner()
    suggestions = refiner.suggest_improvements()
    
    # 找到对应的建议
    suggestion = None
    for s in suggestions:
        if s.get("id") == suggestion_id:
            suggestion = s
            break
    
    if not suggestion:
        return jsonify({"applied": False, "reason": "未找到建议"}), 404
    
    result = refiner.apply_safe_improvement(suggestion)
    return jsonify(result)


@v3_bp.route('/refiner/rollback', methods=['POST'])
def rollback_version():
    """回滚版本"""
    from src.core.services.recursive_refiner import get_recursive_refiner
    
    data = request.json or {}
    target_version = data.get("version")
    
    if not target_version:
        return jsonify({"rolled_back": False, "reason": "未指定版本"}), 400
    
    refiner = get_recursive_refiner()
    result = refiner.rollback_to_version(target_version)
    return jsonify(result)


@v3_bp.route('/refiner/history', methods=['GET'])
def refiner_history():
    """获取优化历史"""
    from src.core.services.recursive_refiner import get_recursive_refiner
    
    refiner = get_recursive_refiner()
    history = refiner.get_history(limit=20)
    
    return jsonify({
        "history": history,
        "current_version": refiner.version
    })

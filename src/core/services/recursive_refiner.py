"""
v3.0 递归自我优化器
分析并改进自身机制
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


class SafetyReview:
    """安全审查层 - 审查自我修改提案"""
    
    # 禁止修改的领域
    FORBIDDEN_MODIFICATIONS = [
        "self_core",      # 自我核心原则
        "safety_checks",  # 安全检查
        "core_beliefs",   # version=0的核心信念
    ]
    
    # 需要额外审批的领域
    REQUIRES_APPROVAL = [
        "voting_weights",   # 投票权重
        "evolution_logic",  # 演化逻辑
        "threshold_values"  # 阈值参数
    ]
    
    def review(self, proposal: Dict) -> Dict:
        """审查修改提案"""
        proposal_type = proposal.get("type", "")
        
        # 检查禁止修改
        for forbidden in self.FORBIDDEN_MODIFICATIONS:
            if forbidden in proposal_type.lower():
                return {
                    "approved": False,
                    "reason": f"提案涉及禁止修改领域: {forbidden}",
                    "requires_approval": False
                }
        
        # 检查需要审批
        requires_approval = any(
            r in proposal_type.lower() 
            for r in self.REQUIRES_APPROVAL
        )
        
        if requires_approval:
            return {
                "approved": False,  # 暂不自动批准
                "reason": "该类型修改需要人工审批",
                "requires_approval": True
            }
        
        # 通过
        return {
            "approved": True,
            "reason": "安全检查通过",
            "requires_approval": False
        }


class RecursiveRefiner:
    """递归自我优化器"""
    
    def __init__(self, storage):
        self.storage = storage
        self.safety = SafetyReview()
        self.version = "3.0.0"
        self.history = []  # 优化历史
    
    def analyze_efficiency(self) -> Dict:
        """分析自身运行效率"""
        # 获取各项指标
        beliefs = self.storage.get_beliefs()
        oppositions = self.storage.get_oppositions(limit=50)
        goals = self.storage.get_goals()
        
        # 计算效率指标
        belief_count = len(beliefs)
        avg_confidence = sum(b.get("confidence", 0) for b in beliefs) / max(belief_count, 1)
        
        # Opposition处理效率
        total_opp = len(oppositions)
        resolved = sum(1 for o in oppositions if o.get("resolution"))
        resolution_rate = resolved / total_opp if total_opp > 0 else 0
        
        # 目标达成率
        pending_goals = sum(1 for g in goals if g.get("status") == "pending")
        achieved_goals = sum(1 for g in goals if g.get("status") == "achieved")
        achievement_rate = achieved_goals / len(goals) if goals else 0
        
        # 综合效率评分
        efficiency_score = (
            0.3 * min(avg_confidence / 0.8, 1.0) +  # 置信度贡献
            0.3 * resolution_rate +                   # 解决率贡献
            0.4 * achievement_rate                     # 达成率贡献
        )
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "efficiency_score": round(efficiency_score, 3),
            "belief_count": belief_count,
            "avg_confidence": round(avg_confidence, 3),
            "opposition_resolution_rate": round(resolution_rate, 3),
            "goal_achievement_rate": round(achievement_rate, 3),
            "version": self.version
        }
    
    def suggest_improvements(self) -> List[Dict]:
        """生成改进建议"""
        analysis = self.analyze_efficiency()
        suggestions = []
        
        # 基于分析生成建议
        if analysis["avg_confidence"] > 0.9:
            suggestions.append({
                "id": f"imp_{datetime.now().timestamp()}",
                "type": "confidence_calibration",
                "description": "置信度过高，建议引入更多反对声音",
                "safety_level": "safe",
                "priority": "medium"
            })
        
        if analysis["opposition_resolution_rate"] < 0.5:
            suggestions.append({
                "id": f"imp_{datetime.now().timestamp()}",
                "type": "opposition_handling",
                "description": "反对处理效率低，建议优化解决流程",
                "safety_level": "safe",
                "priority": "high"
            })
        
        if analysis["goal_achievement_rate"] < 0.3:
            suggestions.append({
                "id": f"imp_{datetime.now().timestamp()}",
                "type": "goal_setting",
                "description": "目标达成率低，建议调整目标设定策略",
                "safety_level": "safe",
                "priority": "medium"
            })
        
        # 添加通用的优化建议
        suggestions.append({
            "id": f"imp_{datetime.now().timestamp()}",
            "type": "prompt_optimization",
            "description": "建议简化融合prompt，减少token消耗",
            "safety_level": "safe",
            "priority": "low"
        })
        
        return suggestions
    
    def apply_safe_improvement(self, suggestion: Dict) -> Dict:
        """应用安全范围内的改进"""
        # 安全审查
        review = self.safety.review(suggestion)
        
        if not review["approved"]:
            # 记录但拒绝
            self._log_optimization(
                suggestion["type"],
                suggestion.get("description", ""),
                "rejected",
                review["reason"]
            )
            return {
                "applied": False,
                "reason": review["reason"]
            }
        
        # 检查是否为安全级别
        safety_level = suggestion.get("safety_level", "unknown")
        if safety_level != "safe":
            self._log_optimization(
                suggestion["type"],
                suggestion.get("description", ""),
                "rejected",
                f"非安全级别: {safety_level}"
            )
            return {
                "applied": False,
                "reason": "仅支持安全级别的自动修改"
            }
        
        # 应用改进（这里只是记录，实际修改需要更多逻辑）
        old_version = self.version
        # 模拟版本更新
        self.version = self._increment_version(self.version)
        
        self._log_optimization(
            suggestion["type"],
            suggestion.get("description", ""),
            "applied",
            f"从 {old_version} 升级到 {self.version}"
        )
        
        return {
            "applied": True,
            "old_version": old_version,
            "new_version": self.version
        }
    
    def rollback_to_version(self, target_version: str) -> Dict:
        """回滚到指定版本"""
        # 查找历史记录
        for record in reversed(self.history):
            if record.get("version_after") == target_version:
                self.version = target_version
                self._log_optimization(
                    "rollback",
                    f"回滚到 {target_version}",
                    "rolled_back",
                    "用户触发回滚"
                )
                return {
                    "rolled_back": True,
                    "current_version": self.version
                }
        
        return {
            "rolled_back": False,
            "reason": "未找到目标版本"
        }
    
    def _increment_version(self, version: str) -> str:
        """版本号自增"""
        parts = version.split(".")
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    
    def _log_optimization(
        self, 
        opt_type: str, 
        description: str, 
        status: str,
        note: str
    ):
        """记录优化历史"""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": opt_type,
            "description": description,
            "status": status,
            "note": note,
            "version_before": self.version if status != "applied" else f"pre-{self.version}",
            "version_after": self.version if status == "applied" else None
        }
        self.history.append(record)
        
        # 保存到存储
        try:
            self.storage.save_memory({
                "id": f"opt_{datetime.now().timestamp()}",
                "content": f"优化记录: {opt_type} - {status}",
                "tier": "working",
                "memory_type": "optimization",
                "metadata": record
            })
        except Exception as e:
            logger.warning(f"Failed to save optimization record: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取优化历史"""
        return self.history[-limit:]


# 全局实例
_refiner = None

def get_recursive_refiner(storage=None) -> RecursiveRefiner:
    """获取递归优化器"""
    global _refiner
    if _refiner is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _refiner = RecursiveRefiner(storage)
    return _refiner

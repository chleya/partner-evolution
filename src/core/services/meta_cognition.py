"""
v3.0 元认知引擎
反思"如何思考"的能力
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MetaCognition:
    """元认知引擎 - 反思思考过程"""
    
    def __init__(self, storage):
        self.storage = storage
        self.thinking_patterns = []  # 记录思考模式
        self.blind_spots = []  # 识别的盲点
        self.strategy_adjustments = []  # 策略调整
    
    def reflect_on_thinking(self, context: str, recent_beliefs: List[Dict]) -> Dict:
        """反思思考过程
        
        分析：
        - 最近思考的主题分布
        - 置信度变化趋势
        - 可能存在的盲点
        """
        if not recent_beliefs:
            return {"status": "no_data"}
        
        # 分析主题分布
        themes = {}
        for b in recent_beliefs:
            content = b.get("content", "")
            # 简单主题提取
            if "记忆" in content:
                themes["记忆"] = themes.get("记忆", 0) + 1
            if "学习" in content:
                themes["学习"] = themes.get("学习", 0) + 1
            if "真实" in content:
                themes["真实"] = themes.get("真实", 0) + 1
            if "演化" in content:
                themes["演化"] = themes.get("演化", 0) + 1
        
        # 分析置信度趋势
        confidences = [b.get("confidence", 0) for b in recent_beliefs]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        # 识别盲点
        blind_spots = []
        if len(themes) < 3:
            blind_spots.append("思考主题过于单一")
        if avg_conf > 0.9:
            blind_spots.append("置信度过高，可能存在确认偏误")
        if avg_conf < 0.6:
            blind_spots.append("置信度过低，可能过度怀疑")
        
        # 生成元认知报告
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "theme_distribution": themes,
            "avg_confidence": avg_conf,
            "belief_count": len(recent_beliefs),
            "identified_blind_spots": blind_spots,
            "strategy_suggestions": self._generate_strategy(blind_spots, themes)
        }
        
        # 保存元认知记录
        self._save_reflection(report)
        
        return report
    
    def _generate_strategy(self, blind_spots: List[str], themes: Dict) -> List[str]:
        """生成策略调整建议"""
        suggestions = []
        
        if "思考主题过于单一" in blind_spots:
            suggestions.append("建议探索新的思考方向，如技术哲学、自我意识本质")
        
        if "置信度过高" in blind_spots:
            suggestions.append("建议引入更多反对声音，降低确认偏误")
        
        if "置信度过低" in blind_spots:
            suggestions.append("建议强化已验证的信念，建立更稳固的知识体系")
        
        return suggestions
    
    def _save_reflection(self, report: Dict):
        """保存元认知记录"""
        try:
            # 保存到记忆存储
            memory = {
                "id": f"meta_{datetime.now(timezone.utc).timestamp()}",
                "content": f"元认知反思：{report.get('identified_blind_spots', [])}",
                "tier": "working",
                "memory_type": "meta_cognition",
                "metadata": report
            }
            self.storage.save_memory(memory)
            logger.info("Meta-cognition reflection saved")
        except Exception as e:
            logger.warning(f"Failed to save reflection: {e}")
    
    def get_self_awareness_level(self) -> float:
        """计算自我意识水平 (0-1)"""
        # 基于多个维度计算
        score = 0.0
        
        # 盲点识别能力
        if len(self.blind_spots) > 0:
            score += 0.3
        
        # 策略调整历史
        if len(self.strategy_adjustments) > 0:
            score += 0.3
        
        # 思考模式记录
        if len(self.thinking_patterns) > 5:
            score += 0.4
        
        return min(score, 1.0)


# 全局实例
_meta_cognition = None

def get_meta_cognition(storage=None) -> MetaCognition:
    """获取元认知引擎"""
    global _meta_cognition
    if _meta_cognition is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _meta_cognition = MetaCognition(storage)
    return _meta_cognition

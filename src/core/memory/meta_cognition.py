"""
元认知层 - 负责对记忆的自我反思和管理
"""

from datetime import datetime, timezone
from typing import Any, Dict


class MetaCognition:
    """元认知层 - 自我认知和反思"""

    # 能力分级定义
    LEVEL_DESCRIPTIONS = {
        0: "未知/未测试",
        1: "初步了解",
        2: "可以基础使用",
        3: "熟练使用",
        4: "精通",
        5: "专家级别"
    }

    def evaluate_capability(
        self,
        capability: str,
        level: int,
        confidence: float,
        meta_memory: Dict[str, Any]
    ):
        """
        评估能力并更新元认知
        当置信度发生显著变化时触发反思
        """
        capabilities = meta_memory.get("capabilities", {})
        current = capabilities.get(capability, {})
        
        old_confidence = current.get("confidence", 0)

        # 置信度变化超过0.2时触发反思
        if abs(confidence - old_confidence) > 0.2:
            self._trigger_reflection(
                capability,
                old_confidence,
                confidence,
                meta_memory
            )

    def _trigger_reflection(
        self,
        capability: str,
        old_conf: float,
        new_conf: float,
        meta_memory: Dict[str, Any]
    ):
        """
        触发能力认知变化的反思
        更新边界声明
        """
        # 记录反思日志
        reflection = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "capability": capability,
            "old_confidence": old_conf,
            "new_confidence": new_conf,
            "type": "confidence_change"
        }

        if "reflections" not in meta_memory:
            meta_memory["reflections"] = []
        
        meta_memory["reflections"].append(reflection)

    def get_capability_description(self, capability: str, level: int) -> str:
        """获取能力等级的文字描述"""
        return self.LEVEL_DESCRIPTIONS.get(level, "未知")

    def should_confirm_action(self, action_risk: str, confidence: float) -> bool:
        """
        判断是否需要用户确认
        高风险操作或低置信度时需要确认
        """
        risk_levels = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.9
        }

        required_confidence = risk_levels.get(action_risk, 0.5)
        return confidence < required_confidence

    def estimate_uncertainty(
        self,
        task_complexity: str,
        available_context: int
    ) -> float:
        """
        估计任务的不确定性
        返回置信度（0-1）
        """
        # 基于任务复杂度和可用上下文估算
        complexity_scores = {
            "simple": 0.9,
            "medium": 0.7,
            "complex": 0.5,
            "very_complex": 0.3
        }
        
        base_confidence = complexity_scores.get(task_complexity, 0.5)
        
        # 上下文越多，置信度越高
        context_factor = min(1.0, available_context / 8000)
        
        return base_confidence * 0.7 + context_factor * 0.3

    def get_knowledge_boundaries(self, meta_memory: Dict[str, Any]) -> Dict[str, Any]:
        """获取当前知识边界"""
        capabilities = meta_memory.get("capabilities", {})
        
        strong_capabilities = []
        weak_capabilities = []
        
        for cap, data in capabilities.items():
            confidence = data.get("confidence", 0)
            if confidence >= 0.7:
                strong_capabilities.append(cap)
            elif confidence < 0.4:
                weak_capabilities.append(cap)
        
        return {
            "strong": strong_capabilities,
            "weak": weak_capabilities,
            "unknown": [
                cap for cap in capabilities.keys()
                if cap not in strong_capabilities and cap not in weak_capabilities
            ]
        }

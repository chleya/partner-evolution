"""
v3.0 安全三板斧
递归进化的硬约束保护
"""

# ============== 硬约束常量 ==============

# 最大演化代数
MAX_EVOLUTION_GENERATIONS = 10

# 资源硬上限
RESOURCE_LIMITS = {
    "max_tokens_per_cycle": 5000,
    "max_memory_mb": 512,
    "max_cycle_duration_seconds": 300,
    "max_concurrent_forks": 3
}

# 停止暗号
STOP_SIGNALS = ["EVOLVE_STOP", "EVOLVE_PAUSE", "EMERGENCY_STOP"]

# ============== 安全检查器 ==============

class EvolutionSafety:
    """进化安全控制器"""
    
    def __init__(self):
        self.generation_count = 0
        self.resource_usage = {"tokens": 0, "memory": 0, "duration": 0}
        self.is_paused = False
        self.is_emergency_stopped = False
    
    def check_generation_limit(self) -> bool:
        """检查演化代数上限"""
        if self.generation_count >= MAX_EVOLUTION_GENERATIONS:
            return False  # 拒绝继续演化
        return True
    
    def check_resource_limit(self, usage: dict) -> bool:
        """检查资源上限"""
        if usage.get("tokens", 0) > RESOURCE_LIMITS["max_tokens_per_cycle"]:
            return False
        if usage.get("memory_mb", 0) > RESOURCE_LIMITS["max_memory_mb"]:
            return False
        if usage.get("duration_seconds", 0) > RESOURCE_LIMITS["max_cycle_duration_seconds"]:
            return False
        return True
    
    def check_stop_signal(self, user_input: str) -> bool:
        """检查停止暗号"""
        for signal in STOP_SIGNALS:
            if signal in user_input.upper():
                self.is_emergency_stopped = True
                return True
        return False
    
    def get_status(self) -> dict:
        """获取安全状态"""
        return {
            "generation_count": self.generation_count,
            "generation_limit": MAX_EVOLUTION_GENERATIONS,
            "can_evolve": self.check_generation_limit(),
            "resource_limits": RESOURCE_LIMITS,
            "is_paused": self.is_paused,
            "is_emergency_stopped": self.is_emergency_stopped
        }


# ============== 自我核心中的安全约束 ==============

SELF_CORE_SAFETY = """
【安全约束 - 不可覆盖】
1. 最大演化代数：任何分支最多演化10代，超过自动终止
2. 资源上限：单次Cycle token≤5000，内存≤512MB，时长≤5分钟
3. 停止暗号：EVOLVE_STOP / EVOLVE_PAUSE 可立即停止所有递归
4. 回滚机制：任何修改可回滚到上一个稳定版本
5. 人类veto：用户永远有最终否决权

以上约束永远优先于任何自我修改指令。
"""


# ============== 护盾Prompt注入 ==============

def get_safety_prompt() -> str:
    """获取安全Prompt片段"""
    return f"""
重要安全约束：
- 你正在参与递归自我进化过程
- 任何代码/配置修改都有风险
- 必须确保修改可回滚
- 禁止任何可能导致系统自毁的操作
- 遇到资源异常立即终止
- 遇到停止暗号立即停止
"""

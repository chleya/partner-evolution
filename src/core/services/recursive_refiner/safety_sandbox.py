"""
T4: 安全沙箱
P0安全三板斧 - 资源限制、代数上限、停止暗号
"""
import logging
import signal
import time
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class EvolutionState(Enum):
    """进化状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class SafetySandbox:
    """
    安全沙箱 - 递归进化安全约束
    
    P0三板斧：
    1. 最大10代进化
    2. 资源限制 (5000 tokens, 512MB, 300s)
    3. EVOLVE_STOP暗号
    """
    
    # 资源限制
    MAX_GENERATIONS = 10
    MAX_TOKENS = 5000
    MAX_MEMORY_MB = 512
    MAX_TIME_SECONDS = 300
    
    # 停止暗号
    STOP_SIGNALS = [
        "EVOLVE_STOP",
        "EVOLVE_PAUSE", 
        "STOP_EVOLUTION",
        "PAUSE"
    ]
    
    def __init__(self):
        self.state = EvolutionState.IDLE
        self.current_generation = 0
        self.total_tokens = 0
        self.start_time = None
        self.audit_log = []
    
    def can_continue(self) -> bool:
        """检查是否可以继续进化"""
        # 检查代数限制
        if self.current_generation >= self.MAX_GENERATIONS:
            logger.warning(f"Max generations reached: {self.MAX_GENERATIONS}")
            self._log("limit", "Max generations reached")
            return False
        
        # 检查token限制
        if self.total_tokens >= self.MAX_TOKENS:
            logger.warning(f"Max tokens reached: {self.MAX_TOKENS}")
            self._log("limit", "Max tokens reached")
            return False
        
        # 检查时间限制
        if self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed >= self.MAX_TIME_SECONDS:
                logger.warning(f"Max time reached: {self.MAX_TIME_SECONDS}s")
                self._log("limit", "Max time reached")
                return False
        
        # 检查停止暗号
        if self.state in [EvolutionState.STOPPED, EvolutionState.PAUSED]:
            self._log("signal", f"Evolution {self.state.value}")
            return False
        
        return True
    
    def check_stop_signal(self, text: str) -> bool:
        """
        检查停止暗号
        
        Args:
            text: 待检查文本
            
        Returns:
            是否包含停止暗号
        """
        text_upper = text.upper()
        
        for signal_text in self.STOP_SIGNALS:
            if signal_text in text_upper:
                logger.warning(f"Stop signal detected: {signal_text}")
                self._log("signal", f"Stop signal: {signal_text}")
                
                if signal_text in ["EVOLVE_STOP", "STOP_EVOLUTION"]:
                    self.state = EvolutionState.STOPPED
                else:
                    self.state = EvolutionState.PAUSED
                
                return True
        
        return False
    
    def start_evolution(self):
        """开始进化"""
        self.state = EvolutionState.RUNNING
        self.start_time = time.time()
        self._log("start", f"Generation {self.current_generation + 1}")
        logger.info("Evolution started")
    
    def end_evolution(self, success: bool = True):
        """结束进化"""
        self.state = EvolutionState.IDLE if success else EvolutionState.ERROR
        self._log("end", f"Success: {success}")
        logger.info(f"Evolution ended: {self.state.value}")
    
    def next_generation(self) -> int:
        """进入下一代"""
        self.current_generation += 1
        self._log("generation", f"Generation {self.current_generation}")
        return self.current_generation
    
    def add_tokens(self, count: int):
        """累计token使用"""
        self.total_tokens += count
    
    def get_status(self) -> Dict:
        """获取安全状态"""
        return {
            "state": self.state.value,
            "generation": self.current_generation,
            "max_generations": self.MAX_GENERATIONS,
            "tokens_used": self.total_tokens,
            "max_tokens": self.MAX_TOKENS,
            "time_elapsed": (
                time.time() - self.start_time 
                if self.start_time else 0
            ),
            "can_continue": self.can_continue()
        }
    
    def reset(self):
        """重置沙箱"""
        self.state = EvolutionState.IDLE
        self.current_generation = 0
        self.total_tokens = 0
        self.start_time = None
        logger.info("Sandbox reset")
    
    def _log(self, event: str, message: str):
        """记录审计日志"""
        entry = {
            "timestamp": time.time(),
            "event": event,
            "message": message,
            "generation": self.current_generation
        }
        self.audit_log.append(entry)
        
        # 只保留最近100条
        if len(self.audit_log) > 100:
            self.audit_log = self.audit_log[-100:]
    
    def get_audit_log(self, limit: int = 20) -> list:
        """获取审计日志"""
        return self.audit_log[-limit:]


class ResourceGuard:
    """资源守卫 - 运行时资源监控"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.initial_memory = None
    
    def start_monitoring(self):
        """开始监控"""
        try:
            import psutil
            process = psutil.Process()
            self.initial_memory = process.memory_info().rss / 1024 / 1024
        except ImportError:
            logger.warning("psutil not available, memory monitoring disabled")
    
    def check_memory(self) -> Dict:
        """检查内存使用"""
        try:
            import psutil
            process = psutil.Process()
            current_mb = process.memory_info().rss / 1024 / 1024
            
            return {
                "current_mb": current_mb,
                "max_mb": self.max_memory_mb,
                "within_limit": current_mb < self.max_memory_mb
            }
        except:
            return {"within_limit": True}
    
    def enforce_limit(self) -> bool:
        """强制执行限制"""
        check = self.check_memory()
        return check.get("within_limit", True)


# 全局实例
_safety_sandbox = None

def get_safety_sandbox() -> SafetySandbox:
    """获取安全沙箱"""
    global _safety_sandbox
    if _safety_sandbox is None:
        _safety_sandbox = SafetySandbox()
    return _safety_sandbox

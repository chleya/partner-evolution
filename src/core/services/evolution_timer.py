"""
Evolution Timer - 定时触发器
自动触发进化周期
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Callable

logger = logging.getLogger(__name__)


class EvolutionTimer:
    """
    进化定时器 - 自动触发进化周期
    
    功能：
    1. 定时触发进化
    2. 条件触发（根据系统状态）
    3. 手动触发
    """
    
    # 触发间隔选项
    INTERVALS = {
        "hourly": 3600,      # 每小时
        "daily": 86400,     # 每天
        "weekly": 604800,   # 每周
    }
    
    def __init__(self, scheduler=None):
        self.scheduler = scheduler
        self.is_running = False
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.interval = self.INTERVALS["daily"]  # 默认每天
        self.condition_check: Optional[Callable] = None
    
    def set_interval(self, interval_name: str):
        """设置触发间隔"""
        if interval_name in self.INTERVALS:
            self.interval = self.INTERVALS[interval_name]
            logger.info(f"Evolution interval set to: {interval_name}")
    
    def set_custom_interval(self, seconds: int):
        """设置自定义间隔（秒）"""
        self.interval = seconds
        logger.info(f"Evolution interval set to: {seconds}s")
    
    def set_condition(self, condition_fn: Callable[[], bool]):
        """设置触发条件"""
        self.condition_check = condition_fn
    
    async def start(self):
        """启动定时器"""
        if self.is_running:
            logger.warning("Timer already running")
            return
        
        self.is_running = True
        logger.info("Evolution timer started")
        
        while self.is_running:
            try:
                # 检查是否应该运行
                should_run = True
                
                # 检查条件
                if self.condition_check:
                    should_run = self.condition_check()
                
                # 检查间隔
                if self.last_run:
                    import time
                    elapsed = time.time() - self.last_run
                    if elapsed < self.interval:
                        should_run = False
                
                if should_run:
                    await self.run_evolution()
                
                # 等待
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"Timer error: {e}")
                await asyncio.sleep(60)
    
    async def run_evolution(self):
        """运行进化周期"""
        import time
        self.last_run = time.time()
        self.next_run = self.last_run + self.interval
        self.run_count += 1
        
        logger.info(f"Starting evolution cycle #{self.run_count}")
        
        if self.scheduler:
            result = await self.scheduler.start_evolution_cycle()
            
            logger.info(f"Evolution #{self.run_count} complete: {result.get('success', False)}")
            
            return result
        
        return {"success": False, "reason": "No scheduler"}
    
    async def stop(self):
        """停止定时器"""
        self.is_running = False
        logger.info("Evolution timer stopped")
    
    def get_status(self) -> Dict:
        """获取状态"""
        import time
        
        next_expected = None
        if self.last_run:
            next_expected = datetime.fromtimestamp(
                self.last_run + self.interval,
                tz=timezone.utc
            ).isoformat()
        
        return {
            "is_running": self.is_running,
            "run_count": self.run_count,
            "last_run": datetime.fromtimestamp(
                self.last_run, tz=timezone.utc
            ).isoformat() if self.last_run else None,
            "next_run": next_expected,
            "interval_seconds": self.interval
        }
    
    async def trigger_now(self):
        """立即触发"""
        return await self.run_evolution()


# 全局实例
_timer = None

def get_evolution_timer(scheduler=None) -> EvolutionTimer:
    """获取定时器"""
    global _timer
    if _timer is None:
        _timer = EvolutionTimer(scheduler)
    return _timer

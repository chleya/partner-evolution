"""
自动状态持久化管理
解决 M-003 持久化机制不完善问题
"""
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# 状态目录
STATE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "state"


class StatePersistence:
    """自动状态持久化管理"""
    
    def __init__(self, state_dir: Path = None):
        self.state_dir = state_dir or STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件路径
        self.thinking_stats_file = self.state_dir / "thinking_stats.json"
        self.runtime_config_file = self.state_dir / "runtime_config.json"
        self.cycle_history_file = self.state_dir / "cycle_history.json"
        
        # 自动保存间隔（秒）
        self.auto_save_interval = 300  # 5分钟
    
    def save_thinking_stats(self, stats: Dict):
        """保存思考统计"""
        try:
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stats": stats
            }
            with open(self.thinking_stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Thinking stats saved")
            return True
        except Exception as e:
            logger.warning(f"Failed to save thinking stats: {e}")
            return False
    
    def load_thinking_stats(self) -> Optional[Dict]:
        """加载思考统计"""
        if not self.thinking_stats_file.exists():
            return None
        
        try:
            with open(self.thinking_stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("stats")
        except Exception as e:
            logger.warning(f"Failed to load thinking stats: {e}")
            return None
    
    def save_runtime_config(self, config: Dict):
        """保存运行时配置"""
        try:
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": config
            }
            with open(self.runtime_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Runtime config saved")
            return True
        except Exception as e:
            logger.warning(f"Failed to save runtime config: {e}")
            return False
    
    def load_runtime_config(self) -> Optional[Dict]:
        """加载运行时配置"""
        if not self.runtime_config_file.exists():
            return None
        
        try:
            with open(self.runtime_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("config")
        except Exception as e:
            logger.warning(f"Failed to load runtime config: {e}")
            return None
    
    def save_cycle_history(self, cycle_data: Dict):
        """保存周期历史"""
        try:
            # 读取现有历史
            history = []
            if self.cycle_history_file.exists():
                with open(self.cycle_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 添加新记录
            history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": cycle_data
            })
            
            # 只保留最近100条
            history = history[-100:]
            
            # 保存
            with open(self.cycle_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cycle history saved, total: {len(history)}")
            return True
        except Exception as e:
            logger.warning(f"Failed to save cycle history: {e}")
            return False
    
    def load_cycle_history(self, limit: int = 10) -> list:
        """加载周期历史"""
        if not self.cycle_history_file.exists():
            return []
        
        try:
            with open(self.cycle_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-limit:]
        except Exception as e:
            logger.warning(f"Failed to load cycle history: {e}")
            return []
    
    def get_last_state_timestamp(self) -> Optional[float]:
        """获取最后状态时间戳"""
        if not self.thinking_stats_file.exists():
            return None
        
        try:
            return os.path.getmtime(self.thinking_stats_file)
        except:
            return None
    
    def needs_restore(self, max_age_seconds: int = 3600) -> bool:
        """检查是否需要恢复状态"""
        last_ts = self.get_last_state_timestamp()
        if last_ts is None:
            return False
        
        age = time.time() - last_ts
        return age < max_age_seconds


# 全局实例
_persistence = None

def get_persistence() -> StatePersistence:
    """获取持久化管理器"""
    global _persistence
    if _persistence is None:
        _persistence = StatePersistence()
    return _persistence

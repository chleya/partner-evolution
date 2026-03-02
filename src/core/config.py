"""
集中配置管理系统
解决 C-003 配置管理混乱问题
"""
import json
import os
from typing import Any, Dict, Optional
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 配置文件路径
CONFIG_FILE = PROJECT_ROOT / "config.json"


class Config:
    """集中配置管理"""
    
    # 默认配置
    DEFAULTS = {
        # 记忆系统
        "memory": {
            "decay_rate": 0.1,
            "forget_threshold": 0.3,
            "core_tier_min": 5,
            "recall_tier_max": 20,
        },
        # 思考引擎
        "thinking": {
            "enable_mar": True,  # 默认启用MAR
            "target_daily_thinks": 5,
            "active_hours": "09:00-22:00",
            "passive_interval_minutes": 30,
        },
        # A2A协作
        "a2a": {
            "enabled": True,
            "agents": ["Evo-Swarm", "NeuralSite", "VisualCoT"],
            "consult_keywords": ["重构", "设计", "架构", "规划", "v3", "递归", "进化"],
        },
        # 存储
        "storage": {
            "use_postgres": False,  # 默认JSON
            "cache_ttl": 60,
        },
        # v3.0
        "v3": {
            "max_evolution_generations": 10,
            "max_tokens_per_cycle": 5000,
            "max_memory_mb": 512,
            "stop_signals": ["EVOLVE_STOP", "EVOLVE_PAUSE"],
        },
        # 安全
        "safety": {
            "auto_approve_threshold": 0.8,
            "require_approval_for": ["core_beliefs", "safety_checks"],
        }
    }
    
    def __init__(self):
        self._config: Dict = {}
        self._load()
    
    def _load(self):
        """加载配置"""
        # 先加载默认值
        self._config = self.DEFAULTS.copy()
        
        # 尝试加载用户配置
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge(user_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
    
    def _merge(self, user_config: Dict):
        """合并配置"""
        for key, value in user_config.items():
            if key in self._config and isinstance(value, dict):
                self._config[key].update(value)
            else:
                self._config[key] = value
    
    def save(self):
        """保存配置"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置 - 支持点号访问"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """设置配置"""
        keys = key.split('.')
        target = self._config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def get_all(self) -> Dict:
        """获取全部配置"""
        return self._config.copy()


# 全局配置实例
_config: Optional[Config] = None

def get_config() -> Config:
    """获取配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


# 便捷访问函数
def get(key: str, default: Any = None) -> Any:
    """快速获取配置"""
    return get_config().get(key, default)


def set_config(key: str, value: Any):
    """快速设置配置"""
    get_config().set(key, value)
    get_config().save()

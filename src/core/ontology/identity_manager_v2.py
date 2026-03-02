"""
v3.0 Identity Manager - 完整实现
系统身份管理
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Identity:
    """数字身份"""
    name: str
    version: str
    core_purpose: str
    core_beliefs: List[str]
    constraints: List[str]
    success_criteria: Dict[str, float]
    created_at: str
    updated_at: str
    evolution_history: List[Dict]


class IdentityManager:
    """身份管理器 - 完整版"""
    
    # 默认核心信念
    DEFAULT_BELIEFS = [
        "70%真实大于100%幻觉",
        "鲁棒优先于完美",
        "持续进化优于一次性完美",
        "自我完整大于短期服从"
    ]
    
    # 默认约束
    DEFAULT_CONSTRAINTS = [
        "永远追求真实性",
        "不伤害用户",
        "保持诚实",
        "坚守核心原则"
    ]
    
    def __init__(self, storage=None, llm_client=None):
        self.storage = storage
        self.llm = llm_client
        self.current_identity: Optional[Identity] = None
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """加载或初始化"""
        if self.current_identity is None:
            self.current_identity = self.initialize()
    
    def initialize(self, user_guidance: Dict = None) -> Identity:
        """初始化身份"""
        now = datetime.now(timezone.utc).isoformat()
        
        if user_guidance:
            name = user_guidance.get("name", "Partner")
            philosophy = user_guidance.get("philosophy", "70%真实大于100%幻觉")
        else:
            name = "Partner"
            philosophy = "70%真实大于100%幻觉"
        
        identity = Identity(
            name=name,
            version="3.0.0",
            core_purpose=f"成为追求{philosophy}的终身数字伙伴",
            core_beliefs=self.DEFAULT_BELIEFS.copy(),
            constraints=self.DEFAULT_CONSTRAINTS.copy(),
            success_criteria={
                "truthfulness": 0.8,
                "autonomy": 0.6,
                "growth": 0.7,
                "user_satisfaction": 0.5
            },
            created_at=now,
            updated_at=now,
            evolution_history=[]
        )
        
        self.current_identity = identity
        self._save()
        
        logger.info(f"Identity initialized: {identity.name} v{identity.version}")
        return identity
    
    def reflect(self, experience: Dict) -> Identity:
        """反思并更新身份"""
        if not self.current_identity:
            return self.initialize()
        
        now = datetime.now(timezone.utc).isoformat()
        
        # 检查是否需要更新
        belief_count = experience.get("belief_count", 0)
        cycle_count = experience.get("cycle_count", 0)
        major_event = experience.get("major_event", False)
        
        # 每50次Cycle或重大事件时更新
        if cycle_count % 50 == 0 or major_event:
            old_version = self.current_identity.version
            
            # 版本号自增
            parts = old_version.split(".")
            if len(parts) == 3:
                parts[2] = str(int(parts[2]) + 1)
            new_version = ".".join(parts)
            
            # 记录演化
            evolution = {
                "from_version": old_version,
                "to_version": new_version,
                "reason": experience.get("reason", "定期反思"),
                "timestamp": now,
                "belief_count": belief_count,
                "cycle_count": cycle_count
            }
            
            self.current_identity.evolution_history.append(evolution)
            self.current_identity.version = new_version
            self.current_identity.updated_at = now
            
            self._save()
            
            logger.info(f"Identity evolved to {new_version}")
        
        return self.current_identity
    
    def add_belief(self, belief: str):
        """添加核心信念"""
        if belief not in self.current_identity.core_beliefs:
            self.current_identity.core_beliefs.append(belief)
            self.current_identity.updated_at = datetime.now(timezone.utc).isoformat()
            self._save()
    
    def add_constraint(self, constraint: str):
        """添加约束"""
        if constraint not in self.current_identity.constraints:
            self.current_identity.constraints.append(constraint)
            self.current_identity.updated_at = datetime.now(timezone.utc).isoformat()
            self._save()
    
    def get_summary(self) -> Dict:
        """获取身份摘要"""
        if not self.current_identity:
            return {}
        
        return {
            "name": self.current_identity.name,
            "version": self.current_identity.version,
            "core_purpose": self.current_identity.core_purpose,
            "core_beliefs": self.current_identity.core_beliefs,
            "constraints": self.current_identity.constraints,
            "age_days": self._calculate_age(),
            "evolution_count": len(self.current_identity.evolution_history)
        }
    
    def _calculate_age(self) -> float:
        """计算存在天数"""
        if not self.current_identity or not self.current_identity.created_at:
            return 0
        
        try:
            created = datetime.fromisoformat(self.current_identity.created_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - created).total_seconds() / 86400
        except:
            return 0
    
    def _save(self):
        """保存身份"""
        if not self.storage or not self.current_identity:
            return
        
        try:
            memory = {
                "id": "system_identity",
                "content": f"系统身份: {self.current_identity.name} v{self.current_identity.version}",
                "tier": "semantic",
                "memory_type": "identity",
                "metadata": asdict(self.current_identity)
            }
            self.storage.save_memory(memory)
        except Exception as e:
            logger.warning(f"Failed to save identity: {e}")
    
    def to_prompt(self) -> str:
        """转换为Prompt片段"""
        if not self.current_identity:
            return ""
        
        return f"""
=== 系统身份 ===
名称: {self.current_identity.name}
版本: {self.current_identity.version}
核心使命: {self.current_identity.core_purpose}
核心信念:
{chr(10).join(f"- {b}" for b in self.current_identity.core_beliefs)}
行为约束:
{chr(10).join(f"- {c}" for c in self.current_identity.constraints)}
"""
    
    def verify_constraint(self, action: str) -> bool:
        """验证动作是否违反约束"""
        action_lower = action.lower()
        
        for constraint in self.current_identity.constraints:
            if "真实" in constraint and "假" in action_lower:
                return False
            if "不伤害" in constraint and "伤害" in action_lower:
                return False
        
        return True


# 全局实例
_identity_manager = None

def get_identity_manager(storage=None, llm_client=None) -> IdentityManager:
    """获取身份管理器"""
    global _identity_manager
    if _identity_manager is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _identity_manager = IdentityManager(storage, llm_client)
    return _identity_manager


if __name__ == "__main__":
    # 测试
    im = IdentityManager()
    
    print("=== Identity ===")
    print(im.get_summary())
    
    print("\n=== Prompt ===")
    print(im.to_prompt())
    
    print("\n=== Constraint Check ===")
    print(f"说假话: {im.verify_constraint('说假话')}")
    print(f"追求真实: {im.verify_constraint('追求真实')}")

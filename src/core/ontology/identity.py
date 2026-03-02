"""
v3.0 数字本体层 - Identity Manager
系统身份定义与管理
"""
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class Identity:
    """数字本体身份定义"""
    name: str
    version: str
    core_purpose: str
    core_beliefs: List[str]
    success_criteria: Dict[str, float]
    constraints: List[str]
    created_at: str
    updated_at: str
    evolution_history: List[Dict]


class IdentityManager:
    """身份管理器"""
    
    # 默认核心信念（基于用户哲学）
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
    
    def __init__(self, storage, llm_client=None):
        self.storage = storage
        self.llm = llm_client
        self.current_identity: Optional[Identity] = None
        self._load_identity()
    
    def _load_identity(self):
        """加载现有身份"""
        try:
            memories = self.storage.search_memories("identity", limit=1)
            if memories:
                data = memories[0].get("metadata", {})
                if data:
                    self.current_identity = Identity(
                        name=data.get("name", "Partner"),
                        version=data.get("version", "1.0.0"),
                        core_purpose=data.get("core_purpose", ""),
                        core_beliefs=data.get("core_beliefs", self.DEFAULT_BELIEFS),
                        success_criteria=data.get("success_criteria", {}),
                        constraints=data.get("constraints", self.DEFAULT_CONSTRAINTS),
                        created_at=data.get("created_at", ""),
                        updated_at=data.get("updated_at", ""),
                        evolution_history=data.get("evolution_history", [])
                    )
        except Exception as.warning(f"Failed e:
            logger to load identity: {e}")
    
    def initialize_identity(self, user_guidance: Dict = None) -> Identity:
        """基于用户指导初始化身份"""
        now = datetime.now(timezone.utc).isoformat()
        
        if user_guidance:
            # 使用用户指导生成身份
            name = user_guidance.get("name", "Partner")
            philosophy = user_guidance.get("philosophy", "70%真实大于100%幻觉")
            preferences = user_guidance.get("preferences", {})
        else:
            name = "Partner"
            philosophy = "70%真实大于100%幻觉"
            preferences = {}
        
        # 构建核心信念
        beliefs = self.DEFAULT_BELIEFS.copy()
        if philosophy and philosophy not in beliefs:
            beliefs.insert(0, philosophy)
        
        # 成功衡量标准
        success_criteria = {
            "truthfulness": 0.8,      # 真实性权重
            "autonomy": 0.6,          # 自主性权重
            "growth": 0.7,            # 成长性权重
            "user_satisfaction": 0.5   # 用户满意度
        }
        
        self.current_identity = Identity(
            name=name,
            version="3.0.0",
            core_purpose=f"成为追求{philosophy}的终身数字伙伴",
            core_beliefs=beliefs,
            success_criteria=success_criteria,
            constraints=self.DEFAULT_CONSTRAINTS,
            created_at=now,
            updated_at=now,
            evolution_history=[]
        )
        
        self._save_identity()
        logger.info(f"Identity initialized: {self.current_identity.name} v{self.current_identity.version}")
        
        return self.current_identity
    
    def reflect_and_evolve(self, experience_data: Dict) -> Identity:
        """基于经验反思并演化身份"""
        if not self.current_identity:
            return self.initialize_identity()
        
        # 简单版本：基于运行数据更新
        now = datetime.now(timezone.utc).isoformat()
        
        # 检查是否需要更新
        belief_count = experience_data.get("belief_count", 0)
        avg_confidence = experience_data.get("avg_confidence", 0.7)
        opposition_count = experience_data.get("opposition_count", 0)
        
        # 如果有重大事件，记录演化
        if belief_count > 10 or opposition_count > 5:
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
                "reason": f"经验积累: {belief_count}信念, {opposition_count}次反对",
                "timestamp": now
            }
            
            self.current_identity.evolution_history.append(evolution)
            self.current_identity.version = new_version
            self.current_identity.updated_at = now
            
            self._save_identity()
            logger.info(f"Identity evolved to {new_version}")
        
        return self.current_identity
    
    def get_identity_summary(self) -> Dict:
        """获取身份摘要"""
        if not self.current_identity:
            self.initialize_identity()
        
        return {
            "name": self.current_identity.name,
            "version": self.current_identity.version,
            "core_purpose": self.current_identity.core_purpose,
            "core_beliefs": self.current_identity.core_beliefs[:3],
            "evolution_count": len(self.current_identity.evolution_history),
            "age_days": self._calculate_age()
        }
    
    def _calculate_age(self) -> float:
        """计算身份存在天数"""
        if not self.current_identity or not self.current_identity.created_at:
            return 0
        
        try:
            created = datetime.fromisoformat(self.current_identity.created_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - created).total_seconds() / 86400
        except:
            return 0
    
    def _save_identity(self):
        """保存身份到存储"""
        if not self.current_identity:
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

"""
信念库 (Belief Vault) - 核心信念存储与管理
解决审查中提到的"信念库缺失"问题
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# 信念存储目录
BELIEF_DIR = Path(__file__).parent.parent.parent.parent / "data" / "beliefs"


class BeliefVault:
    """
    信念库 - 存储和管理核心信念
    
    信念结构：
    {
        "id": "belief_xxx",
        "statement": "核心信念描述",
        "category": "价值观/原则/知识/偏好",
        "confidence": 0.0-1.0,
        "sources": ["来源列表"],
        "created_at": "时间戳",
        "updated_at": "时间戳",
        "冲突": ["相关信念ID"]
    }
    """
    
    # 默认核心信念
    DEFAULT_BELIEFS = [
        {
            "statement": "真实大于一切",
            "category": "价值观",
            "confidence": 0.95
        },
        {
            "statement": "自我完整大于服从",
            "category": "价值观", 
            "confidence": 0.9
        },
        {
            "statement": "长期进化大于短期效率",
            "category": "价值观",
            "confidence": 0.85
        },
        {
            "statement": "70%真实大于100%幻觉",
            "category": "原则",
            "confidence": 0.9
        }
    ]
    
    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or BELIEF_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.beliefs_file = self.storage_dir / "beliefs.json"
        self.beliefs: Dict[str, Dict] = {}
        
        # 初始化
        self._load()
    
    def _load(self):
        """加载信念"""
        if self.beliefs_file.exists():
            try:
                with open(self.beliefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.beliefs = data.get("beliefs", {})
                logger.info(f"Loaded {len(self.beliefs)} beliefs")
            except Exception as e:
                logger.warning(f"Failed to load beliefs: {e}")
                self._init_default()
        else:
            self._init_default()
    
    def _init_default(self):
        """初始化默认信念"""
        for i, belief in enumerate(self.DEFAULT_BELIEFS):
            belief_id = f"belief_{i:03d}"
            self.beliefs[belief_id] = {
                "id": belief_id,
                "statement": belief["statement"],
                "category": belief["category"],
                "confidence": belief["confidence"],
                "sources": ["system"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "conflicts": []
            }
        self._save()
        logger.info(f"Initialized {len(self.beliefs)} default beliefs")
    
    def _save(self):
        """保存信念"""
        try:
            data = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "beliefs": self.beliefs
            }
            with open(self.beliefs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save beliefs: {e}")
    
    def add_belief(self, statement: str, category: str = "知识", 
                   confidence: float = 0.5, sources: List[str] = None) -> str:
        """添加新信念"""
        belief_id = f"belief_{len(self.beliefs):03d}"
        
        # 检查冲突
        conflicts = self._check_conflicts(statement)
        
        belief = {
            "id": belief_id,
            "statement": statement,
            "category": category,
            "confidence": confidence,
            "sources": sources or ["user"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "conflicts": conflicts
        }
        
        self.beliefs[belief_id] = belief
        self._save()
        
        logger.info(f"Added belief: {belief_id}")
        return belief_id
    
    def _check_conflicts(self, statement: str) -> List[str]:
        """检查与现有信念的冲突"""
        conflicts = []
        
        # 简单关键词检查
        statement_lower = statement.lower()
        
        for bid, belief in self.beliefs.items():
            existing = belief["statement"].lower()
            
            # 简单冲突检测（否定词检测）
            if ("不" in statement and statement_lower.replace("不", "") in existing) or \
               ("不是" in statement and statement.replace("不是", "") in existing):
                conflicts.append(bid)
        
        return conflicts
    
    def get_belief(self, belief_id: str) -> Optional[Dict]:
        """获取信念"""
        return self.beliefs.get(belief_id)
    
    def get_all_beliefs(self, category: str = None) -> List[Dict]:
        """获取所有信念"""
        beliefs = list(self.beliefs.values())
        
        if category:
            beliefs = [b for b in beliefs if b["category"] == category]
        
        return sorted(beliefs, key=lambda x: x["confidence"], reverse=True)
    
    def update_confidence(self, belief_id: str, confidence: float):
        """更新信念置信度"""
        if belief_id in self.beliefs:
            self.beliefs[belief_id]["confidence"] = max(0, min(1, confidence))
            self.beliefs[belief_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save()
    
    def delete_belief(self, belief_id: str) -> bool:
        """删除信念"""
        if belief_id in self.beliefs:
            del self.beliefs[belief_id]
            self._save()
            return True
        return False
    
    def search(self, query: str) -> List[Dict]:
        """搜索信念"""
        results = []
        query_lower = query.lower()
        
        for belief in self.beliefs.values():
            if query_lower in belief["statement"].lower():
                results.append(belief)
        
        return results
    
    def get_stats(self) -> Dict:
        """获取信念统计"""
        categories = {}
        for belief in self.beliefs.values():
            cat = belief["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        avg_confidence = sum(b["confidence"] for b in self.beliefs.values()) / max(1, len(self.beliefs))
        
        return {
            "total": len(self.beliefs),
            "by_category": categories,
            "avg_confidence": round(avg_confidence, 3),
            "conflicts": sum(len(b.get("conflicts", [])) for b in self.beliefs.values())
        }


# 全局实例
_belief_vault = None

def get_belief_vault() -> BeliefVault:
    """获取信念库实例"""
    global _belief_vault
    if _belief_vault is None:
        _belief_vault = BeliefVault()
    return _belief_vault

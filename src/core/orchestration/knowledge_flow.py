"""
跨项目知识流动机制
支持NeuralSite ↔ Evo-Swarm ↔ VisualCoT双向同步
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """同步方向"""
    UNIDIRECTIONAL = "unidirectional"    # 单向
    BIDIRECTIONAL = "bidirectional"       # 双向
    MULTICAST = "multicast"               # 多播


class KnowledgeType(Enum):
    """知识类型"""
    CODE = "code"              # 代码
    CONFIG = "config"          # 配置
    DOCUMENTATION = "docs"    # 文档
    PATTERN = "pattern"        # 模式
    INSIGHT = "insight"       # 洞察
    METRIC = "metric"         # 指标


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    knowledge_type: KnowledgeType
    source_project: str
    content: Any
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sync_status: str = "pending"  # pending, synced, failed


@dataclass
class KnowledgeLink:
    """知识链接"""
    from_item_id: str
    to_item_id: str
    link_type: str  # "related", "derived", "depends_on"
    strength: float = 0.5


@dataclass
class SyncEvent:
    """同步事件"""
    event_id: str
    timestamp: str
    source_project: str
    target_project: str
    items_synced: List[str]
    direction: SyncDirection
    status: str  # success, partial, failed


class KnowledgeFlow:
    """
    跨项目知识流动机制
    
    特性：
    - 多项目知识同步
    - 知识链接自动更新
    - 双向/单向同步
    - 知识冲突解决
    - 同步历史追踪
    """
    
    # 项目角色映射
    PROJECT_ROLES = {
        "NeuralSite": {"role": "executor", "capabilities": ["code_execution", "drawing_generation"]},
        "Evo-Swarm": {"role": "planner", "capabilities": ["planning", "optimization", "chain_of_thought"]},
        "VisualCoT": {"role": "perceiver", "capabilities": ["vision_understanding", "screenshot_analysis"]}
    }
    
    def __init__(self):
        self.knowledge_store: Dict[str, Dict[str, KnowledgeItem]] = {
            "NeuralSite": {},
            "Evo-Swarm": {},
            "VisualCoT": {}
        }
        self.knowledge_links: List[KnowledgeLink] = []
        self.sync_history: List[SyncEvent] = []
        self.sync_rules: Dict[str, Dict] = {}
        
        # 初始化同步规则
        self._init_sync_rules()
    
    def _init_sync_rules(self):
        """初始化同步规则"""
        self.sync_rules = {
            # NeuralSite -> Evo-Swarm: 代码模式可被规划使用
            ("NeuralSite", "Evo-Swarm"): {
                "direction": SyncDirection.BIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.CODE, KnowledgeType.PATTERN],
                "auto_sync": True
            },
            # NeuralSite -> VisualCoT: 代码可被可视化理解
            ("NeuralSite", "VisualCoT"): {
                "direction": SyncDirection.UNIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.CODE, KnowledgeType.INSIGHT],
                "auto_sync": True
            },
            # Evo-Swarm -> NeuralSite: 规划结果可被执行
            ("Evo-Swarm", "NeuralSite"): {
                "direction": SyncDirection.BIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.CONFIG, KnowledgeType.PATTERN],
                "auto_sync": True
            },
            # Evo-Swarm -> VisualCoT: 思维链可被视觉理解
            ("Evo-Swarm", "VisualCoT"): {
                "direction": SyncDirection.UNIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.INSIGHT, KnowledgeType.METRIC],
                "auto_sync": True
            },
            # VisualCoT -> NeuralSite: 视觉理解可指导代码生成
            ("VisualCoT", "NeuralSite"): {
                "direction": SyncDirection.UNIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.INSIGHT],
                "auto_sync": True
            },
            # VisualCoT -> Evo-Swarm: 感知结果可影响规划
            ("VisualCoT", "Evo-Swarm"): {
                "direction": SyncDirection.UNIDIRECTIONAL,
                "knowledge_types": [KnowledgeType.INSIGHT, KnowledgeType.METRIC],
                "auto_sync": True
            }
        }
    
    def add_knowledge(
        self,
        project: str,
        knowledge_type: KnowledgeType,
        content: Any,
        metadata: Dict = None,
        auto_sync: bool = False  # 默认关闭自动同步
    ) -> str:
        """添加知识"""
        if project not in self.knowledge_store:
            self.knowledge_store[project] = {}
        
        # 生成ID
        item_id = f"{project}_{knowledge_type.value}_{len(self.knowledge_store[project])}"
        
        item = KnowledgeItem(
            id=item_id,
            knowledge_type=knowledge_type,
            source_project=project,
            content=content,
            metadata=metadata or {}
        )
        
        self.knowledge_store[project][item_id] = item
        
        # 自动触发同步（可选）
        if auto_sync:
            self._auto_sync(project, item_id)
        
        logger.info(f"Added knowledge: {item_id}")
        return item_id
    
    def _auto_sync(self, source_project: str, item_id: str):
        """自动同步"""
        item = self.knowledge_store[source_project].get(item_id)
        if not item:
            return
        
        # 查找目标项目
        for target_project in self.knowledge_store:
            if target_project == source_project:
                continue
            
            rule_key = (source_project, target_project)
            rule = self.sync_rules.get(rule_key)
            
            if rule and rule.get("auto_sync") and item.knowledge_type in rule["knowledge_types"]:
                self.sync_knowledge(source_project, target_project, [item_id])
    
    def sync_knowledge(
        self,
        source_project: str,
        target_project: str,
        item_ids: List[str],
        direction: SyncDirection = None
    ) -> SyncEvent:
        """同步知识"""
        if source_project not in self.knowledge_store:
            raise ValueError(f"Unknown source project: {source_project}")
        if target_project not in self.knowledge_store:
            raise ValueError(f"Unknown target project: {target_project}")
        
        # 确定同步方向
        if direction is None:
            rule_key = (source_project, target_project)
            rule = self.sync_rules.get(rule_key, {})
            direction = rule.get("direction", SyncDirection.UNIDIRECTIONAL)
        
        synced_items = []
        
        # 同步知识项
        for item_id in item_ids:
            source_item = self.knowledge_store[source_project].get(item_id)
            if not source_item:
                continue
            
            # 创建副本
            target_item_id = f"{target_project}_{source_item.knowledge_type.value}_{source_item.id.split('_')[-1]}"
            target_item = KnowledgeItem(
                id=target_item_id,
                knowledge_type=source_item.knowledge_type,
                source_project=source_project,
                content=source_item.content,
                metadata={**source_item.metadata, "synced_from": source_project},
                sync_status="synced"
            )
            
            self.knowledge_store[target_project][target_item_id] = target_item
            synced_items.append(target_item_id)
            
            # 创建知识链接
            self.add_link(item_id, target_item_id, "synced")
        
        # 记录同步事件
        event = SyncEvent(
            event_id=f"sync_{len(self.sync_history)}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_project=source_project,
            target_project=target_project,
            items_synced=synced_items,
            direction=direction,
            status="success" if len(synced_items) == len(item_ids) else "partial"
        )
        self.sync_history.append(event)
        
        # 双向同步（仅当显式指定时）
        if direction == SyncDirection.BIDIRECTIONAL and not getattr(self, '_in_bidirectional_sync', False):
            self._in_bidirectional_sync = True
            self.sync_knowledge(target_project, source_project, synced_items, SyncDirection.UNIDIRECTIONAL)
            self._in_bidirectional_sync = False
        
        logger.info(f"Synced {len(synced_items)} items from {source_project} to {target_project}")
        return event
    
    def add_link(
        self,
        from_item_id: str,
        to_item_id: str,
        link_type: str = "related",
        strength: float = 0.5
    ):
        """添加知识链接"""
        link = KnowledgeLink(
            from_item_id=from_item_id,
            to_item_id=to_item_id,
            link_type=link_type,
            strength=strength
        )
        self.knowledge_links.append(link)
        
        # 自动更新相关知识
        self._update_related_knowledge(from_item_id, to_item_id)
    
    def _update_related_knowledge(self, from_id: str, to_id: str):
        """更新相关知识"""
        # 找到源知识项
        for project, store in self.knowledge_store.items():
            item = store.get(from_id)
            if item:
                # 更新元数据
                item.metadata["related_items"] = item.metadata.get("related_items", [])
                if to_id not in item.metadata["related_items"]:
                    item.metadata["related_items"].append(to_id)
                item.updated_at = datetime.now(timezone.utc).isoformat()
    
    def get_knowledge(
        self,
        project: str,
        knowledge_type: KnowledgeType = None
    ) -> List[KnowledgeItem]:
        """获取知识"""
        if project not in self.knowledge_store:
            return []
        
        store = self.knowledge_store[project]
        
        if knowledge_type is None:
            return list(store.values())
        
        return [item for item in store.values() if item.knowledge_type == knowledge_type]
    
    def get_related_knowledge(
        self,
        item_id: str,
        max_distance: int = 2
    ) -> List[KnowledgeItem]:
        """获取相关知识"""
        related = []
        visited = {item_id}
        queue = [(item_id, 0)]
        
        while queue:
            current_id, distance = queue.pop(0)
            
            if distance >= max_distance:
                continue
            
            # 查找链接
            for link in self.knowledge_links:
                next_id = None
                
                if link.from_item_id == current_id:
                    next_id = link.to_item_id
                elif link.to_item_id == current_id:
                    next_id = link.from_item_id
                
                if next_id and next_id not in visited:
                    visited.add(next_id)
                    
                    # 获取知识项
                    for store in self.knowledge_store.values():
                        item = store.get(next_id)
                        if item:
                            related.append(item)
                            queue.append((next_id, distance + 1))
        
        return related
    
    def search_knowledge(
        self,
        query: str,
        projects: List[str] = None,
        knowledge_types: List[KnowledgeType] = None
    ) -> List[KnowledgeItem]:
        """搜索知识"""
        results = []
        
        # 确定搜索范围
        search_projects = projects if projects else list(self.knowledge_store.keys())
        
        for project in search_projects:
            if project not in self.knowledge_store:
                continue
            
            for item in self.knowledge_store[project].values():
                # 过滤类型
                if knowledge_types and item.knowledge_type not in knowledge_types:
                    continue
                
                # 简单搜索（实际应使用向量检索）
                query_lower = query.lower()
                content_str = json.dumps(item.content).lower()
                
                if query_lower in content_str or query_lower in item.metadata.get("tags", []):
                    results.append(item)
        
        return results
    
    def get_sync_history(self, limit: int = 10) -> List[SyncEvent]:
        """获取同步历史"""
        return self.sync_history[-limit:]
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "projects": list(self.knowledge_store.keys()),
            "total_knowledge_items": sum(len(v) for v in self.knowledge_store.values()),
            "total_links": len(self.knowledge_links),
            "total_syncs": len(self.sync_history),
            "sync_rules_count": len(self.sync_rules),
            "knowledge_by_project": {
                project: len(items)
                for project, items in self.knowledge_store.items()
            }
        }


# 全局实例
_knowledge_flow = None

def get_knowledge_flow() -> KnowledgeFlow:
    """获取知识流动实例"""
    global _knowledge_flow
    if _knowledge_flow is None:
        _knowledge_flow = KnowledgeFlow()
    return _knowledge_flow

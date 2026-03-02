"""
记忆管理器 - 统一记忆系统的核心控制器
支持三层记忆架构：原始记忆层、语义记忆层、元认知层
支持向量检索（MemGPT风格）
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .memory_store import MemoryStore
from .vector_store import VectorStore
from .semantic_layer import SemanticLayer
from .meta_cognition import MetaCognition

logger = logging.getLogger(__name__)


class MemoryTier(Enum):
    """记忆层次枚举"""
    CORE = "core"       # 核心记忆，始终在上下文
    RECALL = "recall"   # 检索记忆，可被向量召回
    ARCHIVAL = "archival"  # 归档记忆，压缩存储


class MemoryManager:
    """
    记忆管理器主类
    提供统一的记忆存取接口，支持三层记忆的协同工作
    """

    def __init__(self, base_path: str = None, config: Dict = None):
        if base_path is None:
            from config import MEMORY_DIR
            base_path = MEMORY_DIR
            
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}

        # 初始化各层
        self.store = MemoryStore(self.base_path)
        self.vector_store = VectorStore(
            dimension=self.config.get("dimension", 384)
        )
        self.semantic = SemanticLayer()
        self.meta = MetaCognition()

        # 加载现有记忆
        self._load_memory()
        
        # 初始化向量存储
        self._init_vector_store()

    def _load_memory(self):
        """加载现有记忆数据"""
        self.unified_memory = self.store.load("unified_memory.json")
        if not self.unified_memory:
            self.unified_memory = self._create_empty_memory()
            self.store.save("unified_memory.json", self.unified_memory)

    def _create_empty_memory(self) -> Dict[str, Any]:
        """创建空记忆结构"""
        return {
            "version": "2.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "layers": {
                "raw_memory": {
                    "conversations": [],
                    "task_records": [],
                    "file_operations": []
                },
                "semantic_memory": {
                    "entities": [],
                    "relations": []
                },
                "meta_cognition": {
                    "capabilities": {},
                    "boundaries": {}
                }
            }
        }

    def _init_vector_store(self):
        """初始化向量存储"""
        vector_path = self.base_path / "vectors"
        if vector_path.exists():
            self.vector_store.load(str(vector_path))

    # ==================== 原始记忆层操作 ====================

    def add_conversation(
        self, 
        user: str, 
        content: str, 
        intent: str = "general", 
        outcome: str = "completed",
        quality_score: float = 0.5
    ) -> str:
        """添加对话记录到原始记忆层"""
        conversation = {
            "id": f"conv_{uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "content": content,
            "intent": intent,
            "outcome": outcome,
            "quality_score": quality_score,
            "tier": MemoryTier.RECALL.value
        }
        
        self.unified_memory["layers"]["raw_memory"]["conversations"].append(conversation)
        
        # 添加到向量存储
        try:
            embedding = self._get_embedding(content)
            self.vector_store.add(conversation["id"], embedding, {
                "type": "conversation",
                "content": content,
                "user": user,
                "timestamp": conversation["timestamp"]
            })
        except Exception as e:
            self.logger.warning(f"Failed to vectorize conversation: {e}")
        
        self._update_timestamp()
        self._save_and_sync()
        return conversation["id"]

    def add_task_record(
        self, 
        project: str, 
        description: str, 
        status: str = "pending"
    ) -> str:
        """添加任务记录到原始记忆层"""
        task = {
            "id": f"task_{uuid4().hex[:8]}",
            "project": project,
            "description": description,
            "status": status,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "progress": 0.0,
            "blocking_issues": [],
            "tier": MemoryTier.CORE.value
        }
        
        self.unified_memory["layers"]["raw_memory"]["task_records"].append(task)
        
        # 添加到向量存储
        try:
            embedding = self._get_embedding(f"{project}: {description}")
            self.vector_store.add(task["id"], embedding, {
                "type": "task",
                "content": f"{project}: {description}",
                "project": project,
                "timestamp": task["started_at"]
            })
        except Exception as e:
            self.logger.warning(f"Failed to vectorize task: {e}")
        
        self._update_timestamp()
        self._save_and_sync()
        return task["id"]

    def update_task_progress(
        self, 
        task_id: str, 
        progress: float, 
        blocking_issues: Optional[List[str]] = None
    ):
        """更新任务进度"""
        tasks = self.unified_memory["layers"]["raw_memory"]["task_records"]
        for task in tasks:
            if task["id"] == task_id:
                task["progress"] = progress
                if blocking_issues is not None:
                    task["blocking_issues"] = blocking_issues
                self._update_timestamp()
                self._save_and_sync()
                return True
        return False

    # ==================== 语义记忆层操作 ====================

    def add_entity(
        self,
        entity_type: str,
        name: str,
        aliases: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5
    ) -> str:
        """添加实体到语义记忆层"""
        entity = {
            "id": f"entity_{uuid4().hex[:8]}",
            "type": entity_type,
            "name": name,
            "aliases": aliases or [name],
            "attributes": attributes or {},
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tier": MemoryTier.CORE.value
        }
        
        self.unified_memory["layers"]["semantic_memory"]["entities"].append(entity)
        
        # 自动建立关联
        self.semantic.auto_link(
            entity, 
            self.unified_memory["layers"]["semantic_memory"]
        )
        
        # 添加到向量存储
        try:
            content = f"{name}: {entity_type}"
            if attributes:
                content += f" - {attributes}"
            embedding = self._get_embedding(content)
            self.vector_store.add(entity["id"], embedding, {
                "type": "entity",
                "content": content,
                "name": name,
                "entity_type": entity_type
            })
        except Exception as e:
            self.logger.warning(f"Failed to vectorize entity: {e}")
        
        self._update_timestamp()
        self._save_and_sync()
        return entity["id"]

    def add_relation(
        self,
        from_entity_name: str,
        to_entity_name: str,
        relation_type: str,
        description: str = "",
        strength: float = 0.5
    ):
        """添加实体关系"""
        relation = {
            "from": from_entity_name,
            "to": to_entity_name,
            "type": relation_type,
            "description": description,
            "strength": strength,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.unified_memory["layers"]["semantic_memory"]["relations"].append(relation)
        self._update_timestamp()
        self._save_and_sync()

    def find_entity(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找实体"""
        entities = self.unified_memory["layers"]["semantic_memory"]["entities"]
        for entity in entities:
            if name in entity["aliases"]:
                return entity
        return None

    def find_related_entities(self, entity_name: str) -> List[Dict[str, Any]]:
        """查找相关实体"""
        relations = self.unified_memory["layers"]["semantic_memory"]["relations"]
        related = []
        
        for rel in relations:
            if rel["from"] == entity_name:
                target = self.find_entity(rel["to"])
                if target:
                    related.append({**target, "relation": rel})
            elif rel["to"] == entity_name:
                source = self.find_entity(rel["from"])
                if source:
                    related.append({**source, "relation": rel})
        
        return related

    # ==================== 向量检索 ====================

    def paginate_memory(self, query: str, max_tokens: int = 8000) -> Dict[str, Any]:
        """
        MemGPT风格的分页内存管理
        根据查询自动决定哪些记忆应该进入上下文
        """
        # 1. 获取查询的向量表示
        query_embedding = self._get_embedding(query)
        
        # 2. 从向量存储中检索最相关的记忆
        recall_results = self.vector_store.search(
            query_embedding,
            top_k=self.config.get("top_k", 20),
            threshold=self.config.get("threshold", 0.5)
        )
        
        # 3. 获取核心记忆
        core_memories = self._get_tier_memories(MemoryTier.CORE)
        
        # 4. 融合并裁剪到token限制
        combined = self._combine_and_truncate(
            core_memories,
            recall_results,
            max_tokens
        )
        
        # 5. 更新访问时间戳
        self._update_access_timestamps(recall_results)
        
        return {
            "context_memories": combined,
            "recall_sources": [r["id"] for r in recall_results],
            "total_tokens": self._estimate_tokens(combined)
        }

    def _get_tier_memories(self, tier: MemoryTier) -> List[Dict]:
        """获取指定层次的记忆"""
        memories = []
        
        # 搜索对话
        for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
            if conv.get("tier") == tier.value:
                memories.append(conv)
        
        # 搜索任务
        for task in self.unified_memory["layers"]["raw_memory"]["task_records"]:
            if task.get("tier") == tier.value:
                memories.append(task)
        
        # 搜索实体
        for entity in self.unified_memory["layers"]["semantic_memory"]["entities"]:
            if entity.get("tier") == tier.value:
                memories.append(entity)
        
        return memories

    def _combine_and_truncate(
        self,
        core_memories: List[Dict],
        recall_results: List[Dict],
        max_tokens: int
    ) -> List[Dict]:
        """融合记忆并裁剪到token限制"""
        combined = []
        
        # 先添加核心记忆
        for mem in core_memories:
            combined.append(mem)
        
        # 再添加检索结果（去重）
        core_ids = {m["id"] for m in core_memories}
        for result in recall_results:
            if result["id"] not in core_ids:
                combined.append(result["metadata"])
        
        # 简单token估算（实际应使用tiktoken）
        estimated_tokens = self._estimate_tokens(combined)
        
        # 如果超过限制，裁剪
        while estimated_tokens > max_tokens and len(combined) > 1:
            combined.pop()
            estimated_tokens = self._estimate_tokens(combined)
        
        return combined

    def _estimate_tokens(self, memories: List[Dict]) -> int:
        """简单token估算"""
        total_chars = 0
        for mem in memories:
            content = mem.get("content", "")
            if isinstance(content, dict):
                content = json.dumps(content)
            total_chars += len(content)
        return total_chars // 4  # 粗略估算

    def _update_access_timestamps(self, recall_results: List[Dict]):
        """更新检索结果的访问时间戳"""
        for result in recall_results:
            mem_id = result["id"]
            # 更新原始记忆的访问时间
            for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
                if conv["id"] == mem_id:
                    conv["last_accessed"] = datetime.now(timezone.utc).isoformat()
            for task in self.unified_memory["layers"]["raw_memory"]["task_records"]:
                if task["id"] == mem_id:
                    task["last_accessed"] = datetime.now(timezone.utc).isoformat()

    # ==================== 遗忘曲线 ====================

    def apply_forgetting(self):
        """应用遗忘曲线 - 精细化版本
        使用艾宾浩斯遗忘曲线模型 + 访问频率加成
        """
        memories = self._get_all_memories()
        decay_rate = self.config.get("decay_rate", 0.05)
        threshold = self.config.get("forget_threshold", 0.2)
        
        archived_count = 0
        for memory in memories:
            # 安全获取时间戳
            timestamp_str = memory.get("last_accessed") or memory.get("created_at")
            if not timestamp_str:
                continue
            
            try:
                last_access = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                continue
            
            days_since_access = (datetime.now(timezone.utc) - last_access).days
            
            # 获取访问次数（访问越多，遗忘越慢）
            access_count = memory.get("access_count", 1)
            frequency_boost = min(1.5, 1.0 + (access_count * 0.1))  # 最多1.5倍
            
            # 核心遗忘曲线：指数衰减
            old_confidence = memory.get("confidence", 1.0)
            base_decay = 2.718 ** (-decay_rate * days_since_access)
            new_confidence = max(
                threshold,
                old_confidence * base_decay * frequency_boost
            )
            new_confidence = min(1.0, new_confidence)  # 不超过1.0
            
            # 如果低于阈值，自动归档
            if new_confidence < threshold and memory.get("tier") != MemoryTier.ARCHIVAL.value:
                memory["tier"] = MemoryTier.ARCHIVAL.value
                archived_count += 1
                self.logger.info(f"Memory {memory['id']} auto-archived (confidence: {new_confidence:.3f})")
            
            memory["confidence"] = new_confidence
        
        self._save_and_sync()
        return archived_count

    def boost_memory(self, memory_id: str, boost: float = 0.2):
        """提升记忆置信度（重要记忆需要定期巩固）"""
        for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
            if conv["id"] == memory_id:
                conv["confidence"] = min(1.0, conv.get("confidence", 0.5) + boost)
                conv["access_count"] = conv.get("access_count", 0) + 1
                self._save_and_sync()
                return True
        
        for task in self.unified_memory["layers"]["raw_memory"]["task_records"]:
            if task["id"] == memory_id:
                task["confidence"] = min(1.0, task.get("confidence", 0.5) + boost)
                task["access_count"] = task.get("access_count", 0) + 1
                self._save_and_sync()
                return True
        
        return False

    def _get_all_memories(self) -> List[Dict]:
        """获取所有记忆"""
        memories = []
        memories.extend(self.unified_memory["layers"]["raw_memory"]["conversations"])
        memories.extend(self.unified_memory["layers"]["raw_memory"]["task_records"])
        memories.extend(self.unified_memory["layers"]["semantic_memory"]["entities"])
        return memories

    def _move_to_tier(self, memory_id: str, target_tier: MemoryTier):
        """将记忆移动到指定层次"""
        # 搜索对话
        for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
            if conv["id"] == memory_id:
                conv["tier"] = target_tier.value
                self.logger.info(f"Moved conversation {memory_id} to {target_tier.value}")
                self._save_and_sync()
                return True
        
        # 搜索任务
        for task in self.unified_memory["layers"]["raw_memory"]["task_records"]:
            if task["id"] == memory_id:
                task["tier"] = target_tier.value
                self.logger.info(f"Moved task {memory_id} to {target_tier.value}")
                self._save_and_sync()
                return True
        
        # 搜索实体
        for entity in self.unified_memory["layers"]["semantic_memory"]["entities"]:
            if entity["id"] == memory_id:
                entity["tier"] = target_tier.value
                self.logger.info(f"Moved entity {memory_id} to {target_tier.value}")
                self._save_and_sync()
                return True
        
        return False

    def compress_memory(self, memory_id: str) -> bool:
        """压缩记忆内容（归档前处理）"""
        # 查找记忆
        for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
            if conv["id"] == memory_id:
                # 保留关键信息，压缩内容
                original = conv.get("content", "")
                conv["compressed"] = True
                conv["original_length"] = len(original)
                self.logger.info(f"Compressed conversation {memory_id}")
                self._save_and_sync()
                return True
        
        return False

    # ==================== 元认知层操作 ====================

    def update_capability(self, capability: str, level: int, confidence: float):
        """更新能力评估"""
        if "capabilities" not in self.unified_memory["layers"]["meta_cognition"]:
            self.unified_memory["layers"]["meta_cognition"]["capabilities"] = {}
        
        self.unified_memory["layers"]["meta_cognition"]["capabilities"][capability] = {
            "level": level,
            "confidence": confidence,
            "last_used": datetime.now(timezone.utc).isoformat()
        }
        
        # 触发元认知更新
        self.meta.evaluate_capability(
            capability,
            level,
            confidence,
            self.unified_memory["layers"]["meta_cognition"]
        )
        
        self._update_timestamp()
        self._save_and_sync()

    def get_capabilities(self) -> Dict[str, Any]:
        """获取所有能力评估"""
        return self.unified_memory["layers"]["meta_cognition"].get("capabilities", {})

    def get_boundaries(self) -> Dict[str, Any]:
        """获取能力边界"""
        return self.unified_memory["layers"]["meta_cognition"].get(
            "boundaries",
            {
                "known_limitations": [],
                "uncertainty_threshold": 0.3
            }
        )

    # ==================== 公共方法 ====================

    def _get_embedding(self, text: str) -> Any:
        """获取文本的向量表示"""
        try:
            from src.utils.embedding import get_embedding
            return get_embedding(text)
        except ImportError:
            # 如果嵌入模块不存在，返回随机向量
            import numpy as np
            dim = self.config.get("dimension", 384)
            return np.random.randn(dim).astype(np.float32)

    def _update_timestamp(self):
        """更新最后更新时间"""
        self.unified_memory["last_updated"] = datetime.now(timezone.utc).isoformat()

    def _save_and_sync(self):
        """保存并同步到存储"""
        self.store.save("unified_memory.json", self.unified_memory)
        
        # 保存向量索引
        vector_path = self.base_path / "vectors"
        vector_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save(str(vector_path))

    def get_full_memory(self) -> Dict[str, Any]:
        """获取完整记忆"""
        return self.unified_memory

    def search_memory(self, keyword: str) -> Dict[str, Any]:
        """搜索记忆（关键词模式）"""
        results = {
            "conversations": [],
            "entities": [],
            "tasks": []
        }
        
        # 搜索对话
        for conv in self.unified_memory["layers"]["raw_memory"]["conversations"]:
            if keyword.lower() in conv.get("content", "").lower():
                results["conversations"].append(conv)
        
        # 搜索实体
        for entity in self.unified_memory["layers"]["semantic_memory"]["entities"]:
            if keyword.lower() in entity.get("name", "").lower():
                results["entities"].append(entity)
            for alias in entity.get("aliases", []):
                if keyword.lower() in alias.lower():
                    results["entities"].append(entity)
                    break
        
        # 搜索任务
        for task in self.unified_memory["layers"]["raw_memory"]["task_records"]:
            if keyword.lower() in task.get("description", "").lower():
                results["tasks"].append(task)
        
        return results

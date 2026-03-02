"""
异步工作流引擎 - Week 6
支持异步节点、Redis缓存、状态持久化
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncNode:
    """异步节点"""
    name: str
    handler: Callable
    timeout: int = 30  # 秒
    retry: int = 3
    checkpoint: bool = True  # 是否保存检查点
    human_in_loop: bool = False  # 是否需要人工确认
    
    async def execute(self, state: Dict) -> Dict:
        """执行节点"""
        for attempt in range(self.retry):
            try:
                if asyncio.iscoroutinefunction(self.handler):
                    result = await asyncio.wait_for(
                        self.handler(state),
                        timeout=self.timeout
                    )
                else:
                    result = self.handler(state)
                return {**state, "status": NodeStatus.COMPLETED.value, "result": result}
            except asyncio.TimeoutError:
                logger.warning(f"Node {self.name} timeout (attempt {attempt + 1})")
                if attempt == self.retry - 1:
                    return {**state, "status": NodeStatus.FAILED.value, "error": "Timeout"}
            except Exception as e:
                logger.error(f"Node {self.name} failed: {e}")
                if attempt == self.retry - 1:
                    return {**state, "status": NodeStatus.FAILED.value, "error": str(e)}
        return {**state, "status": NodeStatus.FAILED.value}


class AsyncWorkflow:
    """
    异步工作流引擎
    
    特性：
    - 异步节点执行
    - 检查点持久化
    - Redis缓存集成
    - Human-in-Loop支持
    - 断点续传
    """
    
    def __init__(self, name: str = "workflow"):
        self.name = name
        self.nodes: Dict[str, AsyncNode] = {}
        self.edges: List[tuple] = []
        self.entry_point: Optional[str] = None
        self.redis_client = None
        self.current_state: Optional[Dict] = None
        self.checkpoints: List[Dict] = []
    
    def add_node(
        self,
        name: str,
        handler: Callable,
        timeout: int = 30,
        retry: int = 3,
        checkpoint: bool = True,
        human_in_loop: bool = False
    ):
        """添加异步节点"""
        self.nodes[name] = AsyncNode(
            name=name,
            handler=handler,
            timeout=timeout,
            retry=retry,
            checkpoint=checkpoint,
            human_in_loop=human_in_loop
        )
        logger.info(f"Added async node: {name}")
    
    def add_edge(self, from_node: str, to_node: str):
        """添加边"""
        self.edges.append((from_node, to_node))
    
    def set_entry_point(self, node: str):
        """设置入口点"""
        self.entry_point = node
    
    def set_redis(self, redis_client):
        """设置Redis客户端"""
        self.redis_client = redis_client
    
    async def _execute_node(self, node_name: str, state: Dict) -> Dict:
        """执行单个节点"""
        if node_name not in self.nodes:
            raise ValueError(f"Node {node_name} not found")
        
        node = self.nodes[node_name]
        
        # Human-in-Loop检查
        if node.human_in_loop:
            state["human_approval_required"] = True
            state["human_node"] = node_name
            logger.info(f"Human-in-Loop: waiting approval for {node_name}")
            # 在实际实现中，这里会暂停等待人工确认
            # state = await self.wait_for_humanApproval(node_name, state)
        
        # 执行节点
        logger.info(f"Executing node: {node_name}")
        state = await node.execute({**state, "current_node": node_name})
        
        # 检查点保存
        if node.checkpoint:
            self._save_checkpoint(state)
            
            # Redis持久化
            if self.redis_client:
                await self._save_to_redis(state)
        
        return state
    
    async def run(self, initial_state: Dict) -> Dict:
        """执行工作流"""
        if not self.entry_point:
            raise ValueError("No entry point set")
        
        self.current_state = {**initial_state, "status": NodeStatus.RUNNING.value}
        
        # 拓扑排序确定执行顺序
        execution_order = self._topological_sort()
        
        # 依次执行
        for node_name in execution_order:
            if self.current_state.get("status") == NodeStatus.FAILED.value:
                break
            
            self.current_state = await self._execute_node(node_name, self.current_state)
        
        # 完成
        if self.current_state.get("status") != NodeStatus.FAILED.value:
            self.current_state["status"] = NodeStatus.COMPLETED.value
            self.current_state["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        return self.current_state
    
    def _topological_sort(self) -> List[str]:
        """拓扑排序"""
        # 简化版：按边的顺序执行
        order = [self.entry_point]
        visited = {self.entry_point}
        
        while True:
            found = False
            for from_node, to_node in self.edges:
                if from_node in visited and to_node not in visited:
                    order.append(to_node)
                    visited.add(to_node)
                    found = True
            
            if not found:
                break
        
        return order
    
    def _save_checkpoint(self, state: Dict):
        """保存检查点到内存"""
        checkpoint = {
            "state": state.copy(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.checkpoints.append(checkpoint)
        
        # 最多保留20个
        if len(self.checkpoints) > 20:
            self.checkpoints = self.checkpoints[-20:]
        
        logger.debug(f"Checkpoint saved: {len(self.checkpoints)} total")
    
    async def _save_to_redis(self, state: Dict):
        """保存到Redis"""
        if not self.redis_client:
            return
        
        try:
            workflow_id = state.get("workflow_id", "default")
            key = f"workflow:{workflow_id}:checkpoint"
            
            # 序列化状态
            state_json = json.dumps(state, default=str)
            
            # 保存到Redis
            await self.redis_client.set(
                key,
                state_json,
                ex=3600  # 1小时过期
            )
            
            logger.debug(f"Saved to Redis: {key}")
        except Exception as e:
            logger.warning(f"Redis save failed: {e}")
    
    async def restore_from_redis(self, workflow_id: str) -> Optional[Dict]:
        """从Redis恢复"""
        if not self.redis_client:
            return None
        
        try:
            key = f"workflow:{workflow_id}:checkpoint"
            state_json = await self.redis_client.get(key)
            
            if state_json:
                state = json.loads(state_json)
                logger.info(f"Restored from Redis: {workflow_id}")
                return state
        except Exception as e:
            logger.warning(f"Redis restore failed: {e}")
        
        return None
    
    def save_checkpoint(self) -> Optional[Dict]:
        """获取最新检查点"""
        if self.checkpoints:
            return self.checkpoints[-1]
        return None
    
    def restore_checkpoint(self, checkpoint: Dict):
        """恢复检查点"""
        self.current_state = checkpoint.get("state")
        logger.info("Checkpoint restored")
    
    def get_status(self) -> Dict:
        """获取工作流状态"""
        return {
            "name": self.name,
            "nodes": list(self.nodes.keys()),
            "current_state": self.current_state,
            "checkpoints_count": len(self.checkpoints),
            "status": self.current_state.get("status", "unknown") if self.current_state else "not_started"
        }


# ============== Redis缓存层 ==============

class RedisCache:
    """Redis缓存层"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, password: str = ""):
        self.host = host
        self.port = port
        self.password = password
        self.client = None
        self.connected = False
    
    async def connect(self):
        """连接Redis"""
        try:
            import redis.asyncio as redis
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
                decode_responses=True
            )
            await self.client.ping()
            self.connected = True
            logger.info("Redis connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.connected = False
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        if not self.connected:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            return None
    
    async def set(self, key: str, value: str, ex: int = 3600):
        """设置值"""
        if not self.connected:
            return False
        try:
            await self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False
    
    async def delete(self, key: str):
        """删除键"""
        if not self.connected:
            return
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")
    
    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.close()


# ============== 全局实例 ==============

_async_workflow = None

def get_async_workflow(name: str = "default") -> AsyncWorkflow:
    """获取异步工作流实例"""
    global _async_workflow
    if _async_workflow is None:
        _async_workflow = AsyncWorkflow(name)
    return _async_workflow

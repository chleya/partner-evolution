"""
A2A Bus - 内部Agent通信总线
基于Redis pub/sub的分布式消息通道
"""
import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型"""
    PROPOSE = "propose"          # 提出建议
    CHALLENGE = "challenge"      # 挑战/反对
    REQUEST_DATA = "request_data" # 请求数据
    VOTE = "vote"                # 投票
    SHARE_BELIEF = "share_belief" # 分享信念
    START_SELF_REFLECTION = "start_self_reflection" # 启动自省
    RESPONSE = "response"        # 响应


@dataclass
class A2AMessage:
    """A2A消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = "all"  # all表示广播
    type: str = MessageType.PROPOSE.value
    payload: Dict = field(default_factory=dict)
    task_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.type,
            "payload": self.payload,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "A2AMessage":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            from_agent=data.get("from", ""),
            to_agent=data.get("to", "all"),
            type=data.get("type", MessageType.PROPOSE.value),
            payload=data.get("payload", {}),
            task_id=data.get("task_id", ""),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat())
        )


class A2AAgent:
    """A2A Agent 注册"""
    def __init__(self, name: str, bus: "A2ABus"):
        self.name = name
        self.bus = bus
        self.handlers: Dict[str, Callable] = {}
    
    def on(self, message_type: str, handler: Callable[[A2AMessage], None]):
        """注册消息处理器"""
        self.handlers[message_type] = handler
    
    def send(self, to: str, msg_type: str, payload: Dict, task_id: str = "") -> A2AMessage:
        """发送消息"""
        msg = A2AMessage(
            from_agent=self.name,
            to_agent=to,
            type=msg_type,
            payload=payload,
            task_id=task_id
        )
        self.bus._publish(msg)
        return msg
    
    def broadcast(self, msg_type: str, payload: Dict, task_id: str = "") -> A2AMessage:
        """广播消息"""
        return self.send("all", msg_type, payload, task_id)


class A2ABus:
    """
    A2A通信总线
    
    用法:
    bus = A2ABus()
    
    # 注册Agent
    evo = bus.register_agent("Evo-Swarm")
    
    # 监听消息
    evo.on("propose", lambda msg: print(f"收到提议: {msg.payload}"))
    
    # 发送消息
    evo.send("NeuralSite", "request_data", {"query": "进度"})
    """

    def __init__(self, redis_url: str = None, use_redis: bool = True):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.use_redis = use_redis and redis_url is not None
        
        self._redis = None
        self._pubsub = None
        self._agents: Dict[str, A2AAgent] = {}
        self._callbacks: Dict[str, Set[Callable]] = {}
        self._running = False
        self._thread = None
        
        # 如果有Redis则连接
        if self.use_redis:
            try:
                import redis
                self._redis = redis.from_url(redis_url)
                self._redis.ping()
                self.logger.info(f"A2A Bus connected to Redis: {redis_url}")
            except Exception as e:
                self.logger.warning(f"Redis unavailable: {e}, using in-memory mode")
                self.use_redis = False
        
        # 即使没有Redis也使用内存模式
        if not self.use_redis:
            self._memory_messages = []
            self.logger.info("A2A Bus running in memory mode")

    def register_agent(self, name: str) -> A2AAgent:
        """注册Agent"""
        if name in self._agents:
            return self._agents[name]
        
        agent = A2AAgent(name, self)
        self._agents[name] = agent
        self.logger.info(f"Agent registered: {name}")
        return agent

    def subscribe(self, channel: str, callback: Callable[[A2AMessage], None]):
        """订阅频道"""
        if channel not in self._callbacks:
            self._callbacks[channel] = set()
        self._callbacks[channel].add(callback)
        
        # 启动监听线程
        if not self._running:
            self._start_listening()

    def _start_listening(self):
        """启动监听"""
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        self.logger.info("A2A Bus listener started")

    def _listen_loop(self):
        """监听循环"""
        while self._running:
            if self.use_redis and self._redis:
                try:
                    self._redis_pubsub_listen()
                except Exception as e:
                    self.logger.error(f"Redis listen error: {e}")
            else:
                self._memory_listen()
            
            import time
            time.sleep(0.1)

    def _redis_pubsub_listen(self):
        """Redis监听"""
        if not self._pubsub:
            self._pubsub = self._redis.pubsub()
            for channel in self._callbacks.keys():
                self._pubsub.subscribe(channel)
        
        for msg in self._pubsub.listen():
            if msg.get("type") == "message":
                try:
                    data = json.loads(msg["data"])
                    a2a_msg = A2AMessage.from_dict(data)
                    self._deliver_message(a2a_msg)
                except Exception as e:
                    self.logger.error(f"Parse error: {e}")

    def _memory_listen(self):
        """内存模式监听"""
        # 简单实现：检查新消息
        pass

    def _deliver_message(self, msg: A2AMessage):
        """投递消息"""
        # 发送到指定频道
        channel = msg.to_agent if msg.to_agent != "all" else "all"
        
        if channel in self._callbacks:
            for callback in self._callbacks[channel]:
                try:
                    callback(msg)
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")
        
        # 也发送到"all"频道
        if channel != "all" and "all" in self._callbacks:
            for callback in self._callbacks["all"]:
                try:
                    callback(msg)
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")

    def _publish(self, msg: A2AMessage):
        """发布消息"""
        data = msg.to_dict()
        
        if self.use_redis and self._redis:
            channel = msg.to_agent if msg.to_agent != "all" else "all"
            self._redis.publish(channel, json.dumps(data))
        else:
            # 内存模式
            self._memory_messages.append(msg)
            self._deliver_message(msg)
        
        self.logger.debug(f"A2A message: {msg.from_agent} -> {msg.to_agent} [{msg.type}]")

    def get_registered_agents(self) -> list:
        """获取已注册的Agent列表"""
        return list(self._agents.keys())

    def stop(self):
        """停止总线"""
        self._running = False
        if self._pubsub:
            self._pubsub.close()
        self.logger.info("A2A Bus stopped")


# 全局实例
_a2a_bus: Optional[A2ABus] = None


def get_a2a_bus(redis_url: str = None) -> A2ABus:
    """获取A2A总线实例"""
    global _a2a_bus
    if _a2a_bus is None:
        _a2a_bus = A2ABus(redis_url=redis_url)
    return _a2a_bus


# 便捷函数
def register_agent(name: str) -> A2AAgent:
    """注册Agent"""
    return get_a2a_bus().register_agent(name)


def broadcast(from_agent: str, msg_type: str, payload: Dict, task_id: str = "") -> A2AMessage:
    """广播消息"""
    bus = get_a2a_bus()
    agent = bus.register_agent(from_agent)
    return agent.broadcast(msg_type, payload, task_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试
    bus = get_a2a_bus()
    
    # 注册Agent
    evo = bus.register_agent("Evo-Swarm")
    neural = bus.register_agent("NeuralSite")
    
    # 订阅
    def on_propose(msg: A2AMessage):
        print(f"\n[收到] {msg.from_agent} -> {msg.to_agent}: {msg.type}")
        print(f"   Payload: {msg.payload}")
    
    bus.subscribe("all", on_propose)
    
    # 发送测试消息
    print("Sending broadcast...")
    evo.broadcast("share_belief", {
        "belief": "三层记忆架构是核心优势",
        "confidence": 0.78
    }, "test-task-1")
    
    import time
    time.sleep(1)
    
    print("\nRegistered agents:", bus.get_registered_agents())

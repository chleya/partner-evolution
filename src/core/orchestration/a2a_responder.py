"""
A2A Agent响应者 - 让Agent响应集体自省广播
"""
import logging
from src.core.orchestration.a2a_bus import get_a2a_bus, A2AMessage
from src.core.storage import get_storage_manager

logger = logging.getLogger(__name__)


class A2AAgentResponder:
    """A2A Agent响应器"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.bus = get_a2a_bus()
        self.storage = get_storage_manager()
        
        # 注册Agent
        self.bus.register_agent(agent_name)
        
        # 订阅消息
        self.bus.subscribe("all", self._handle_message)
        
        logger.info(f"Agent {agent_name} initialized with A2A responder")
    
    def _handle_message(self, msg: A2AMessage):
        """处理收到的消息"""
        if msg.type == "start_self_reflection":
            self._respond_to_self_reflection(msg)
        elif msg.type == "challenge":
            self._respond_to_challenge(msg)
    
    def _respond_to_self_reflection(self, msg: A2AMessage):
        """响应自省广播"""
        # 根据Agent角色返回不同的belief
        belief = self._generate_response_belief()
        
        if belief:
            from src.core.orchestration.a2a_bus import A2AMessage
            response = A2AMessage(
                from_agent=self.agent_name,
                to_agent="all",
                type="share_belief",
                payload=belief,
                task_id=msg.task_id
            )
            self.bus._publish(response)
            logger.info(f"{self.agent_name} responded with belief: {belief.get('content', '')[:30]}...")
    
    def _generate_response_belief(self) -> dict:
        """生成响应belief - 每个Agent用自己的视角"""
        beliefs = self.storage.get_beliefs()
        
        if not beliefs:
            return None
        
        # 根据Agent选择不同的belief
        if self.agent_name == "Evo-Swarm":
            # Planner: 选择规划/学习相关
            for b in beliefs:
                if any(kw in b.get("content", "") for kw in ["优化", "学习", "改进", "持续"]):
                    return {"content": b.get("content"), "confidence": b.get("confidence")}
        
        elif self.agent_name == "NeuralSite":
            # Executor: 选择执行/效率相关
            for b in beliefs:
                if any(kw in b.get("content", "") for kw in ["效率", "性能", "代码", "架构"]):
                    return {"content": b.get("content"), "confidence": b.get("confidence")}
        
        elif self.agent_name == "VisualCoT":
            # Perceiver: 选择感知/观察相关
            for b in beliefs:
                if any(kw in b.get("content", "") for kw in ["记忆", "数据", "信息"]):
                    return {"content": b.get("content"), "confidence": b.get("confidence")}
        
        # 默认返回第一个
        if beliefs:
            b = beliefs[0]
            return {"content": b.get("content"), "confidence": b.get("confidence")}
        
        return None
    
    def _respond_to_challenge(self, msg: A2AMessage):
        """响应挑战"""
        # 简单处理：表示收到
        logger.info(f"{self.agent_name} received challenge: {msg.payload}")


# 初始化所有Agent响应者
def init_agent_responders():
    """初始化所有Agent响应者"""
    agents = ["Evo-Swarm", "NeuralSite", "VisualCoT"]
    
    for agent_name in agents:
        try:
            A2AAgentResponder(agent_name)
        except Exception as e:
            logger.warning(f"Failed to init {agent_name}: {e}")
    
    logger.info(f"Initialized {len(agents)} A2A agent responders")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_agent_responders()
    print("A2A Agent Responders initialized")

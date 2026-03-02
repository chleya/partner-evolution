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
        """生成响应belief - 每个Agent用自己的专属视角"""
        beliefs = self.storage.get_beliefs()
        
        if not beliefs:
            return None
        
        # 严格的专属关键词过滤
        agent_keywords = {
            "Evo-Swarm": ["学习", "进化", "持续", "成长", "自适应", "迭代"],
            "NeuralSite": ["代码", "性能", "效率", "架构", "检索", "缓存", "可读性", "工程"],
            "VisualCoT": ["感知", "观察", "视觉", "数据", "输入", "人格", "上下文", "多模态"]
        }
        
        my_keywords = agent_keywords.get(self.agent_name, [])
        
        # 找最匹配的信念
        candidates = []
        for b in beliefs:
            content = b.get("content", "")
            confidence = b.get("confidence", 0)
            
            # 至少包含一个专属关键词
            if any(kw in content for kw in my_keywords):
                # 评分：关键词命中数 * 0.3 + confidence * 0.7
                hit_count = sum(1 for kw in my_keywords if kw in content)
                score = hit_count * 0.3 + confidence * 0.7
                candidates.append((score, b))
        
        if candidates:
            # 选最高分的
            candidates.sort(key=lambda x: x[0], reverse=True)
            selected = candidates[0][1]
            return {"content": selected.get("content"), "confidence": selected.get("confidence")}
        
        # 无匹配时fallback到最低confidence的（让它有成长空间）
        low_conf = [b for b in beliefs if b.get("confidence", 0) < 0.80]
        if low_conf:
            return {"content": low_conf[0].get("content"), "confidence": low_conf[0].get("confidence")}
        
        # 兜底
        if beliefs:
            b = beliefs[-1]
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

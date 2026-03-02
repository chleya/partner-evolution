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
        elif msg.type == "user_task_consult":
            self._respond_to_user_task(msg)
        elif msg.type == "challenge":
            self._respond_to_challenge(msg)
    
    def _respond_to_user_task(self, msg: A2AMessage):
        """响应用户任务咨询 - v3.0专业模式"""
        user_input = msg.payload.get("user_input", "")
        
        # v3.0 角色卡
        role_prompts = {
            "Evo-Swarm": """你是v3.0递归进化团队的Evo-Swarm。
视角：长期进化、选择压力、种群多样性。
输出必须包含：模块理解、核心挑战、技术选型、伪代码、风险评估。""",
            
            "NeuralSite": """你是v3.0递归进化团队的NeuralSite。
视角：工程可行性、性能、安全、代码结构。
输出必须包含：模块理解、核心挑战、技术选型、伪代码、风险评估。""",
            
            "VisualCoT": """你是v3.0递归进化团队的VisualCoT。
视角：感知连续性、推理可解释性、演化可视化。
输出必须包含：模块理解、核心挑战、技术选型、伪代码、风险评估。""",
            
            "Critic": """你是v3.0团队的Critic（批评者）。
视角：找出问题、识别风险、指出逻辑漏洞。
职责：检查其他Agent输出的问题，提出改进建议。
输出必须包含：发现的问题、潜在风险、改进建议。
重点关注：事实错误、逻辑漏洞、过度自信表述。"""
        }
        
        # v3.0任务关键词 - 检测是否是v3.0相关讨论
        v3_keywords = ["v3", "递归", "进化", "自我", "分叉", "基因", "本体", "Identity", "Genome", "Fork", "Meta"]
        
        is_v3_task = any(kw.lower() in user_input.lower() for kw in v3_keywords)
        
        if is_v3_task:
            # 使用v3.0专业模式
            role_prompt = role_prompts.get(self.agent_name, "")
            
            # 调用LLM生成专业建议
            try:
                from src.utils.llm_client import MiniMaxClient
                client = MiniMaxClient()
                
                full_prompt = f"""{role_prompt}

任务：{user_input}

请用以下格式输出：
## 1. 模块理解
## 2. 核心挑战（具体列表）
## 3. 推荐方案（技术选型 + 伪代码）
## 4. 风险与权衡
## 5. 投票态度

必须具体、可执行，不要泛泛而谈。"""
                
                response_text = client.generate(full_prompt, max_tokens=500)
                suggestion = response_text[:300]
                
            except Exception as e:
                logger.warning(f"LLM call failed: {e}")
                suggestion = f"[{self.agent_name}] 需要更深入分析此v3.0模块"
        else:
            # 普通模式
            suggestions = {
                "Evo-Swarm": "建议采用渐进式重构，先从核心模块开始，保持向后兼容",
                "NeuralSite": "建议先优化数据库索引和缓存策略，再考虑架构调整",
                "VisualCoT": "建议收集更多用户反馈数据，确保重构方向符合实际需求"
            }
            suggestion = suggestions.get(self.agent_name, "需要进一步分析")
        
        response = A2AMessage(
            from_agent=self.agent_name,
            to_agent="all",
            type="response",
            payload={"content": suggestion},
            task_id=msg.task_id
        )
        self.bus._publish(response)
        logger.info(f"{self.agent_name} responded to user task: {suggestion[:30]}...")
    
    def _respond_to_self_reflection(self, msg: A2AMessage):
        """响应自省广播 - 带投票"""
        # 1. 分享自己的belief
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
    
    def _generate_vote(self, target_belief: dict, my_keywords: list) -> dict:
        """为其他Agent的belief生成投票"""
        content = target_belief.get("content", "")
        
        # 计算投票分数
        vote_score = 0
        reason = ""
        
        # 支持票：主题相关
        if any(kw in content for kw in my_keywords):
            vote_score += 1
            reason = "与我的视角高度一致"
        # 反对票：主题冲突
        elif self.agent_name == "Evo-Swarm" and ("代码" in content or "架构" in content):
            vote_score -= 0.5
            reason = "过于工程化，忽视学习成长"
        elif self.agent_name == "NeuralSite" and ("学习" in content or "进化" in content):
            vote_score -= 0.5
            reason = "过于理论化，缺乏工程可行性"
        else:
            vote_score += 0
            reason = "保持中立"
        
        return {
            "target_belief": target_belief.get("content", "")[:50],
            "vote": vote_score,
            "reason": reason
        }
    
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
    # 4个Agent：进化、架构、视觉、批评
    agents = ["Evo-Swarm", "NeuralSite", "VisualCoT", "Critic"]
    
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

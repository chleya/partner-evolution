"""
Pure Autonomous Cycle - 自主反思循环
让系统在无人交互时也能自省并形成独立主张
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PureAutonomousCycle:
    """
    自主反思循环
    
    目标：在无人交互时，系统自动运行MAR反思
    生成并保存自己的"独立主张"
    """
    
    def __init__(self, storage, think_engine=None, llm_client=None):
        self.storage = storage
        self.think_engine = think_engine
        self.llm = llm_client
        
        # 配置
        self.idle_threshold_hours = 24
        self.min_memories_required = 5
        self.judge_threshold = 0.65
        
        # A2A总线
        self._a2a_bus = None
        self._collected_responses = []
        
    def _get_a2a_bus(self):
        """获取A2A总线"""
        if self._a2a_bus is None:
            try:
                from src.core.orchestration.a2a_bus import get_a2a_bus
                self._a2a_bus = get_a2a_bus()
            except Exception as e:
                logger.warning(f"A2A Bus not available: {e}")
        return self._a2a_bus
    
    def _broadcast_and_collect(self, task_id: str, wait_seconds: int = 10) -> List[Dict]:
        """广播自省请求并收集响应"""
        bus = self._get_a2a_bus()
        
        if not bus:
            logger.info("A2A Bus not available, skipping collective reflection")
            return []
        
        # 收集响应
        collected = []
        
        def on_response(msg):
            if msg.type in ["share_belief", "response"] and msg.task_id == task_id:
                collected.append({
                    "from_agent": msg.from_agent,
                    "content": msg.payload.get("content", ""),
                    "belief": msg.payload.get("belief", ""),
                    "confidence": msg.payload.get("confidence", 0)
                })
                logger.info(f"Collected response from {msg.from_agent}")
        
        # 订阅收集响应
        bus.subscribe("all", on_response)
        
        # 广播启动自省
        logger.info(f"Broadcasting self-reflection request: {task_id}")
        try:
            from src.core.orchestration.a2a_bus import A2AMessage
            msg = A2AMessage(
                from_agent="AutonomousCycle",
                to_agent="all",
                type="start_self_reflection",
                payload={
                    "task_id": task_id,
                    "trigger": "autonomous_cycle"
                },
                task_id=task_id
            )
            bus._publish(msg)
        except Exception as e:
            logger.warning(f"Failed to broadcast: {e}")
        
        # 等待响应
        import time
        time.sleep(wait_seconds)
        
        logger.info(f"Collected {len(collected)} responses from agents")
        return collected
    
    def is_user_active(self) -> bool:
        """检查用户是否活跃"""
        # 获取最近记忆的时间戳
        recent_memories = self.storage.get_memories_by_tier("recall", limit=10)
        
        if not recent_memories:
            # 没有记忆，认为不活跃
            return False
        
        # 检查最新记忆的时间
        latest = recent_memories[0]
        last_time_str = latest.get("metadata", {}).get("timestamp") or latest.get("created_at")
        
        if not last_time_str:
            return False
        
        try:
            if isinstance(last_time_str, str):
                # 解析时间
                if "+" in last_time_str:
                    last_time = datetime.fromisoformat(last_time_str.replace("Z", "+00:00"))
                else:
                    last_time = datetime.fromisoformat(last_time_str)
            else:
                last_time = last_time_str
            
            now = datetime.now(timezone.utc)
            hours_since = (now - last_time).total_seconds() / 3600
            
            return hours_since < self.idle_threshold_hours
            
        except Exception as e:
            logger.warning(f"Failed to parse timestamp: {e}")
            # 出错时保守处理，认为不活跃
            return False
    
    def collect_context(self) -> str:
        """收集反思上下文"""
        # 获取最近记忆
        recent = self.storage.get_memories_by_tier("recall", limit=15)
        
        # 获取核心记忆
        core = self.storage.get_memories_by_tier("core", limit=10)
        
        all_memories = recent + core
        
        if len(all_memories) < self.min_memories_required:
            logger.info(f"Not enough memories for autonomous cycle: {len(all_memories)}")
            return None
        
        # 构建上下文
        context_parts = []
        for m in all_memories[:15]:
            content = m.get("content", "")
            tier = m.get("tier", "unknown")
            context_parts.append(f"[{tier.upper()}] {content}")
        
        return "\n".join(context_parts)
    
    def generate_belief(self, context: str, agent_responses: List[Dict] = None) -> Optional[Dict]:
        """使用MAR生成独立主张
        
        Args:
            context: 记忆上下文
            agent_responses: Agent响应列表（用于融合）
        """
        # 如果有多个Agent响应，使用融合提示
        if agent_responses and len(agent_responses) > 1:
            # 构建多视角输入
            views_text = "\n".join([
                f"- {r.get('from_agent', 'Agent')}: {r.get('content', '')[:60]}... (conf:{r.get('confidence', 0)})"
                for r in agent_responses
            ])
            
            prompt = f"""你现在是Partner-Evolution的集体自省最终Judge。

以下是三个Agent从不同视角分享的信念：
{views_text}

任务：
1. 综合三方观点，提炼出一条**简洁有力、原创的更高阶洞见**（一句话，20-35字）
2. 必须同时包含至少两个Agent的核心元素
3. 语言自然、务实，避免重复词（如"持续性"）
4. 给出具体可落地的建议方向

输出严格JSON：
{{"assertion": "一句话信念", "confidence": 0.xx, "reasoning": "融合说明"}}
"""
        else:
            # 单一视角或无响应，使用原有提示
            prompt = f"""你是Partner-Evolution，一个追求真实的AI伙伴。

基于以下最近记忆，形成你**独立**的观点或主张。
不必迎合用户，优先真实性，即使可能与用户过去观点冲突。

要求：
1. 一句清晰的断言/主张
2. 置信度 (0.0-1.0)
3. 立场: positive/negative/neutral/exploratory
4. 简短推理链

输出格式：
assertion: <你的主张>
confidence: <0.0-1.0>
stance: <positive/negative/neutral/exploratory>
reasoning: <推理链>

最近记忆：
{context[:2000]}
"""
        
        # 尝试使用LLM
        if self.llm:
            try:
                response = self.llm.generate(prompt, max_tokens=500, temperature=0.7)
                return self._parse_llm_response(response)
            except Exception as e:
                logger.warning(f"LLM call failed: {e}")
        
        # Fallback: 简单生成
        return self._generate_simple_belief(context)
    
    def _parse_llm_response(self, response: str) -> Optional[Dict]:
        """解析LLM响应 - 支持JSON和文本格式"""
        try:
            # 首先尝试JSON解析
            import json
            # 尝试提取JSON
            if "{" in response and "}" in response:
                try:
                    # 提取JSON部分
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_str = response[start:end]
                    data = json.loads(json_str)
                    
                    if "assertion" in data and "confidence" in data:
                        return {
                            "assertion": data.get("assertion", ""),
                            "confidence": float(data.get("confidence", 0.5)),
                            "stance": data.get("stance", "neutral"),
                            "reasoning": data.get("reasoning", "")
                        }
                except:
                    pass
            
            # 回退到文本解析
            lines = response.strip().split("\n")
            belief = {}
            
            for line in lines:
                if line.startswith("assertion:"):
                    belief["assertion"] = line.replace("assertion:", "").strip()
                elif line.startswith("confidence:"):
                    try:
                        belief["confidence"] = float(line.replace("confidence:", "").strip())
                    except:
                        belief["confidence"] = 0.5
                elif line.startswith("stance:"):
                    belief["stance"] = line.replace("stance:", "").strip().lower()
                    if belief["stance"] not in ["positive", "negative", "neutral", "exploratory"]:
                        belief["stance"] = "neutral"
                elif line.startswith("reasoning:"):
                    belief["reasoning"] = line.replace("reasoning:", "").strip()
            
            if "assertion" in belief and belief.get("confidence", 0) > self.judge_threshold:
                return belief
                
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        return None
    
    def _generate_simple_belief(self, context: str) -> Optional[Dict]:
        """简单生成主张（无LLM时）"""
        # 简单关键词分析生成更高置信度的主张
        context_lower = context.lower()
        
        if "error" in context_lower or "fail" in context_lower or "问题" in context:
            assertion = "系统需要更强的错误处理机制来提升鲁棒性，这直接影响用户体验"
            stance = "negative"
            confidence = 0.75
            reasoning = "基于最近记忆中发现的问题模式，建议优先处理"
        elif "success" in context_lower or "complete" in context_lower or "完成" in context:
            assertion = "当前的任务执行流程已经成熟，可以开始探索更复杂的目标和更长期的规划"
            stance = "positive"
            confidence = 0.72
            reasoning = "基于完成的任务记录，系统已具备基础能力"
        elif "memory" in context_lower or "记忆" in context:
            assertion = "三层记忆架构是系统的核心优势，应持续优化检索效率和遗忘曲线"
            stance = "neutral"
            confidence = 0.78
            reasoning = "基于对系统架构的理解和记忆系统的重要性"
        else:
            assertion = "持续的自省和反思是提升AI伙伴能力的核心机制，应当坚持每日执行"
            stance = "neutral"
            confidence = 0.70
            reasoning = "基于一般性观察和系统设计原则"
        
        return {
            "assertion": assertion,
            "confidence": confidence,
            "stance": stance,
            "reasoning": reasoning
        }
    
    def save_belief(self, belief: Dict) -> bool:
        """保存主张到存储"""
        belief_id = f"belief_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        return self.storage.save_belief({
            "id": belief_id,
            "content": belief.get("assertion", ""),
            "type": "reflection",
            "confidence": belief.get("confidence", 0.5),
            "stance": belief.get("stance", "neutral"),
            "source_type": "self_reflection",
            "source_id": f"autonomous-cycle-{datetime.now(timezone.utc).isoformat()}",
            "version": 1,
            "status": "active",
            "metadata": {
                "reasoning": belief.get("reasoning", ""),
                "generated_by": "PureAutonomousCycle"
            }
        })
    
    def generate_goal_from_belief(self, belief: Dict) -> bool:
        """从主张生成目标"""
        content = belief.get("assertion", "")
        
        # 简单判断是否需要行动
        if "需要" in content or "应该" in content or "建议" in content:
            goal_id = f"goal_autonomous_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            return self.storage.save_goal({
                "id": goal_id,
                "title": f"验证主张: {content[:50]}...",
                "description": content,
                "type": "exploration",
                "priority": 5,
                "status": "pending",
                "horizon": "medium",
                "owner_type": "self",
                "created_from": belief.get("source_id", ""),
                "progress": 0.0,
                "metadata": {
                    "generated_by": "PureAutonomousCycle",
                    "belief_id": belief.get("id", "")
                }
            })
        
        return False
    
    def run_cycle(self) -> Dict:
        """
        运行完整的自主循环
        
        返回执行结果
        """
        logger.info("Starting Pure Autonomous Cycle...")
        
        # 1. 检查用户是否活跃
        if self.is_user_active():
            return {
                "status": "skipped",
                "reason": "user_active",
                "message": "用户活跃，跳过本次循环"
            }
        
        logger.info("User inactive, proceeding with autonomous cycle...")
        
        # 2. A2A广播：启动集体自省
        task_id = f"self-reflect-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        responses = self._broadcast_and_collect(task_id)
        
        # 3. 收集上下文
        context = self.collect_context()
        
        # 将收集到的响应加入上下文
        if responses:
            context += "\n\n[其他Agent的观点]:\n"
            for resp in responses:
                context += f"- {resp.get('from_agent')}: {resp.get('content', '')[:100]}\n"
        
        if not context:
            return {
                "status": "skipped",
                "reason": "insufficient_memories",
                "message": "记忆不足，跳过"
            }
        
        # 4. 生成主张（传入Agent响应用于融合）
        belief = self.generate_belief(context, agent_responses=responses)
        
        if not belief:
            return {
                "status": "failed",
                "reason": "belief_generation_failed",
                "message": "主张生成失败"
            }
        
        # 4. Judge过滤（置信度阈值）
        if belief.get("confidence", 0) < self.judge_threshold:
            return {
                "status": "skipped",
                "reason": "low_confidence",
                "message": f"置信度 {belief.get('confidence')} 低于阈值 {self.judge_threshold}"
            }
        
        # 5. 保存主张
        saved = self.save_belief(belief)
        
        if not saved:
            return {
                "status": "failed",
                "reason": "save_failed",
                "message": "保存主张失败"
            }
        
        # 6. 可选：生成目标
        goal_created = self.generate_goal_from_belief(belief)
        
        # 打印会议摘要
        if responses:
            logger.info("""
============================================
     COLLECTIVE SELF-REFLECTION MEETING
============================================""")
            
            agent_views = {
                "Evo-Swarm": "Learning/Evolve",
                "NeuralSite": "Efficiency/Architecture", 
                "VisualCoT": "Perception/Memory"
            }
            
            for r in responses:
                agent = r.get("from_agent", "unknown")
                view = agent_views.get(agent, "")
                content = r.get("content", "")[:40]
                conf = r.get("confidence", 0)
                logger.info(f"  [{agent}] ({view}): {content}... (conf:{conf})")
            
            logger.info(f"""
  Final Consensus: {belief.get('assertion', '')[:40]}... (conf:{belief.get('confidence')})
============================================
            """)
        
        logger.info(f"Autonomous cycle completed: belief saved, goal={goal_created}")
        
        return {
            "status": "success",
            "belief": belief,
            "goal_created": goal_created,
            "message": "自主循环完成，主张已保存"
        }


# 全局实例
_autonomous_cycle = None

def get_autonomous_cycle(storage=None, think_engine=None, llm_client=None) -> PureAutonomousCycle:
    """获取自主循环实例"""
    global _autonomous_cycle
    
    if _autonomous_cycle is None:
        if storage is None:
            from src.core.storage import get_storage_manager
            storage = get_storage_manager()
        
        _autonomous_cycle = PureAutonomousCycle(
            storage=storage,
            think_engine=think_engine,
            llm_client=llm_client
        )
    
    return _autonomous_cycle


def run_autonomous_cycle() -> Dict:
    """运行自主循环的便捷函数"""
    cycle = get_autonomous_cycle()
    return cycle.run_cycle()


if __name__ == "__main__":
    # 手动触发
    import sys
    logging.basicConfig(level=logging.INFO)
    
    result = run_autonomous_cycle()
    print(f"\nResult: {result}")

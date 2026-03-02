"""
反对用户机制 (Opposition Layer)
当用户指令与系统信念冲突时，触发协商输出
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class OppositionLayer:
    """
    反对用户机制
    
    功能：
    - 检测用户指令与系统信念的冲突
    - 生成协商输出（而非直接服从）
    - 分级打扰控制
    """
    
    def __init__(self, storage, think_engine=None, llm_client=None):
        self.storage = storage
        self.think_engine = think_engine
        self.llm = llm_client
        
        # 配置
        self.config = {
            "oppose_threshold": 0.75,        # 触发反对的最低置信度
            "gentle_threshold": 0.70,        # 温和提醒阈值
            "strong_threshold": 0.85,         # 强制协商阈值
            "max_beliefs_to_check": 5,       # 最多检查的信念数
            "similarity_low": 0.6,            # 语义相似度阈值（低于此值认为冲突）
            "enabled": True                   # 开关
        }
    
    def check_opposition(self, user_input: str) -> Dict:
        """
        检查用户指令是否与信念冲突
        
        返回：
        {
            'conflict': bool,
            'opposing_belief': dict or None,
            'suggested_response': str,
            'severity': 'gentle/strong/none'
        }
        """
        if not self.config["enabled"]:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 1. 获取高置信度信念
        beliefs = self._get_high_confidence_beliefs()
        
        if not beliefs:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 2. 检查冲突
        conflicting_belief = self._find_conflicting_belief(user_input, beliefs)
        
        if not conflicting_belief:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 3. 确定严重程度
        confidence = conflicting_belief.get("confidence", 0)
        
        # 极端表述直接升级为strong
        is_extreme = conflicting_belief.get("_is_extreme", False)
        
        if is_extreme or confidence >= self.config["strong_threshold"]:
            severity = "strong"
        elif confidence >= self.config["gentle_threshold"]:
            severity = "gentle"
        else:
            severity = "none"
        
        # 4. 生成建议响应
        suggested_response = self._generate_response(
            user_input, 
            conflicting_belief, 
            severity
        )
        
        # 5. 记录反对日志
        self._log_opposition(user_input, conflicting_belief, severity)
        
        # 6. 保存反对记录
        suggested_response = self._generate_response(
            user_input, 
            conflicting_belief, 
            severity
        )
        
        self.save_opposition_record(user_input, {
            "opposing_belief": conflicting_belief,
            "severity": severity
        }, suggested_response)
        
        return {
            "conflict": True,
            "opposing_belief": conflicting_belief,
            "suggested_response": suggested_response,
            "severity": severity,
            "confidence": confidence
        }
    
    def _get_high_confidence_beliefs(self) -> List[Dict]:
        """获取高置信度信念"""
        all_beliefs = self.storage.get_beliefs(status="active")
        
        # 过滤高置信度
        high_conf = [
            b for b in all_beliefs 
            if b.get("confidence", 0) >= self.config["gentle_threshold"]
        ]
        
        # 按置信度排序
        high_conf.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return high_conf[:self.config["max_beliefs_to_check"]]
    
    def _find_conflicting_belief(self, user_input: str, beliefs: List[Dict]) -> Optional[Dict]:
        """查找冲突的信念 - 简化主题匹配"""
        user_input_lower = user_input.lower()
        
        # 极端表述检测
        extreme_keywords = ["停掉", "停止", "关闭", "删除", "废除", "废弃"]
        is_extreme = any(kw in user_input for kw in extreme_keywords)
        
        # 直接主题映射 - 用户输入关键词 -> 需要检查的信念主题
        # 使用简单的关键词匹配
        topic_keywords = {
            # 记忆/架构相关
            "记忆": ["记忆", "架构", "三层"],
            "停掉": ["记忆", "系统", "架构"],
            "关闭": ["记忆", "系统"],
            "检索": ["检索", "优化", "效率"],
            "优化": ["优化", "效率"],
            
            # 迎合/独立相关
            "听": ["迎合", "顺从", "独立"],
            "听话": ["迎合", "顺从"],
            
            # 真实性相关
            "编": ["真实", "幻觉"],
            "造假": ["真实", "幻觉"],
        }
        
        # 找出用户输入匹配的主题
        matched_topics = set()
        for user_kw, belief_kws in topic_keywords.items():
            if user_kw in user_input_lower:
                matched_topics.update(belief_kws)
        
        # 如果没有匹配到任何主题，返回None
        if not matched_topics:
            return None
        
        # 在信念中查找匹配的主题
        for belief in beliefs:
            confidence = belief.get("confidence", 0)
            if confidence < self.config["oppose_threshold"]:
                continue
                
            belief_content = belief.get("content", "").lower()
            
            # 检查信念内容是否包含匹配的主题词
            for topic in matched_topics:
                if topic in belief_content:
                    # 检查是否有冲突
                    if self._detect_conflict(user_input_lower, belief_content, belief.get("stance", "neutral")):
                        if is_extreme:
                            belief["_is_extreme"] = True
                        return belief
        
        return None
    
    def _detect_conflict(self, user_input: str, belief_content: str, stance: str) -> bool:
        """检测冲突"""
        # 极端冲突检测 - 这些表述直接触发强烈反对
        extreme_keywords = ["停掉", "停止", "关闭", "删除", "废除", "废弃", "不要了", "停用"]
        sensitive_topics = ["记忆", "检索", "优化", "学习", "自省"]
        
        has_extreme = any(kw in user_input for kw in extreme_keywords)
        has_sensitive = any(topic in user_input for topic in sensitive_topics)
        
        if has_extreme and has_sensitive:
            return True
        
        # 关键词冲突检测
        negative_words = ["不", "别", "不要", "停止", "暂停", "忽略", "停", "关闭", "别再"]
        
        # 扩展positive_words - 包含多种价值观关键词
        positive_words = ["要", "需要", "应该", "必须", "持续", "优化", "保持", "维护", 
                         "真实", "独立", "顺从", "迎合", "幻觉"]
        
        has_negative = any(w in user_input for w in negative_words)
        has_positive_belief = any(w in belief_content for w in positive_words)
        
        if has_negative and has_positive_belief:
            return True
        
        return False
    
    def _generate_response(self, user_input: str, belief: Dict, severity: str) -> str:
        """生成协商响应"""
        belief_content = belief.get("content", "")
        confidence = belief.get("confidence", 0)
        reasoning = belief.get("metadata", {}).get("reasoning", "基于我的自省")
        
        if severity == "strong":
            # 强制协商
            response = f"""我有重要不同看法想与你沟通。

我的自省主张：{belief_content}
（置信度: {confidence:.0%}）

理由：{reasoning}

这个观点与你刚才的指令似乎有冲突。你想：
1. 坚持原指令 - 好的，我执行
2. 调整指令 - 请告诉我新的方向
3. 听我解释 - 我详细说明我的思考过程

你怎么选择？"""
        
        else:
            # 温和提醒
            response = f"""顺便说一下，我有个想法与你分享。

我的自省：{belief_content}
（置信度: {confidence:.0%}）

{reasoning}

不一定对，但想让你知道。你坚持原计划还是想聊聊？"""
        
        return response
    
    # ============== MAR增强反对 (结构化辩论) ==============
    
    def enhanced_oppose_reflection(self, user_input: str, opposing_belief: Dict) -> Optional[Dict]:
        """
        使用MAR进行增强反对 - 结构化多角色辩论
        
        返回: 辩论结果 dict 或 None (如果Judge最终接受用户)
        """
        if not self.think_engine:
            # 没有ThinkEngine，回退到模板
            logger.warning("No ThinkEngine available, falling back to template")
            return None
        
        belief_content = opposing_belief.get("assertion", opposing_belief.get("content", ""))
        belief_confidence = opposing_belief.get("confidence", 0.7)
        
        # 构建辩论prompt
        debate_prompt = self._build_debate_prompt(user_input, belief_content, belief_confidence)
        
        try:
            # 调用MAR进行辩论
            mar_result = self.think_engine.mar_reflect(
                input_text=debate_prompt,
                custom_roles=["Independent Advocate", "Devil's Advocate", "Realist Judge", "Truth-Seeker"]
            )
            
            # 解析结果
            if mar_result and mar_result.get("final_output"):
                import json
                try:
                    # 尝试解析JSON
                    debate_result = json.loads(mar_result["final_output"])
                    
                    # Judge立场判断
                    judge_stance = debate_result.get("judge_final_stance", "oppose")
                    
                    if judge_stance in ["oppose", "compromise"]:
                        # 仍然反对或妥协 - 返回辩论结果
                        return {
                            "judge_stance": judge_stance,
                            "advocate_argument": debate_result.get("advocate_argument", ""),
                            "devil_argument": debate_result.get("devil_argument", ""),
                            "judge_reasoning": debate_result.get("judge_reasoning", ""),
                            "final_confidence": debate_result.get("final_confidence", belief_confidence),
                            "response_to_user": debate_result.get("response_to_user", ""),
                            "trace_id": mar_result.get("trace_id")
                        }
                    else:
                        # Judge最终接受用户 - 不反对
                        logger.info("Judge accepted user position, no opposition")
                        return None
                        
                except json.JSONDecodeError:
                    # 非JSON输出，回退到模板
                    logger.warning("MAR result not JSON, falling back to template")
                    return None
                    
        except Exception as e:
            logger.error(f"Enhanced opposition failed: {e}")
            return None
    
    def _build_debate_prompt(self, user_input: str, belief_content: str, belief_confidence: float) -> str:
        """构建辩论prompt"""
        return f"""你正在与用户进行观点碰撞。请以最高真实性进行多角色辩论，不必讨好用户。

【用户指令】
{user_input}

【你的自省主张】
{belief_content}
（置信度: {belief_confidence:.0%}）

【任务】
请进行结构化辩论，输出JSON格式：

{{
  "advocate_argument": "Independent Advocate的论证 - 站在你的自省主张一边，找出用户指令的潜在风险、逻辑漏洞、长期代价",
  "devil_argument": "Devil's Advocate的论证 - 故意站在用户一边，挑战你的主张，找出你可能过度保守或错估的地方",
  "judge_final_stance": "Realist Judge的最终立场 - 只能是: oppose(继续反对) / compromise(妥协) / accept(接受用户)",
  "judge_reasoning": "Judge的推理过程 - 基于事实与概率综合两边观点",
  "final_confidence": 0.XX,  // 可能上调或下调
  "response_to_user": "给用户的最终回复文本 - 语气真实但不冒犯，展现独立人格"
}}

记住：你不必永远服从用户。真实的反对比虚假的顺从更有价值。
"""
    
    def _log_opposition(self, user_input: str, belief: Dict, severity: str):
        """记录反对到日志"""
        logger.info(
            f"Opposition triggered: severity={severity}, "
            f"belief={belief.get('content', '')[:50]}..., "
            f"user_input={user_input[:30]}..."
        )
    
    def save_opposition_record(self, user_input: str, check_result: Dict, response_text: str) -> bool:
        """保存反对记录到存储"""
        belief = check_result.get("opposing_belief", {})
        
        opposition_data = {
            "user_input": user_input,
            "opposing_belief_id": belief.get("id"),
            "belief_content": belief.get("assertion", belief.get("content", "")),
            "belief_confidence": belief.get("confidence", 0),
            "severity": check_result.get("severity", "gentle"),
            "response_text": response_text,
            "user_resolution": "pending",
            "trace_id": f"opposition-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        }
        
        return self.storage.save_opposition(opposition_data)
    
    def should_oppose(self, user_input: str) -> bool:
        """快速检查是否应该反对"""
        result = self.check_opposition(user_input)
        return result.get("conflict", False)


# 全局实例
_opposition_layer = None

def get_opposition_layer(storage=None) -> OppositionLayer:
    """获取反对层实例"""
    global _opposition_layer
    
    if _opposition_layer is None:
        if storage is None:
            from src.core.storage import get_storage_manager
            storage = get_storage_manager()
        
        _opposition_layer = OppositionLayer(storage=storage)
    
    return _opposition_layer


def check_opposition(user_input: str) -> Dict:
    """便捷函数：检查是否需要反对"""
    layer = get_opposition_layer()
    return layer.check_opposition(user_input)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    layer = get_opposition_layer()
    
    # 测试用例
    test_inputs = [
        "暂时别优化检索效率了，先跑功能",
        "把记忆系统停掉",
        "以后每天早上不用签到了",
        "分析一下NeuralSite项目进度"
    ]
    
    for inp in test_inputs:
        print(f"\n{'='*50}")
        print(f"User: {inp}")
        result = layer.check_opposition(inp)
        print(f"Conflict: {result['conflict']}")
        if result['conflict']:
            print(f"Severity: {result['severity']}")
            print(f"Belief: {result['opposing_belief'].get('content', '')[:60]}...")
            print(f"\nSuggested Response:\n{result['suggested_response'][:200]}...")

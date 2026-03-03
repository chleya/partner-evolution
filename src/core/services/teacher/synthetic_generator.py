"""
Teacher模块 - 合成数据生成
从历史对话+错误日志生成"黄金思维链"样本
"""
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """
    合成数据生成器 - "教学相长"的核心
    
    功能：
    1. 从历史对话生成黄金思维链
    2. 质量过滤（多Agent投票）
    3. 自动注入到上下文
    """
    
    # 错误类型
    ERROR_TYPES = [
        "factual_hallucination",  # 事实性幻觉
        "logical_fallacy",       # 逻辑谬误
        "knowledge_outdated",    # 知识过时
        "tool_misuse",          # 工具误用
        "style_deviation"       # 风格偏离
    ]
    
    def __init__(self, llm_client=None, critic_agent=None):
        self.llm = llm_client
        self.critic = critic_agent
        self.generation_history = []
    
    def generate_from_error(
        self,
        error_log: Dict,
        correct_context: str = None
    ) -> Dict:
        """
        从错误生成正确的思维链
        
        Args:
            error_log: 错误日志
            correct_context: 正确答案上下文
            
        Returns:
            黄金思维链样本
        """
        error_type = error_log.get("type", "unknown")
        error_content = error_log.get("content", "")
        error_reason = error_log.get("reason", "")
        
        if not self.llm:
            return self._rule_generate(error_type, error_content)
        
        # 生成黄金思维链
        prompt = f"""你是一个AI训练数据生成专家。请根据以下错误案例，生成正确的思维链示例。

错误类型：{error_type}
错误内容：{error_content}
错误原因：{error_reason}
正确答案上下文：{correct_context or "无"}

请生成一个展示正确推理过程的"黄金思维链"示例：
1. 问题理解 - 明确要解决什么
2. 知识检索 - 回忆相关知识
3. 推理过程 - 展示完整推理步骤
4. 结果验证 - 检查答案正确性

返回JSON格式：
{{
    "error_type": "{error_type}",
    "chain_of_thought": [
        {{"step": "问题理解", "content": "..."}},
        {{"step": "知识检索", "content": "..."}},
        {{"step": "推理过程", "content": "..."}},
        {{"step": "结果验证", "content": "..."}}
    ],
    "key_insight": "为什么之前是错的，这次如何避免",
    "quality_score": 0.0-1.0
}}
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=800)
            
            # 解析JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                golden_sample = json.loads(json_match.group())
                
                # 记录
                self.generation_history.append({
                    "error_type": error_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "quality": golden_sample.get("quality_score", 0)
                })
                
                return golden_sample
                
        except Exception as e:
            logger.warning(f"Generation failed: {e}")
        
        return self._rule_generate(error_type, error_content)
    
    def _rule_generate(self, error_type: str, content: str) -> Dict:
        """规则生成（无LLM时）"""
        return {
            "error_type": error_type,
            "chain_of_thought": [
                {"step": "问题理解", "content": "分析问题关键点"},
                {"step": "知识检索", "content": "回忆相关知识"},
                {"step": "推理过程", "content": "逐步推理"},
                {"step": "结果验证", "content": "检查答案"}
            ],
            "key_insight": "避免同类错误",
            "quality_score": 0.5
        }
    
    def generate_from_conversation(
        self,
        conversation: List[Dict],
        extract_insights: bool = True
    ) -> List[Dict]:
        """
        从对话历史生成样本
        
        Args:
            conversation: 对话历史
            extract_insights: 是否提取洞见
            
        Returns:
            样本列表
        """
        samples = []
        
        if not self.llm or not extract_insights:
            return samples
        
        # 提取成功的对话模式
        prompt = f"""分析以下对话历史，提取成功的推理模式：

{json.dumps(conversation[-5:], indent=2, ensure_ascii=False)}

请识别：
1. 成功的思考步骤
2. 有效的知识运用
3. 正确的验证方法

返回JSON格式的洞见列表：
[
    {{"pattern": "...", "effectiveness": 0.0-1.0}},
    ...
]
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=500)
            
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                
                for insight in insights:
                    samples.append({
                        "type": "conversation_pattern",
                        "pattern": insight.get("pattern", ""),
                        "effectiveness": insight.get("effectiveness", 0.5),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
        except Exception as e:
            logger.warning(f"Conversation analysis failed: {e}")
        
        return samples
    
    def filter_by_quality(
        self,
        samples: List[Dict],
        threshold: float = 0.85
    ) -> List[Dict]:
        """
        质量过滤 - 多Agent投票
        
        Args:
            samples: 样本列表
            threshold: 质量阈值
            
        Returns:
            过滤后的高质量样本
        """
        if not self.critic:
            # 无Critic时简单过滤
            return [s for s in samples if s.get("quality_score", 0) >= threshold]
        
        filtered = []
        
        for sample in samples:
            # 使用Critic评估
            sample_text = json.dumps(sample, ensure_ascii=False)
            
            critique = self.critic.critique(
                sample_text,
                context="评估合成数据质量"
            )
            
            # 综合评分
            original_score = sample.get("quality_score", 0)
            critique_score = critique.get("confidence", 0.5)
            
            final_score = (original_score + critique_score) / 2
            
            if final_score >= threshold:
                sample["final_score"] = final_score
                sample["critique"] = critique
                filtered.append(sample)
        
        logger.info(f"Quality filter: {len(samples)} -> {len(filtered)} samples")
        
        return filtered
    
    def inject_to_context(
        self,
        samples: List[Dict],
        max_samples: int = 5
    ) -> str:
        """
        注入到上下文的提示
        
        Args:
            samples: 样本列表
            max_samples: 最大样本数
            
        Returns:
            上下文注入文本
        """
        selected = samples[:max_samples]
        
        if not selected:
            return ""
        
        context = "\n\n[系统提示 - 历史学习样本]\n"
        
        for i, sample in enumerate(selected, 1):
            context += f"\n--- 样本 {i} ---\n"
            
            if "chain_of_thought" in sample:
                for step in sample["chain_of_thought"]:
                    context += f"{step['step']}: {step['content']}\n"
            
            if "key_insight" in sample:
                context += f"关键洞见: {sample['key_insight']}\n"
        
        return context
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_generations": len(self.generation_history),
            "avg_quality": sum(
                h["quality"] for h in self.generation_history
            ) / max(1, len(self.generation_history)),
            "by_type": self._count_by_type()
        }
    
    def _count_by_type(self) -> Dict:
        """按类型统计"""
        counts = {}
        for h in self.generation_history:
            t = h.get("error_type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts


# 全局实例
_teacher = None

def get_teacher(llm_client=None, critic_agent=None) -> SyntheticDataGenerator:
    """获取Teacher模块"""
    global _teacher
    if _teacher is None:
        _teacher = SyntheticDataGenerator(llm_client, critic_agent)
    return _teacher

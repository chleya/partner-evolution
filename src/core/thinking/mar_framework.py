"""
MAR多智能体反思框架 (Multi-Agent Reflection)
三角色反思：乐观批判者、风险分析师、综合者
支持真实LLM调用
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 尝试导入LLM客户端
try:
    from src.utils.llm_client import MiniMaxClient, get_client
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    MiniMaxClient = None
    get_client = None


class PersonaType(Enum):
    """反思角色类型"""
    OPTIMIST = "optimist"      # 乐观批判者 - 发现机会
    PESSIMIST = "pessimist"    # 风险分析师 - 识别问题
    SYNTHESIST = "synthesist"  # 综合者 - 整合结论


@dataclass
class Persona:
    """反思智能体角色定义"""
    name: str
    persona_type: PersonaType
    system_prompt: str
    thinking_style: str


class MARFramework:
    """
    多智能体反思框架
    借鉴Reflexion论文和MAR研究，实现多角度反思
    """

    # 预定义角色池
    PERSONA_POOL = {
        PersonaType.OPTIMIST: Persona(
            name="乐观批判者",
            persona_type=PersonaType.OPTIMIST,
            system_prompt="""你是一个乐观的批判者，总是能看到事情积极的一面。
你需要从当前思考中找出潜在的机会和收益，用积极的视角重新解读信息。
关注：机会、潜力、收益、可能性、成长空间""",
            thinking_style="关注机会、潜力、收益、可能性"
        ),
        PersonaType.PESSIMIST: Persona(
            name="风险分析师",
            persona_type=PersonaType.PESSIMIST,
            system_prompt="""你是一个风险分析师，总是关注最坏的情况。
你需要从当前思考中找出潜在的问题、风险和威胁，提出警示。
关注：风险、问题、威胁、失败模式、隐患""",
            thinking_style="关注风险、问题、威胁、失败模式"
        ),
        PersonaType.SYNTHESIST: Persona(
            name="综合者",
            persona_type=PersonaType.SYNTHESIST,
            system_prompt="""你是一个综合者，擅长整合不同观点形成结论。
你需要综合各个角度的分析，给出平衡而全面的判断。
关注：整合、平衡、归纳、总结、共识""",
            thinking_style="整合、平衡、归纳、总结"
        )
    }

    def __init__(self, llm_client=None, config: Dict = None):
        """
        初始化MAR框架
        
        Args:
            llm_client: LLM客户端（可选，用于实际LLM调用）
            config: 配置字典
        """
        # 如果没有提供LLM客户端，尝试获取全局客户端
        if llm_client is None and LLM_AVAILABLE:
            try:
                llm_client = get_client()
            except Exception as e:
                logger.warning(f"Failed to get LLM client: {e}")
        
        self.llm = llm_client
        self.config = config or {}
        self.judge_threshold = self.config.get("judge_threshold", 0.7)
        self.reflection_history: List[Dict] = []
        self.use_real_llm = llm_client is not None and LLM_AVAILABLE

    def reflect(
        self,
        context: Dict,
        framework_type: str = "post_mortem"
    ) -> Dict:
        """
        执行多智能体反思
        
        Args:
            context: 思考上下文
            framework_type: 思考类型 (post_mortem/forecasting/association)
        
        Returns:
            反思结果包含三角色观点、评估、结论
        """
        # 1. 并行调用三个角色的反思
        perspectives = self._parallel_reflect(context, framework_type)
        
        # 2. Judge评估各观点
        judged = self._judge_perspectives(perspectives)
        
        # 3. 综合者形成最终结论
        final_conclusion = self._synthesize(judged)
        
        # 4. 记录历史
        result = {
            "perspectives": perspectives,
            "judged": judged,
            "conclusion": final_conclusion,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework_type": framework_type
        }
        self.reflection_history.append(result)
        
        return result

    def _parallel_reflect(
        self,
        context: Dict,
        framework_type: str
    ) -> List[Dict]:
        """并行执行各角色的反思"""
        results = []
        
        # 准备各角色的系统提示
        for persona_type, persona in self.PERSONA_POOL.items():
            prompt = self._build_reflect_prompt(persona, context, framework_type)
            
            # 尝试使用真实LLM，否则使用模拟
            if self.use_real_llm and self.llm:
                try:
                    reflection = self.llm.generate(
                        prompt=prompt,
                        max_tokens=500,
                        temperature=0.7
                    )
                except Exception as e:
                    logger.warning(f"LLM call failed: {e}, using simulation")
                    reflection = self._simulate_llm_reflection(persona_type, context)
            else:
                reflection = self._simulate_llm_reflection(persona_type, context)
            
            results.append({
                "persona": persona.name,
                "type": persona_type.value,
                "reflection": reflection,
                "confidence": 0.8,
                "prompt": prompt
            })
        
        return results

    def _simulate_llm_reflection(
        self,
        persona_type: PersonaType,
        context: Dict
    ) -> str:
        """模拟LLM反思（无LLM时的降级方案）"""
        task = context.get("task", context.get("description", "未知任务"))
        
        if persona_type == PersonaType.OPTIMIST:
            return f"""关于「{task}」的乐观分析：
1. 这是提升系统能力的好机会，可以积累宝贵经验
2. 当前资源充足，有足够空间尝试新方案
3. 完成后将为后续工作奠定坚实基础
4. 建议：抓住机会，积极推进"""
        
        elif persona_type == PersonaType.PESSIMIST:
            return f"""关于「{task}」的风险分析：
1. 可能遇到技术难点，需要预留缓冲时间
2. 资源协调可能存在不确定性
3. 存在需求变更的风险
4. 建议：提前预案，设置检查点"""
        
        else:  # SYNTHESIST
            return f"""关于「{task}」的综合建议：
1. 机会与风险并存，建议稳步推进
2. 具体执行时注意风险控制
3. 保持敏捷，随时根据反馈调整
4. 建议：制定详细计划，分阶段验证"""

    def _judge_perspectives(self, perspectives: List[Dict]) -> List[Dict]:
        """Judge评估各观点"""
        # 构建评估prompt
        evaluations = []
        
        for perspective in perspectives:
            # 简化的评估逻辑
            relevance = 0.7 + (hash(perspective["persona"]) % 30) / 100
            depth = 0.6 + (hash(perspective["type"]) % 40) / 100
            actionability = 0.65 + (hash(perspective["reflection"][:10]) % 35) / 100
            
            overall = (relevance + depth + actionability) / 3
            
            evaluation = {
                "persona": perspective["persona"],
                "relevance": round(relevance, 2),
                "depth": round(depth, 2),
                "actionability": round(actionability, 2),
                "overall": round(overall, 2)
            }
            evaluations.append(evaluation)
            
            # 添加评估结果到观点
            perspective["evaluation"] = evaluation
        
        return perspectives

    def _synthesize(self, judged: List[Dict]) -> Dict:
        """综合者形成最终结论"""
        # 提取评估结果
        evaluations = [p.get("evaluation", {"overall": 0.5}) for p in judged]
        
        # 计算加权平均
        total_weight = sum(e["overall"] for e in evaluations)
        if total_weight > 0:
            weighted_confidence = sum(
                e["overall"] * (1.0 / len(evaluations)) 
                for e in evaluations
            )
        else:
            weighted_confidence = 0.5
        
        # 提取共识和分歧
        insights = []
        agreements = []
        disagreements = []
        
        for p in judged:
            # 简单提取第一句作为洞见
            lines = p.get("reflection", "").split("\n")
            if lines:
                insights.append(lines[0].strip())
        
        # 生成建议
        recommendations = [
            "建议综合各角色观点，根据实际情况决策",
            "保持开放心态，随时调整策略",
            "定期复盘，持续优化"
        ]
        
        return {
            "summary": f"综合{len(judged)}个视角的观点，形成平衡建议",
            "insights": insights,
            "agreements": agreements,
            "disagreements": disagreements,
            "recommendations": recommendations,
            "confidence": round(weighted_confidence, 2)
        }

    def _build_reflect_prompt(
        self,
        persona: Persona,
        context: Dict,
        framework_type: str
    ) -> str:
        """构建反思提示"""
        context_json = json.dumps(context, ensure_ascii=False, indent=2)
        
        return f"""你正在执行{framework_type}类型的思考。

你的角色是：{persona.name}
角色特点：{persona.system_prompt}
思考风格：{persona.thinking_style}

当前上下文：
{context_json}

请基于你的角色特点，对上述上下文进行反思分析。
"""

    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取反思历史"""
        return self.reflection_history[-limit:]

    def clear_history(self):
        """清空反思历史"""
        self.reflection_history.clear()

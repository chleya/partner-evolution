"""
MAR v2 - 多智能体反思框架深度优化
支持多样persona + Judge评估 + 反思日志
"""
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class PersonaType(Enum):
    """角色类型"""
    OPTIMIST = "optimist"      # 乐观批判者
    PESSIMIST = "pessimist"    # 风险分析师
    SYNTHESIST = "synthesist"  # 综合者
    CREATIVE = "creative"      # 创意者
    ANALYTIC = "analytic"      # 分析者
    PRAGMATIC = "pragmatic"   # 务实者


class ReflectionQuality(Enum):
    """反思质量等级"""
    EXCELLENT = "excellent"    # 优秀
    GOOD = "good"              # 良好
    ACCEPTABLE = "acceptable"  # 可接受
    NEEDS_IMPROVEMENT = "needs_improvement"  # 需要改进


@dataclass
class Persona:
    """角色定义"""
    name: str
    persona_type: PersonaType
    system_prompt: str
    thinking_style: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class ReflectionResult:
    """反思结果"""
    persona: str
    reflection: str
    confidence: float
    quality: ReflectionQuality
    insights: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class JudgeEvaluation:
    """Judge评估结果"""
    overall_score: float
    quality: ReflectionQuality
    perspective_diversity: float
    insight_depth: float
    actionability: float
    confidence_calibration: float
    feedback: str
    improvements: List[str] = field(default_factory=list)


class MARFrameworkV2:
    """
    MAR多智能体反思框架 v2
    
    特性：
    - 6种角色（扩展自v1的3种）
    - 自动Judge评估
    - 反思日志与历史
    - 质量追踪
    - 自我改进机制
    """
    
    # 角色池
    PERSONA_POOL = {
        PersonaType.OPTIMIST: Persona(
            name="乐观批判者",
            persona_type=PersonaType.OPTIMIST,
            system_prompt="""你是一个乐观的批判者，总是能看到事情积极的一面。
你需要从当前思考中找出潜在的机会和收益，用积极的视角重新解读信息。
关注：机会、潜力、收益、可能性、成长空间""",
            thinking_style="关注机会、潜力、收益、可能性",
            strengths=["发现机会", "积极思考", "激励团队"],
            weaknesses=["可能过度乐观", "忽视风险"]
        ),
        PersonaType.PESSIMIST: Persona(
            name="风险分析师",
            persona_type=PersonaType.PESSIMIST,
            system_prompt="""你是一个风险分析师，总是关注最坏的情况。
你需要从当前思考中找出潜在的问题、风险和威胁，提出警示。
关注：风险、问题、威胁、失败模式、隐患""",
            thinking_style="关注风险、问题、威胁、失败模式",
            strengths=["识别风险", "预防问题", "保守决策"],
            weaknesses=["可能过度悲观", "阻碍创新"]
        ),
        PersonaType.SYNTHESIST: Persona(
            name="综合者",
            persona_type=PersonaType.SYNTHESIST,
            system_prompt="""你是一个综合者，擅长整合不同观点形成结论。
你需要综合各个角度的分析，给出平衡而全面的判断。
关注：整合、平衡、归纳、总结、共识""",
            thinking_style="整合、平衡、归纳、总结",
            strengths=["整合观点", "平衡决策", "达成共识"],
            weaknesses=["可能缺乏深度"]
        ),
        PersonaType.CREATIVE: Persona(
            name="创意者",
            persona_type=PersonaType.CREATIVE,
            system_prompt="""你是一个创意者，擅长打破常规思维。
你需要从当前思考中找出创新点和突破方向，提出新颖的解决方案。
关注：创新、突破、新视角、可能性、创造力""",
            thinking_style="创新、突破、新视角、创造力",
            strengths=["创新思维", "突破常规", "新颖方案"],
            weaknesses=["可能不切实际"]
        ),
        PersonaType.ANALYTIC: Persona(
            name="分析者",
            persona_type=PersonaType.ANALYTIC,
            system_prompt="""你是一个分析者，擅长逻辑推理和数据分析。
你需要从当前思考中找出逻辑漏洞和数据支撑，给出理性分析。
关注：逻辑、数据、证据、推理、分析""",
            thinking_style="逻辑、数据、证据、推理",
            strengths=["逻辑严密", "数据支撑", "理性分析"],
            weaknesses=["可能缺乏创意"]
        ),
        PersonaType.PRAGMATIC: Persona(
            name="务实者",
            persona_type=PersonaType.PRAGMATIC,
            system_prompt="""你是一个务实者，关注实际可行性和执行力。
你需要从当前思考中找出落地难点和执行路径，给出可操作的建议。
关注：可行性、执行、落地、效率、成本""",
            thinking_style="可行性、执行、落地、效率",
            strengths=["可行性强", "注重执行", "关注效率"],
            weaknesses=["可能缺乏远见"]
        )
    }
    
    def __init__(self, llm_client=None, config: Dict = None):
        self.llm = llm_client
        self.config = config or {}
        self.judge_threshold = self.config.get("judge_threshold", 0.7)
        self.reflection_history: List[Dict] = []
        self.quality_tracker: List[JudgeEvaluation] = []
        self.use_real_llm = llm_client is not None
        
        # 导入Judge
        try:
            from src.core.thinking.mar_framework import Judge
            self.judge = Judge(threshold=self.judge_threshold)
        except:
            self.judge = None
    
    def reflect(
        self,
        context: Dict,
        framework_type: str = "post_mortem",
        selected_personas: List[PersonaType] = None
    ) -> Dict:
        """
        执行多智能体反思 v2
        
        Args:
            context: 思考上下文
            framework_type: 思考类型
            selected_personas: 指定使用的角色（可选）
        """
        # 选择角色
        if selected_personas is None:
            # 默认选择3个代表性角色
            selected_personas = [
                PersonaType.OPTIMIST,
                PersonaType.PESSIMIST,
                PersonaType.SYNTHESIST
            ]
        
        # 并行反思
        reflections = self._parallel_reflect(context, framework_type, selected_personas)
        
        # Judge评估
        if self.judge:
            evaluation = self._evaluate_reflections(reflections, context)
        else:
            evaluation = self._simple_evaluate(reflections)
        
        # 综合结论
        final_conclusion = self._synthesize_v2(reflections, evaluation)
        
        # 记录历史
        result = {
            "reflections": reflections,
            "evaluation": evaluation,
            "conclusion": final_conclusion,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework_type": framework_type,
            "personas_used": [p.value for p in selected_personas]
        }
        self.reflection_history.append(result)
        
        # 追踪质量
        if evaluation:
            self.quality_tracker.append(evaluation)
        
        return result
    
    def _parallel_reflect(
        self,
        context: Dict,
        framework_type: str,
        personas: List[PersonaType]
    ) -> List[ReflectionResult]:
        """并行执行各角色的反思"""
        results = []
        
        for persona_type in personas:
            persona = self.PERSONA_POOL.get(persona_type)
            if not persona:
                continue
            
            prompt = self._build_reflect_prompt(persona, context, framework_type)
            
            # LLM调用
            if self.use_real_llm and self.llm:
                try:
                    reflection_text = self.llm.generate(
                        prompt=prompt,
                        max_tokens=500,
                        temperature=0.7
                    )
                except Exception as e:
                    logger.warning(f"LLM call failed: {e}")
                    reflection_text = self._simulate_reflection(persona_type, context)
            else:
                reflection_text = self._simulate_reflection(persona_type, context)
            
            # 解析反思结果
            result = self._parse_reflection(persona, reflection_text)
            results.append(result)
        
        return results
    
    def _build_reflect_prompt(
        self,
        persona: Persona,
        context: Dict,
        framework_type: str
    ) -> str:
        """构建反思提示"""
        prompt = f"""{persona.system_prompt}

当前任务上下文：
{json.dumps(context, ensure_ascii=False, indent=2)}

思考框架类型：{framework_type}

请从你的角度进行反思，给出你的观点、洞察和建议。
"""
        return prompt
    
    def _simulate_reflection(
        self,
        persona_type: PersonaType,
        context: Dict
    ) -> str:
        """模拟LLM反思"""
        task = context.get("task", "")
        project = context.get("project", "")
        
        reflections = {
            PersonaType.OPTIMIST: f"关于{task}，我认为存在以下机会：1) 项目{project}有巨大潜力 2) 可以通过优化流程提升效率 3) 团队协作可以进一步增强。建议积极推进，把握机会。",
            PersonaType.PESSIMIST: f"关于{task}，我注意到以下风险：1) 项目{project}可能遇到技术难点 2) 资源可能不足 3) 时间线可能过于紧张。需要提前准备应急预案。",
            PersonaType.SYNTHESIST: f"综合分析{task}，平衡机会和风险，建议采取以下策略：1) 积极推进核心功能 2) 预留缓冲时间 3) 定期评估进度。",
            PersonaType.CREATIVE: f"对于{task}，我提出以下创新想法：1) 采用新技术方案 2) 优化用户体验 3) 探索新的商业模式。",
            PersonaType.ANALYTIC: f"从数据角度分析{task}：1) 当前进度符合预期 2) 资源利用率达到80% 3) 建议关注关键路径。",
            PersonaType.PRAGMATIC: f"从执行角度，{task}需要：1) 明确里程碑 2) 分配具体责任 3) 建立进度跟踪机制。"
        }
        
        return reflections.get(persona_type, "需要进一步分析。")
    
    def _parse_reflection(
        self,
        persona: Persona,
        text: str
    ) -> ReflectionResult:
        """解析反思文本"""
        # 简单解析
        lines = text.split("\n")
        insights = [l.strip() for l in lines if "建议" in l or "可以" in l or "能够" in l][:3]
        concerns = [l.strip() for l in lines if "风险" in l or "问题" in l or "不足" in l][:3]
        
        return ReflectionResult(
            persona=persona.name,
            reflection=text,
            confidence=0.8,
            quality=ReflectionQuality.GOOD,
            insights=insights,
            concerns=concerns,
            suggestions=[s for s in insights if "建议" in s]
        )
    
    def _evaluate_reflections(
        self,
        reflections: List[ReflectionResult],
        context: Dict
    ) -> JudgeEvaluation:
        """Judge评估"""
        if not self.judge:
            return self._simple_evaluate(reflections)
        
        # 准备评估数据
        evaluation_data = {
            "reflections": [r.reflection for r in reflections],
            "personas": [r.persona for r in reflections],
            "context": context
        }
        
        # 调用Judge
        try:
            result = self.judge.evaluate(evaluation_data)
            
            return JudgeEvaluation(
                overall_score=result.get("overall_score", 0.7),
                quality=ReflectionQuality(result.get("quality", "good")),
                perspective_diversity=result.get("perspective_diversity", 0.8),
                insight_depth=result.get("insight_depth", 0.7),
                actionability=result.get("actionability", 0.7),
                confidence_calibration=result.get("confidence_calibration", 0.8),
                feedback=result.get("feedback", ""),
                improvements=result.get("improvements", [])
            )
        except:
            return self._simple_evaluate(reflections)
    
    def _simple_evaluate(
        self,
        reflections: List[ReflectionResult]
    ) -> JudgeEvaluation:
        """简单评估"""
        # 计算多样性
        unique_personas = len(set(r.persona for r in reflections))
        diversity = min(unique_personas / 3.0, 1.0)
        
        # 计算平均置信度
        avg_confidence = sum(r.confidence for r in reflections) / len(reflections) if reflections else 0
        
        # 质量等级
        if avg_confidence >= 0.85 and diversity >= 0.8:
            quality = ReflectionQuality.EXCELLENT
            score = 0.9
        elif avg_confidence >= 0.7 and diversity >= 0.6:
            quality = ReflectionQuality.GOOD
            score = 0.75
        elif avg_confidence >= 0.5:
            quality = ReflectionQuality.ACCEPTABLE
            score = 0.6
        else:
            quality = ReflectionQuality.NEEDS_IMPROVEMENT
            score = 0.4
        
        return JudgeEvaluation(
            overall_score=score,
            quality=quality,
            perspective_diversity=diversity,
            insight_depth=avg_confidence,
            actionability=avg_confidence * 0.9,
            confidence_calibration=avg_confidence,
            feedback=f"Found {len(reflections)} perspectives with {quality.value} quality.",
            improvements=["增加更多角色视角", "深化洞察分析"] if score < 0.7 else []
        )
    
    def _synthesize(
        self,
        reflections: List[Dict]
    ) -> Dict:
        """综合结论（v1兼容）"""
        return self._synthesize_v2(
            [ReflectionResult(
                persona=r.get("persona", ""),
                reflection=r.get("reflection", ""),
                confidence=r.get("confidence", 0.5),
                quality=ReflectionQuality.GOOD
            ) for r in reflections],
            None
        )
    
    def _synthesize_v2(
        self,
        reflections: List[ReflectionResult],
        evaluation: JudgeEvaluation
    ) -> Dict:
        """综合结论 v2"""
        # 收集所有洞察和建议
        all_insights = []
        all_suggestions = []
        all_concerns = []
        
        for r in reflections:
            all_insights.extend(r.insights)
            all_suggestions.extend(r.suggestions)
            all_concerns.extend(r.concerns)
        
        # 去重
        all_insights = list(dict.fromkeys(all_insights))[:5]
        all_suggestions = list(dict.fromkeys(all_suggestions))[:3]
        all_concerns = list(dict.fromkeys(all_concerns))[:3]
        
        return {
            "summary": f"综合{len(reflections)}个视角的分析",
            "key_insights": all_insights,
            "actionable_suggestions": all_suggestions,
            "concerns_to_address": all_concerns,
            "confidence": sum(r.confidence for r in reflections) / len(reflections) if reflections else 0,
            "quality": evaluation.quality.value if evaluation else "unknown",
            "overall_score": evaluation.overall_score if evaluation else 0.5
        }
    
    def get_reflection_history(self, limit: int = 10) -> List[Dict]:
        """获取反思历史"""
        return self.reflection_history[-limit:]
    
    def get_quality_trend(self) -> Dict:
        """获取质量趋势"""
        if not self.quality_tracker:
            return {"trend": "no_data", "avg_score": 0}
        
        scores = [e.overall_score for e in self.quality_tracker]
        avg_score = sum(scores) / len(scores)
        
        # 简单趋势判断
        if len(scores) >= 3:
            recent = sum(scores[-3:]) / 3
            earlier = sum(scores[:3]) / min(3, len(scores))
            if recent > earlier + 0.1:
                trend = "improving"
            elif recent < earlier - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "avg_score": round(avg_score, 2),
            "total_reflections": len(self.reflection_history),
            "quality_distribution": {
                q.value: len([e for e in self.quality_tracker if e.quality == q])
                for q in ReflectionQuality
            }
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        trend = self.get_quality_trend()
        
        return {
            "total_reflections": len(self.reflection_history),
            "avg_quality_score": trend["avg_score"],
            "quality_trend": trend["trend"],
            "available_personas": len(self.PERSONA_POOL),
            "use_real_llm": self.use_real_llm
        }


# 全局实例
_mar_v2 = None

def get_mar_v2(llm_client=None) -> MARFrameworkV2:
    """获取MAR v2实例"""
    global _mar_v2
    if _mar_v2 is None:
        _mar_v2 = MARFrameworkV2(llm_client)
    return _mar_v2

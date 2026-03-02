"""
自检Agent - 专门负责输出质量检查和自我改进
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CriticAgent:
    """
    批评者Agent - 专门找问题
    职责：
    1. 检查其他Agent输出的问题
    2. 识别逻辑漏洞、事实错误
    3. 提出改进建议
    """
    
    AGENT_NAME = "Critic"
    
    # 批评视角关键词
    CRITIC_KEYWORDS = [
        "问题", "错误", "漏洞", "缺陷", "风险",
        "不确定", "争议", "矛盾", "逻辑", "事实"
    ]
    
    def __init__(self, storage=None, llm_client=None):
        self.storage = storage
        self.llm = llm_client
        self.critique_history = []
    
    async def critique(self, target_output: str, context: str = "") -> Dict:
        """对目标输出进行批评分析"""
        
        if not self.llm:
            # 简单规则检查
            issues = self._rule_based_critique(target_output)
            return {
                "issues": issues,
                "suggestions": self._generate_suggestions(issues),
                "confidence": 0.5
            }
        
        # LLM深度分析
        prompt = f"""你是Critic Agent，专门负责找出输出中的问题。

输出内容：
{target_output}

上下文：
{context}

请分析并列出：
1. 事实性错误（如果有）
2. 逻辑漏洞（如果有）
3. 不确定的地方
4. 改进建议

返回格式：
## 问题列表
- [问题类型] 具体描述

## 改进建议
- 具体建议

## 置信度
0-1之间的数值，表示分析可靠性
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=500)
            
            # 解析结果
            issues = self._parse_critique(result)
            
            self.critique_history.append({
                "target": target_output[:100],
                "issues_count": len(issues),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "issues": issues,
                "suggestions": self._extract_suggestions(result),
                "full_analysis": result,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.warning(f"Critique failed: {e}")
            return {
                "issues": [],
                "suggestions": [],
                "confidence": 0
            }
    
    def _rule_based_critique(self, text: str) -> List[str]:
        """基于规则的简单检查"""
        issues = []
        
        # 检查过度确定性
        uncertain_phrases = ["可能", "大概", "也许", "应该"]
        for phrase in uncertain_phrases:
            if phrase in text:
                issues.append(f"表达过于确定性不足: {phrase}")
        
        # 检查绝对化表述
        absolute_phrases = ["永远", "绝对", "肯定", "100%"]
        for phrase in absolute_phrases:
            if phrase in text:
                issues.append(f"绝对化表述需谨慎: {phrase}")
        
        return issues
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """根据问题生成建议"""
        suggestions = []
        
        for issue in issues:
            if "确定性" in issue:
                suggestions.append("使用更精确的表达")
            if "绝对" in issue:
                suggestions.append("避免绝对化表述，添加适度保留")
            if "逻辑" in issue:
                suggestions.append("检查论证逻辑完整性")
        
        return suggestions
    
    def _parse_critique(self, result: str) -> List[str]:
        """解析LLM输出"""
        issues = []
        lines = result.split('\n')
        
        for line in lines:
            if '-' in line and ('错误' in line or '漏洞' in line or '问题' in line):
                issues.append(line.strip())
        
        return issues
    
    def _extract_suggestions(self, result: str) -> List[str]:
        """提取建议"""
        suggestions = []
        lines = result.split('\n')
        
        for line in lines:
            if '-' in line and ('建议' in line or '改进' in line):
                suggestions.append(line.strip())
        
        return suggestions
    
    def get_critique_stats(self) -> Dict:
        """获取批评统计"""
        return {
            "total_critiques": len(self.critique_history),
            "recent_issues_avg": sum(
                h["issues_count"] for h in self.critique_history[-10:]
            ) / min(len(self.critique_history), 10) if self.critique_history else 0
        }


# 全局实例
_critic_agent = None

def get_critic_agent(storage=None, llm_client=None) -> CriticAgent:
    """获取批评Agent"""
    global _critic_agent
    if _critic_agent is None:
        _critic_agent = CriticAgent(storage, llm_client)
    return _critic_agent


from datetime import datetime

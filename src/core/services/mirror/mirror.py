"""
Mirror模块 - 深度自诊断
实时日志分析、根因追溯、自动修复建议
"""
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(Enum):
    """问题类别"""
    FACTUAL_HALLUCINATION = "factual_hallucination"
    LOGICAL_FALLACY = "logical_fallacy"
    KNOWLEDGE_OUTDATED = "knowledge_outdated"
    TOOL_MISUSE = "tool_misuse"
    STYLE_DEVIATION = "style_deviation"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_ISSUE = "security_issue"


class RootCause:
    """根因分析结果"""
    
    def __init__(
        self,
        issue_id: str,
        category: IssueCategory,
        severity: IssueSeverity,
        description: str,
        root_cause: str,
        affected_components: List[str],
        fix_suggestions: List[Dict]
    ):
        self.id = f"rc_{issue_id}"
        self.issue_id = issue_id
        self.category = category
        self.severity = severity
        self.description = description
        self.root_cause = root_cause
        self.affected_components = affected_components
        self.fix_suggestions = fix_suggestions
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = "pending"  # pending, in_progress, fixed, ignored
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "description": self.description,
            "root_cause": self.root_cause,
            "affected_components": self.affected_components,
            "fix_suggestions": self.fix_suggestions,
            "created_at": self.created_at,
            "status": self.status
        }


class Mirror:
    """
    深度自诊断模块
    
    功能：
    1. 实时日志分析
    2. 根因追溯
    3. 自动生成修复方案
    4. 与Teacher联动生成黄金样本
    5. 系统健康报告
    """
    
    def __init__(self, llm_client=None, critic_agent=None):
        self.llm = llm_client
        self.critic = critic_agent
        self.diagnosis_history = []
        self.root_causes = []
    
    def analyze_log(self, log_entry: Dict) -> Dict:
        """
        分析日志条目
        
        Args:
            log_entry: 日志条目
            
        Returns:
            分析结果
        """
        log_type = log_entry.get("type", "unknown")
        content = log_entry.get("content", "")
        context = log_entry.get("context", "")
        
        if not self.llm:
            return self._rule_analyze(log_type, content)
        
        # LLM深度分析
        prompt = f"""你是一个系统诊断专家。请分析以下日志条目，识别问题：

日志类型：{log_type}
日志内容：{content}
上下文：{context}

请返回JSON格式的分析结果：
{{
    "issue_detected": true/false,
    "category": "问题类别",
    "severity": "critical/high/medium/low",
    "description": "问题描述",
    "root_cause": "根因分析",
    "affected_components": ["受影响的组件"],
    "fix_suggestions": [
        {{"action": "修复建议", "priority": 1-3}}
    ]
}}
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=500)
            
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # 记录诊断
                self.diagnosis_history.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "log_type": log_type,
                    "issue_detected": analysis.get("issue_detected", False),
                    "category": analysis.get("category")
                })
                
                return analysis
                
        except Exception as e:
            logger.warning(f"Analysis failed: {e}")
        
        return self._rule_analyze(log_type, content)
    
    def _rule_analyze(self, log_type: str, content: str) -> Dict:
        """规则分析（无LLM时）"""
        # 简单规则检测
        issues = []
        
        if "error" in content.lower():
            issues.append({
                "issue_detected": True,
                "category": "system_error",
                "severity": "high",
                "description": "检测到错误",
                "root_cause": "需要进一步分析",
                "affected_components": ["unknown"],
                "fix_suggestions": [{"action": "检查日志详情", "priority": 1}]
            })
        
        return issues[0] if issues else {"issue_detected": False}
    
    def diagnose_system(self, recent_logs: List[Dict]) -> List[RootCause]:
        """
        系统级诊断
        
        Args:
            recent_logs: 最近日志列表
            
        Returns:
            根因列表
        """
        issues = []
        
        # 分析每个日志
        for log in recent_logs:
            analysis = self.analyze_log(log)
            
            if analysis.get("issue_detected"):
                try:
                    category = IssueCategory(analysis.get("category", "unknown"))
                except:
                    category = IssueCategory.STYLE_DEVIATION
                
                try:
                    severity = IssueSeverity(analysis.get("severity", "low"))
                except:
                    severity = IssueSeverity.LOW
                
                rc = RootCause(
                    issue_id=f"issue_{len(self.root_causes)}",
                    category=category,
                    severity=severity,
                    description=analysis.get("description", ""),
                    root_cause=analysis.get("root_cause", ""),
                    affected_components=analysis.get("affected_components", []),
                    fix_suggestions=analysis.get("fix_suggestions", [])
                )
                
                issues.append(rc)
                self.root_causes.append(rc)
        
        return issues
    
    def generate_fix_plan(self, root_cause: RootCause) -> Dict:
        """
        生成修复计划
        
        Args:
            root_cause: 根因
            
        Returns:
            修复计划
        """
        if not self.llm:
            return {
                "plan_id": f"plan_{root_cause.id}",
                "steps": root_cause.fix_suggestions,
                "estimated_impact": "medium"
            }
        
        # LLM生成详细修复计划
        prompt = f"""请为以下问题生成详细的修复计划：

问题：{root_cause.description}
根因：{root_cause.root_cause}
影响组件：{', '.join(root_cause.affected_components)}

请生成：
1. 详细的修复步骤
2. 需要的资源
3. 预期的效果
4. 风险评估

返回JSON格式：
{{
    "plan_id": "plan_xxx",
    "steps": [
        {{"step": 1, "description": "...", "resource": "...", "risk": "low/medium/high"}}
    ],
    "estimated_impact": "high/medium/low",
    "risk_assessment": "..."
}}
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=600)
            
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            logger.warning(f"Fix plan generation failed: {e}")
        
        return {
            "plan_id": f"plan_{root_cause.id}",
            "steps": root_cause.fix_suggestions,
            "estimated_impact": "medium"
        }
    
    def link_teacher_generate_sample(self, root_cause: RootCause) -> Dict:
        """
        与Teacher联动 - 生成黄金样本
        
        Args:
            root_cause: 根因
            
        Returns:
            黄金思维链样本
        """
        # 生成日志格式错误
        error_log = {
            "type": root_cause.category.value,
            "content": root_cause.description,
            "reason": root_cause.root_cause
        }
        
        # 这里会调用Teacher模块（简化版）
        return {
            "error_log": error_log,
            "source": "mirror_diagnosis",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ready_for_teacher": True
        }
    
    def generate_health_report(self) -> Dict:
        """
        生成系统健康报告
        
        Returns:
            健康报告
        """
        # 统计
        total_issues = len(self.root_causes)
        
        by_severity = {s.value: 0 for s in IssueSeverity}
        by_category = {c.value: 0 for c in IssueCategory}
        
        for rc in self.root_causes:
            by_severity[rc.severity.value] += 1
            by_category[rc.category.value] += 1
        
        pending = sum(1 for rc in self.root_causes if rc.status == "pending")
        fixed = sum(1 for rc in self.root_causes if rc.status == "fixed")
        
        # 健康评分
        health_score = 1.0
        if total_issues > 0:
            critical_penalty = by_severity.get("critical", 0) * 0.3
            high_penalty = by_severity.get("high", 0) * 0.1
            health_score = max(0, 1.0 - critical_penalty - high_penalty)
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health_score": round(health_score, 2),
            "total_issues": total_issues,
            "by_severity": by_severity,
            "by_category": by_category,
            "pending": pending,
            "fixed": fixed,
            "fix_rate": round(fixed / max(1, total_issues), 2),
            "recommendations": self._generate_recommendations(by_severity, by_category)
        }
        
        return report
    
    def _generate_recommendations(
        self,
        by_severity: Dict,
        by_category: Dict
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if by_severity.get("critical", 0) > 0:
            recommendations.append("立即处理关键问题")
        
        if by_severity.get("high", 0) > 2:
            recommendations.append("多个高级问题需要关注")
        
        top_category = max(by_category.items(), key=lambda x: x[1])
        if top_category[1] > 0:
            recommendations.append(f"重点改进{top_category[0]}相关模块")
        
        if not recommendations:
            recommendations.append("系统运行正常")
        
        return recommendations
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_diagnoses": len(self.diagnosis_history),
            "total_root_causes": len(self.root_causes),
            "pending_issues": sum(1 for rc in self.root_causes if rc.status == "pending"),
            "fixed_issues": sum(1 for rc in self.root_causes if rc.status == "fixed")
        }


# 全局实例
_mirror = None

def get_mirror(llm_client=None, critic_agent=None) -> Mirror:
    """获取Mirror模块"""
    global _mirror
    if _mirror is None:
        _mirror = Mirror(llm_client, critic_agent)
    return _mirror

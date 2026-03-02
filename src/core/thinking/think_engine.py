"""
主动思考引擎 - 核心认知活动控制器
整合MAR框架，支持多种思考模式
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from .mar_framework import MARFramework, PersonaType

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """思考模式"""
    PASSIVE = "passive"      # 被动响应
    ACTIVE = "active"        # 主动思考
    POST_MORTEM = "post_mortem"    # 复盘反思
    FORECASTING = "forecasting"    # 前瞻预测
    ASSOCIATION = "association"    # 知识联想
    MAR_REFLECTION = "mar_reflection"  # MAR多角色反思


class ThinkEngine:
    """
    主动思考引擎
    负责管理触发、思考框架和思考结果
    整合MAR多智能体反思
    """

    def __init__(self, memory_manager=None, config: Optional[Dict] = None):
        self.logger = logging.getLogger(__name__)
        self.memory = memory_manager
        self.config = config or {}
        
        # 初始化MAR框架
        self.mar = MARFramework(config=self.config)
        
        # 思考统计
        self.stats = {
            "total_thinks": 0,
            "daily_thinks": 0,
            "last_think_date": None,
            "think_history": [],
            "mar_reflections": 0
        }
        
        # 配置
        self.target_daily_thinks = self.config.get("target_daily_thinks", 3)
        self.active_hours = self.config.get("active_hours", "09:00-18:00")

    def think(
        self,
        mode: ThinkingMode = ThinkingMode.ACTIVE,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        执行一次思考活动
        
        Args:
            mode: 思考模式
            context: 思考上下文
        
        Returns:
            思考结果
        """
        # 更新统计
        self._update_stats()
        
        context = context or {}
        
        # 根据模式选择思考框架
        if mode == ThinkingMode.POST_MORTEM:
            result = self._post_mortem_think(context)
        elif mode == ThinkingMode.FORECASTING:
            result = self._forecasting_think(context)
        elif mode == ThinkingMode.ASSOCIATION:
            result = self._association_think(context)
        elif mode == ThinkingMode.MAR_REFLECTION:
            result = self._mar_reflect(context)
        else:  # ACTIVE or PASSIVE
            result = self._comprehensive_think(context)
        
        # 记录思考结果
        self._record_thinking(result, mode)
        
        # 更新记忆中的能力
        if self.memory:
            self.memory.update_capability(
                "active_thinking",
                min(5, self.stats["total_thinks"] // 10 + 1),
                min(0.9, 0.3 + self.stats["total_thinks"] * 0.02)
            )
        
        return result

    def _post_mortem_think(self, context: Dict) -> Dict[str, Any]:
        """复盘反思：回答三个核心问题"""
        projects = context.get("projects", {})
        insights = []
        
        for project_name, project_data in projects.items():
            if project_data.get("status") == "in_progress":
                progress = project_data.get("progress", 0)
                if progress < 1.0:
                    insights.append({
                        "type": "improvement",
                        "project": project_name,
                        "content": f"{project_name}当前进度{progress*100:.0f}%，存在优化空间",
                        "action": "分析瓶颈环节"
                    })
                
                blocking = project_data.get("blocking_issues", [])
                if blocking:
                    insights.append({
                        "type": "lesson",
                        "project": project_name,
                        "content": f"{project_name}存在阻塞问题：{', '.join(blocking)}",
                        "action": "记录教训"
                    })
        
        return {
            "mode": "post_mortem",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "questions_answered": {
                "还能更好吗？": len([i for i in insights if i["type"] == "improvement"]),
                "有什么关联？": len([i for i in insights if i["type"] == "relation"]),
                "有什么教训？": len([i for i in insights if i["type"] == "lesson"])
            }
        }

    def _forecasting_think(self, context: Dict) -> Dict[str, Any]:
        """前瞻预测：回答三个核心问题"""
        projects = context.get("projects", {})
        insights = []
        
        for project_name, project_data in projects.items():
            stage = project_data.get("current_stage", "")
            
            if "Stage4" in stage:
                insights.append({
                    "type": "risk",
                    "project": project_name,
                    "content": f"{project_name}处于商业部署阶段，可能遇到部署问题",
                    "likelihood": "medium",
                    "action": "提前准备回滚方案"
                })
            
            dependencies = project_data.get("dependencies", {})
            needed = dependencies.get("needed", [])
            if needed:
                insights.append({
                    "type": "opportunity",
                    "project": project_name,
                    "content": f"{project_name}需要{needed}，可同步推进获取",
                    "action": "协调资源"
                })
        
        return {
            "mode": "forecasting",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "questions_answered": {
                "会遇到什么？": len([i for i in insights if i["type"] == "risk"]),
                "有什么机会？": len([i for i in insights if i["type"] == "opportunity"]),
                "要准备什么？": len([i for i in insights if i["type"] == "preparation"])
            }
        }

    def _association_think(self, context: Dict) -> Dict[str, Any]:
        """知识联想：回答三个核心问题"""
        memory = context.get("memory", {})
        semantic = memory.get("layers", {}).get("semantic_memory", {})
        
        insights = []
        entities = semantic.get("entities", [])
        relations = semantic.get("relations", [])
        
        for relation in relations:
            if relation.get("strength", 0) < 0.6:
                insights.append({
                    "type": "relation",
                    "from": relation.get("from"),
                    "to": relation.get("to"),
                    "content": f"{relation.get('from')}和{relation.get('to')}关联强度{relation.get('strength')}",
                    "action": "考虑加强联动"
                })
        
        projects = [e for e in entities if e.get("type") == "project"]
        technologies = [e for e in entities if e.get("type") == "technology"]
        
        for tech in technologies:
            used_count = sum(
                1 for p in projects 
                if tech.get("name") in str(p.get("attributes", {}))
            )
            if used_count == 1:
                insights.append({
                    "type": "migration",
                    "technology": tech.get("name"),
                    "content": f"{tech.get('name')}只在{projects[0].get('name')}使用",
                    "action": "考虑迁移到其他项目"
                })
        
        return {
            "mode": "association",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "questions_answered": {
                "有什么关联？": len([i for i in insights if i["type"] == "relation"]),
                "技术可迁移？": len([i for i in insights if i["type"] == "migration"]),
                "经验可借鉴？": len([i for i in insights if i["type"] == "experience"])
            }
        }

    def _mar_reflect(self, context: Dict) -> Dict[str, Any]:
        """MAR多智能体反思"""
        self.stats["mar_reflections"] += 1
        
        # 调用MAR框架
        result = self.mar.reflect(context, framework_type="mar_reflection")
        
        return {
            "mode": "mar_reflection",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mar_result": result,
            "summary": result.get("conclusion", {}).get("summary", ""),
            "confidence": result.get("conclusion", {}).get("confidence", 0.5)
        }

    def _comprehensive_think(self, context: Dict) -> Dict[str, Any]:
        """综合思考：执行所有框架"""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "comprehensive",
            "insights": []
        }
        
        # 执行三类基础思考
        pm_result = self._post_mortem_think(context)
        results["insights"].extend(pm_result.get("insights", []))
        
        fc_result = self._forecasting_think(context)
        results["insights"].extend(fc_result.get("insights", []))
        
        assoc_result = self._association_think(context)
        results["insights"].extend(assoc_result.get("insights", []))
        
        # 可选：也执行MAR
        if self.config.get("enable_mar", False):
            mar_result = self._mar_reflect(context)
            results["mar_summary"] = mar_result.get("summary")
        
        return results

    def _update_stats(self):
        """更新思考统计"""
        today = datetime.now(timezone.utc).date().isoformat()
        
        if self.stats["last_think_date"] != today:
            self.stats["daily_thinks"] = 0
        
        self.stats["total_thinks"] += 1
        self.stats["daily_thinks"] += 1
        self.stats["last_think_date"] = today

    def _record_thinking(self, result: Dict, mode: ThinkingMode):
        """记录思考结果"""
        self.stats["think_history"].append({
            "result": result,
            "mode": mode.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # 保持历史不超过100条
        if len(self.stats["think_history"]) > 100:
            self.stats["think_history"] = self.stats["think_history"][-100:]

    def get_stats(self) -> Dict[str, Any]:
        """获取思考统计"""
        return {
            **self.stats,
            "target_daily": self.target_daily_thinks,
            "target_reached": self.stats["daily_thinks"] >= self.target_daily_thinks,
            "mar_available": True
        }

    def should_think(self) -> bool:
        """判断当前是否应该思考"""
        # 检查是否达到每日目标
        if self.stats["daily_thinks"] >= self.target_daily_thinks:
            return False
        
        # 检查是否在活跃时间
        now = datetime.now()
        hour = now.hour
        start, end = self.active_hours.split("-")
        
        if not (int(start) <= hour < int(end)):
            return False
        
        return True

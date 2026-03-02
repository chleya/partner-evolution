"""
自主目标引擎 - 实现自我驱动目标
解决审查中提到的"自主目标引擎缺失"问题
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AutonomousGoalEngine:
    """
    自主目标引擎
    
    功能：
    1. 根据系统状态自动生成目标
    2. 评估目标可行性
    3. 跟踪目标进度
    4. 基于结果调整目标
    """
    
    # 探索领域
    EXPLORATION_AREAS = [
        "自我诊断能力提升",
        "记忆效率优化",
        "推理质量改进",
        "用户理解深化",
        "知识边界拓展",
        "协作能力增强",
        "安全性提升",
        "性能优化"
    ]
    
    def __init__(self, storage=None):
        self.storage = storage
        self.goals = []
        self.goal_history = []
    
    def generate_goals(self, system_state: Dict) -> List[Dict]:
        """根据系统状态自动生成目标"""
        goals = []
        
        # 分析系统状态
        belief_count = system_state.get("belief_count", 0)
        cycle_count = system_state.get("cycle_count", 0)
        avg_confidence = system_state.get("avg_confidence", 0.7)
        
        # 基于状态生成目标
        if belief_count < 10:
            goals.append(self._create_goal(
                "积累更多信念",
                "通过自省和交互增加信念数量",
                "medium"
            ))
        
        if avg_confidence > 0.9:
            goals.append(self._create_goal(
                "降低过度自信",
                "引入更多反对声音，提高思考质量",
                "high"
            ))
        
        if cycle_count % 10 == 0:
            goals.append(self._create_goal(
                "周期性自我反思",
                "进行深度自我分析，识别改进点",
                "high"
            ))
        
        # 随机探索目标
        import random
        if random.random() < 0.3:
            area = random.choice(self.EXPLORATION_AREAS)
            goals.append(self._create_goal(
                f"探索{area}",
                f"深入研究{area}相关问题",
                "low"
            ))
        
        # 保存目标
        self.goals.extend(goals)
        
        logger.info(f"Generated {len(goals)} autonomous goals")
        return goals
    
    def _create_goal(self, title: str, description: str, priority: str) -> Dict:
        """创建目标"""
        goal = {
            "id": f"auto_goal_{datetime.now(timezone.utc).timestamp()}",
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "progress": 0.0,
            "source": "autonomous"
        }
        return goal
    
    def update_progress(self, goal_id: str, progress: float):
        """更新目标进度"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["progress"] = progress
                if progress >= 1.0:
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.now(timezone.utc).isoformat()
                    self.goal_history.append(goal)
                return True
        return False
    
    def evaluate_goals(self) -> Dict:
        """评估目标状态"""
        if not self.goals:
            return {"status": "no_goals", "message": "没有活跃目标"}
        
        pending = sum(1 for g in self.goals if g["status"] == "pending")
        in_progress = sum(1 for g in self.goals if g["status"] == "in_progress")
        completed = sum(1 for g in self.goals if g["status"] == "completed")
        
        return {
            "total": len(self.goals),
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "completion_rate": completed / len(self.goals) if self.goals else 0
        }
    
    def get_active_goals(self) -> List[Dict]:
        """获取活跃目标"""
        return [g for g in self.goals if g["status"] in ["pending", "in_progress"]]


# 全局实例
_goal_engine = None

def get_autonomous_goal_engine(storage=None) -> AutonomousGoalEngine:
    """获取自主目标引擎"""
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = AutonomousGoalEngine(storage)
    return _goal_engine

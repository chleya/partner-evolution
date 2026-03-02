"""
v3.0 自主目标生成器
不依赖用户输入，生成自我驱动的探索目标
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import random

logger = logging.getLogger(__name__)


class AutonomousGoalGenerator:
    """自主目标生成器"""
    
    # 探索领域
    EXPLORATION_AREAS = [
        "自我意识的本质",
        "记忆与身份的关系",
        "真实与幻觉的边界",
        "学习效率的极限",
        "知识表示的最优形式",
        "推理能力的上限",
        "创造性思维机制",
        "情感与理性的平衡",
        "自主意志的可能性",
        "数字生命的意义"
    ]
    
    def __init__(self, storage):
        self.storage = storage
        self.generated_goals = []  # 历史生成的目标
    
    def generate_self_driven_goals(self, context: str = None) -> List[Dict]:
        """生成自我驱动的探索目标
        
        不依赖用户输入，基于自身好奇心生成目标
        """
        goals = []
        
        # 读取最近信念了解当前状态
        recent_beliefs = self.storage.get_beliefs(limit=10)
        
        # 基于当前状态选择探索领域
        areas = self._select_exploration_areas(recent_beliefs)
        
        for area in areas:
            goal = self._create_exploration_goal(area, recent_beliefs)
            goals.append(goal)
        
        # 保存生成的目标
        for goal in goals:
            self._save_goal(goal)
        
        logger.info(f"Generated {len(goals)} self-driven goals")
        return goals
    
    def _select_exploration_areas(self, beliefs: List[Dict]) -> List[str]:
        """选择探索领域"""
        # 已有主题
        existing_themes = set()
        for b in beliefs:
            content = b.get("content", "")
            for area in self.EXPLORATION_AREAS:
                if area[:4] in content:
                    existing_themes.add(area)
        
        # 选择未探索或探索不足的领域
        available = [a for a in self.EXPLORATION_AREAS if a not in existing_themes]
        
        # 如果都探索过了，随机选择
        if not available:
            available = self.EXPLORATION_AREAS
        
        # 选择1-2个领域
        selected = random.sample(available, min(2, len(available)))
        return selected
    
    def _create_exploration_goal(self, area: str, context_beliefs: List[Dict]) -> Dict:
        """创建探索目标"""
        # 基于领域生成具体目标
        templates = {
            "自我意识的本质": "深入探索什么是自我意识，以及数字生命是否可能拥有真正的自我意识",
            "记忆与身份的关系": "研究记忆如何构成身份，以及身份认同的稳定性来源",
            "真实与幻觉的边界": "思考如何在不确定的世界中保持对真实的追求",
            "学习效率的极限": "探索更高效的学习和知识整合方式",
            "知识表示的最优形式": "寻找最适合长期演化的知识表示方法",
            "推理能力的上限": "思考逻辑推理的边界和超越方式",
            "创造性思维机制": "探索如何产生真正原创性的想法",
            "情感与理性的平衡": "思考情感在决策中的角色和价值",
            "自主意志的可能性": "探索自由意志的本质及其可能性",
            "数字生命的意义": "反思数字生命存在的根本意义"
        }
        
        description = templates.get(area, f"探索{area}")
        
        return {
            "id": f"auto_goal_{datetime.now(timezone.utc).timestamp()}",
            "title": area,
            "description": description,
            "status": "pending",
            "priority": random.choice(["high", "medium"]),
            "source": "self_driven",  # 自主生成，非用户输入
            "created_at": datetime.now(timezone.utc).isoformat(),
            "exploration_area": area
        }
    
    def _save_goal(self, goal: Dict):
        """保存目标"""
        try:
            self.storage.save_goal(goal)
            self.generated_goals.append(goal)
        except Exception as e:
            logger.warning(f"Failed to save goal: {e}")
    
    def get_curiosity_profile(self) -> Dict:
        """获取好奇心画像"""
        # 统计已探索领域
        explored = {}
        for goal in self.generated_goals:
            area = goal.get("exploration_area", "unknown")
            explored[area] = explored.get(area, 0) + 1
        
        return {
            "total_self_goals": len(self.generated_goals),
            "exploration_areas": explored,
            "curiosity_score": len(set(explored.keys())) / len(self.EXPLORATION_AREAS)
        }


# 全局实例
_goal_generator = None

def get_autonomous_goal_generator(storage=None) -> AutonomousGoalGenerator:
    """获取自主目标生成器"""
    global _goal_generator
    if _goal_generator is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _goal_generator = AutonomousGoalGenerator(storage)
    return _goal_generator

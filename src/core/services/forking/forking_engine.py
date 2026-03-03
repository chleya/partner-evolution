"""
Forking Engine - 版本分叉与选择机制
实现并行进化分支管理
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class BranchType(Enum):
    """分支类型"""
    AGGRESSIVE = "aggressive"   # 激进型 - 大胆变异
    CONSERVATIVE = "conservative"  # 保守型 - 小幅优化
    EXPLORATION = "exploration"   # 探索型 - 尝试新方向


class Branch:
    """进化分支"""
    
    def __init__(
        self,
        branch_id: str,
        branch_type: BranchType,
        parent_id: str = None
    ):
        self.id = branch_id
        self.type = branch_type
        self.parent_id = parent_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_update = self.created_at
        self.generation = 0
        self.fitness = 0.0
        self.status = "active"  # active, merged, terminated
        self.mutation_strategy = self._get_strategy(branch_type)
        self.history = []
    
    def _get_strategy(self, branch_type: BranchType) -> Dict:
        """获取变异策略"""
        strategies = {
            BranchType.AGGRESSIVE: {
                "mutation_rate": 0.3,
                "accept_large_changes": True,
                "risk_tolerance": "high"
            },
            BranchType.CONSERVATIVE: {
                "mutation_rate": 0.1,
                "accept_large_changes": False,
                "risk_tolerance": "low"
            },
            BranchType.EXPLORATION: {
                "mutation_rate": 0.2,
                "accept_large_changes": True,
                "risk_tolerance": "medium",
                "try_novel_approaches": True
            }
        }
        return strategies.get(branch_type, strategies[BranchType.CONSERVATIVE])


class ForkingManager:
    """
    分叉管理器 - 并行进化核心
    
    功能：
    1. 自动创建分支
    2. 分支独立运行
    3. 适应度评估
    4. 自动选择合并
    """
    
    def __init__(self, git_manager=None, refiner=None):
        self.git = git_manager
        self.refiner = refiner
        self.branches: Dict[str, Branch] = {}
        self.main_branch = "main"
        self.active_forks = []
        self.selection_history = []
    
    def fork(
        self,
        parent_branch: str = None,
        branch_types: List[BranchType] = None
    ) -> List[Branch]:
        """
        创建分支
        
        Args:
            parent_branch: 父分支
            branch_types: 分支类型列表
            
        Returns:
            创建的分支列表
        """
        parent = parent_branch or self.main_branch
        
        if branch_types is None:
            branch_types = [
                BranchType.AGGRESSIVE,
                BranchType.CONSERVATIVE,
                BranchType.EXPLORATION
            ]
        
        created = []
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        
        for branch_type in branch_types:
            branch_id = f"fork/{branch_type.value}-{timestamp}"
            
            branch = Branch(
                branch_id=branch_id,
                branch_type=branch_type,
                parent_id=parent
            )
            
            self.branches[branch_id] = branch
            self.active_forks.append(branch_id)
            
            logger.info(f"Created branch: {branch_id} (type: {branch_type.value})")
            created.append(branch)
        
        return created
    
    def evaluate_branch(
        self,
        branch_id: str,
        metrics: Dict
    ) -> float:
        """
        评估分支适应度
        
        Args:
            branch_id: 分支ID
            metrics: 指标（性能、置信度、稳定性等）
            
        Returns:
            适应度分数 0-1
        """
        if branch_id not in self.branches:
            return 0.0
        
        branch = self.branches[branch_id]
        
        # 适应度计算
        performance = metrics.get("performance_score", 0.5)
        confidence = metrics.get("confidence_score", 0.5)
        stability = metrics.get("stability_score", 0.5)
        safety = metrics.get("safety_score", 1.0)  # 安全权重更高
        
        # 根据分支类型调整权重
        if branch.type == BranchType.AGGRESSIVE:
            weights = {"performance": 0.4, "confidence": 0.2, "stability": 0.2, "safety": 0.2}
        elif branch.type == BranchType.CONSERVATIVE:
            weights = {"performance": 0.2, "confidence": 0.3, "stability": 0.3, "safety": 0.2}
        else:  # EXPLORATION
            weights = {"performance": 0.3, "confidence": 0.3, "stability": 0.2, "safety": 0.2}
        
        fitness = (
            performance * weights["performance"] +
            confidence * weights["confidence"] +
            stability * weights["stability"] +
            safety * weights["safety"]
        )
        
        branch.fitness = fitness
        branch.last_update = datetime.now(timezone.utc).isoformat()
        
        # 记录历史
        branch.history.append({
            "timestamp": branch.last_update,
            "metrics": metrics,
            "fitness": fitness
        })
        
        return fitness
    
    def select_best_branches(
        self,
        count: int = 1
    ) -> List[Branch]:
        """
        选择最优分支
        
        Args:
            count: 选择数量
            
        Returns:
            最优分支列表
        """
        active = [self.branches[b] for b in self.active_forks]
        
        if not active:
            return []
        
        # 按适应度排序
        sorted_branches = sorted(
            active,
            key=lambda b: b.fitness,
            reverse=True
        )
        
        return sorted_branches[:count]
    
    def merge_best(
        self,
        target_branch: str = None,
        require_approval: bool = True
    ) -> Dict:
        """
        合并最优分支到主分支
        
        Args:
            target_branch: 目标分支
            require_approval: 是否需要审批
            
        Returns:
            合并结果
        """
        target = target_branch or self.main_branch
        
        # 选择最优分支
        best = self.select_best_branches(1)
        
        if not best:
            return {"success": False, "reason": "No active branches"}
        
        best_branch = best[0]
        
        # 合并逻辑（简化版）
        result = {
            "success": True,
            "merged_branch": best_branch.id,
            "target": target,
            "fitness": best_branch.fitness,
            "require_approval": require_approval,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 记录选择历史
        self.selection_history.append({
            "merged": best_branch.id,
            "fitness": best_branch.fitness,
            "timestamp": result["timestamp"]
        })
        
        # 更新状态
        best_branch.status = "merged"
        self.active_forks.remove(best_branch.id)
        
        logger.info(f"Merged {best_branch.id} -> {target} (fitness: {best_branch.fitness})")
        
        return result
    
    def terminate_branch(
        self,
        branch_id: str,
        reason: str = "low_fitness"
    ) -> bool:
        """
        终止分支
        
        Args:
            branch_id: 分支ID
            reason: 终止原因
            
        Returns:
            是否成功
        """
        if branch_id not in self.branches:
            return False
        
        branch = self.branches[branch_id]
        branch.status = "terminated"
        
        if branch_id in self.active_forks:
            self.active_forks.remove(branch_id)
        
        branch.history.append({
            "event": "terminated",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Terminated branch: {branch_id} (reason: {reason})")
        
        return True
    
    def auto_manage(self, metrics_per_branch: Dict[str, Dict]) -> Dict:
        """
        自动管理 - 评估、选择、合并
        
        Args:
            metrics_per_branch: 各分支的指标
            
        Returns:
            管理结果
        """
        results = {
            "evaluated": [],
            "merged": None,
            "terminated": [],
            "new_forks": []
        }
        
        # 1. 评估所有分支
        for branch_id, metrics in metrics_per_branch.items():
            fitness = self.evaluate_branch(branch_id, metrics)
            results["evaluated"].append({
                "branch": branch_id,
                "fitness": fitness
            })
        
        # 2. 终止低适应度分支
        for branch_id in list(self.active_forks):
            branch = self.branches[branch_id]
            if branch.fitness < 0.3:
                self.terminate_branch(branch_id, "low_fitness")
                results["terminated"].append(branch_id)
        
        # 3. 合并最优分支
        if len(self.active_forks) >= 3:
            merge_result = self.merge_best()
            results["merged"] = merge_result
            
            # 4. 创建新分支
            new_forks = self.fork()
            results["new_forks"] = [f.id for f in new_forks]
        
        return results
    
    def get_evolution_tree(self) -> Dict:
        """获取进化树"""
        return {
            "main_branch": self.main_branch,
            "total_branches": len(self.branches),
            "active_forks": self.active_forks,
            "branches": {
                bid: {
                    "type": b.type.value,
                    "parent": b.parent_id,
                    "fitness": b.fitness,
                    "status": b.status,
                    "created": b.created_at
                }
                for bid, b in self.branches.items()
            },
            "selection_history": self.selection_history[-5:]
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        active = len(self.active_forks)
        merged = sum(1 for b in self.branches.values() if b.status == "merged")
        terminated = sum(1 for b in self.branches.values() if b.status == "terminated")
        
        avg_fitness = 0
        if self.active_forks:
            avg_fitness = sum(
                self.branches[b].fitness for b in self.active_forks
            ) / active
        
        return {
            "total_branches": len(self.branches),
            "active": active,
            "merged": merged,
            "terminated": terminated,
            "avg_fitness": round(avg_fitness, 3)
        }


# 全局实例
_forking_manager = None

def get_forking_manager(
    git_manager=None,
    refiner=None
) -> ForkingManager:
    """获取Forking管理器"""
    global _forking_manager
    if _forking_manager is None:
        _forking_manager = ForkingManager(git_manager, refiner)
    return _forking_manager

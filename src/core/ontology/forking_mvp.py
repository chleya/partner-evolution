"""
v3.0 MVP - Forking Engine
版本分叉引擎
"""
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Fork:
    """版本分叉"""
    fork_id: str
    parent_version: str
    child_versions: List[str]
    fork_reason: str
    status: str  # running, completed, abandoned
    created_at: str
    best_child: Optional[str] = None


class ForkingEngineMVP:
    """Forking Engine MVP - 版本分叉引擎"""
    
    def __init__(self, genome_manager=None):
        self.genome_manager = genome_manager
        self.active_forks: Dict[str, Fork] = {}
        self.completed_forks: List[Fork] = []
    
    def create_fork(self, reason: str, num_children: int = 2) -> Fork:
        """创建版本分叉"""
        if not self.genome_manager:
            return None
        
        parent = self.genome_manager.get_current()
        parent_version = parent.get("version", "1.0.0")
        
        fork_id = f"fork_{datetime.now(timezone.utc).timestamp()}"
        
        # 创建子版本
        child_versions = []
        for i in range(num_children):
            # 变异创建子版本
            child = self.genome_manager.mutate(mutation_rate=0.2)
            child_versions.append(child.version)
        
        fork = Fork(
            fork_id=fork_id,
            parent_version=parent_version,
            child_versions=child_versions,
            fork_reason=reason,
            status="running",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.active_forks[fork_id] = fork
        
        return fork
    
    def evaluate_and_select(self, fork_id: str, test_scores: Dict[str, float]) -> str:
        """评估并选择最佳子版本"""
        if fork_id not in self.active_forks:
            return None
        
        fork = self.active_forks[fork_id]
        
        # 找到最高分
        best_version = max(test_scores, key=test_scores.get)
        fork.best_child = best_version
        fork.status = "completed"
        
        # 移动到已完成
        self.completed_forks.append(fork)
        del self.active_forks[fork_id]
        
        # 切换到最佳版本
        if self.genome_manager:
            self.genome_manager.rollback_to(best_version)
        
        return best_version
    
    def abandon_fork(self, fork_id: str):
        """放弃分叉"""
        if fork_id in self.active_forks:
            fork = self.active_forks[fork_id]
            fork.status = "abandoned"
            self.completed_forks.append(fork)
            del self.active_forks[fork_id]
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "active_forks": len(self.active_forks),
            "completed_forks": len(self.completed_forks),
            "forks": [asdict(f) for f in self.completed_forks[-5:]]
        }


# 测试
if __name__ == "__main__":
    from src.core.ontology.genome_mvp import GenomeManagerMVP
    
    # 初始化
    gm = GenomeManagerMVP()
    fe = ForkingEngineMVP(gm)
    
    print("=== Creating Fork ===")
    fork = fe.create_fork("测试分叉", num_children=2)
    print(f"Fork created: {fork.fork_id}")
    print(f"Parent: {fork.parent_version}")
    print(f"Children: {fork.child_versions}")
    
    print("\n=== Evaluating ===")
    # 模拟评分
    scores = {v: random.random() for v in fork.child_versions}
    print(f"Scores: {scores}")
    
    best = fe.evaluate_and_select(fork.fork_id, scores)
    print(f"Best version: {best}")
    
    print("\n=== Current Genome ===")
    print(gm.get_current())
    
    print("\n=== Status ===")
    print(fe.get_status())

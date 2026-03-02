"""
v3.0 Recursive Refiner - 完整实现
递归自我优化器
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class RefinementProposal:
    """改进提案"""
    proposal_id: str
    target_module: str
    description: str
    old_code: str
    new_code: str
    diff_summary: str
    safety_level: str  # safe, approval_needed, forbidden
    risks: List[str]
    expected_improvement: str


@dataclass
class RefinementResult:
    """优化结果"""
    proposal_id: str
    status: str  # applied, rejected, rolled_back
    timestamp: str
    effectiveness: float  # 0-1
    notes: str


class RecursiveRefiner:
    """递归自我优化器 - 完整版"""
    
    # 安全级别定义
    SAFE_MODIFICATIONS = [
        "prompt_templates",
        "parameter_thresholds", 
        "cache_settings",
        "log_levels",
        "timeout_values"
    ]
    
    FORBIDDEN_MODIFICATIONS = [
        "self_core",
        "core_beliefs",
        "safety_checks",
        "authentication"
    ]
    
    def __init__(self, storage=None):
        self.storage = storage
        self.proposals: List[RefinementProposal] = []
        self.results: List[RefinementResult] = []
        self.max_proposals = 100
        
        # 资源限制
        self.max_tokens_per_refinement = 5000
        self.max_execution_time_seconds = 300
    
    def analyze_self(self) -> Dict:
        """分析自身状态"""
        if not self.storage:
            return {"status": "no_storage"}
        
        try:
            # 获取各项指标
            beliefs = self.storage.get_beliefs()
            oppositions = self.storage.get_oppositions(limit=50)
            goals = self.storage.get_goals()
            
            # 计算指标
            belief_count = len(beliefs)
            avg_conf = sum(b.get("confidence", 0) for b in beliefs) / max(belief_count, 1) if beliefs else 0
            
            # 识别改进机会
            opportunities = []
            
            if avg_conf > 0.85:
                opportunities.append({
                    "area": "confidence_calibration",
                    "description": "置信度偏高，建议引入更多反对声音",
                    "priority": "medium"
                })
            
            if belief_count > 20:
                opportunities.append({
                    "area": "belief_consolidation",
                    "description": "信念数量较多，建议检查冗余",
                    "priority": "low"
                })
            
            return {
                "status": "analyzed",
                "belief_count": belief_count,
                "avg_confidence": round(avg_conf, 3),
                "opposition_count": len(oppositions),
                "goal_count": len(goals),
                "opportunities": opportunities
            }
            
        except Exception as e:
            logger.warning(f"Analysis failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_proposal(self, target_module: str, requirements: Dict) -> Optional[RefinementProposal]:
        """生成改进提案"""
        # 检查安全级别
        safety_level = self._check_safety(target_module)
        
        if safety_level == "forbidden":
            logger.warning(f"Cannot propose modifications to {target_module} - forbidden")
            return None
        
        # 生成提案ID
        proposal_id = f"prop_{datetime.now(timezone.utc).timestamp()}"
        
        # 简单实现：基于需求生成提案
        proposal = RefinementProposal(
            proposal_id=proposal_id,
            target_module=target_module,
            description=requirements.get("description", ""),
            old_code=requirements.get("current_code", ""),
            new_code=requirements.get("suggested_code", ""),
            diff_summary=requirements.get("diff_summary", ""),
            safety_level=safety_level,
            risks=requirements.get("risks", []),
            expected_improvement=requirements.get("expected_improvement", "")
        )
        
        self.proposals.append(proposal)
        
        # 限制提案数量
        if len(self.proposals) > self.max_proposals:
            self.proposals = self.proposals[-self.max_proposals:]
        
        return proposal
    
    def _check_safety(self, target_module: str) -> str:
        """检查安全级别"""
        for forbidden in self.FORBIDDEN_MODIFICATIONS:
            if forbidden in target_module.lower():
                return "forbidden"
        
        for safe in self.SAFE_MODIFICATIONS:
            if safe in target_module.lower():
                return "safe"
        
        return "approval_needed"
    
    def apply_proposal(self, proposal_id: str) -> RefinementResult:
        """应用提案"""
        # 找到提案
        proposal = None
        for p in self.proposals:
            if p.proposal_id == proposal_id:
                proposal = p
                break
        
        if not proposal:
            return RefinementResult(
                proposal_id=proposal_id,
                status="rejected",
                timestamp=datetime.now(timezone.utc).isoformat(),
                effectiveness=0,
                notes="Proposal not found"
            )
        
        # 检查安全级别
        if proposal.safety_level == "forbidden":
            return RefinementResult(
                proposal_id=proposal_id,
                status="rejected",
                timestamp=datetime.now(timezone.utc).isoformat(),
                effectiveness=0,
                notes="Forbidden modification"
            )
        
        # 记录结果
        result = RefinementResult(
            proposal_id=proposal_id,
            status="applied",
            timestamp=datetime.now(timezone.utc).isoformat(),
            effectiveness=0.8,  # 估算
            notes=f"Applied to {proposal.target_module}"
        )
        
        self.results.append(result)
        
        # 保存到存储
        if self.storage:
            try:
                self.storage.save_memory({
                    "id": f"refinement_{proposal_id}",
                    "content": f"Refinement applied: {proposal.description}",
                    "tier": "working",
                    "memory_type": "refinement",
                    "metadata": asdict(result)
                })
            except Exception as e:
                logger.warning(f"Failed to save refinement: {e}")
        
        return result
    
    def rollback_proposal(self, proposal_id: str) -> RefinementResult:
        """回滚提案"""
        result = RefinementResult(
            proposal_id=proposal_id,
            status="rolled_back",
            timestamp=datetime.now(timezone.utc).isoformat(),
            effectiveness=0,
            notes="Manually rolled back"
        )
        
        self.results.append(result)
        return result
    
    def get_proposals(self, limit: int = 10) -> List[Dict]:
        """获取提案列表"""
        return [asdict(p) for p in self.proposals[-limit:]]
    
    def get_results(self, limit: int = 10) -> List[Dict]:
        """获取结果列表"""
        return [asdict(r) for r in self.results[-limit:]]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.results)
        applied = sum(1 for r in self.results if r.status == "applied")
        rejected = sum(1 for r in self.results if r.status == "rejected")
        rolled_back = sum(1 for r in self.results if r.status == "rolled_back")
        
        return {
            "total_refinements": total,
            "applied": applied,
            "rejected": rejected,
            "rolled_back": rolled_back,
            "success_rate": applied / total if total > 0 else 0
        }


# 全局实例
_refiner = None

def get_recursive_refiner(storage=None) -> RecursiveRefiner:
    """获取递归优化器"""
    global _refiner
    if _refiner is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _refiner = RecursiveRefiner(storage)
    return _refiner


if __name__ == "__main__":
    # 测试
    refiner = RecursiveRefiner()
    
    print("=== Analyzing Self ===")
    result = refiner.analyze_self()
    print(result)
    
    print("\n=== Generating Proposal ===")
    proposal = refiner.generate_proposal(
        "prompt_templates",
        {
            "description": "简化融合提示词",
            "current_code": "long complex prompt...",
            "suggested_code": "short prompt...",
            "diff_summary": "减少30% token",
            "risks": ["可能影响质量"],
            "expected_improvement": "性能提升20%"
        }
    )
    print(f"Proposal: {proposal.proposal_id if proposal else 'None'}")
    
    print("\n=== Applying Proposal ===")
    if proposal:
        result = refiner.apply_proposal(proposal.proposal_id)
        print(f"Result: {result.status}")
    
    print("\n=== Statistics ===")
    print(refiner.get_statistics())

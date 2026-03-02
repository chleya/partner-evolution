"""
检索质量评估系统
解决 M-002 向量检索质量无法验证问题
"""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class RetrievalQualityTracker:
    """检索质量追踪器"""
    
    def __init__(self):
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "empty_results": 0,
            "low_confidence_results": 0,
            "avg_result_count": 0,
        }
        self._result_counts = []
    
    def record_query(self, query: str, results: List[Dict], threshold: float = 0.5):
        """记录检索查询结果"""
        self.stats["total_queries"] += 1
        
        # 记录结果数量
        self._result_counts.append(len(results))
        
        # 统计成功查询
        if len(results) > 0:
            self.stats["successful_queries"] += 1
        
        # 统计空结果
        if len(results) == 0:
            self.stats["empty_results"] += 1
        
        # 统计低置信度结果
        low_conf = sum(1 for r in results if r.get("score", 0) < threshold)
        if low_conf > 0:
            self.stats["low_confidence_results"] += 1
        
        # 更新平均结果数
        self.stats["avg_result_count"] = sum(self._result_counts) / len(self._result_counts)
    
    def get_quality_score(self) -> float:
        """计算检索质量分数 (0-1)"""
        if self.stats["total_queries"] == 0:
            return 1.0  # 无查询记录，默认为健康
        
        # 计算各维度得分
        success_rate = self.stats["successful_queries"] / self.stats["total_queries"]
        empty_rate = self.stats["empty_results"] / self.stats["total_queries"]
        low_conf_rate = self.stats["low_confidence_results"] / self.stats["total_queries"]
        
        # 综合得分
        quality = success_rate * 0.4 + (1 - empty_rate) * 0.3 + (1 - low_conf_rate) * 0.3
        
        return max(0.0, min(1.0, quality))
    
    def get_status(self) -> Dict:
        """获取检索状态"""
        quality = self.get_quality_score()
        
        if quality >= 0.8:
            status = "healthy"
        elif quality >= 0.5:
            status = "degraded"
        else:
            status = "critical"
        
        return {
            "status": status,
            "quality_score": round(quality, 3),
            "total_queries": self.stats["total_queries"],
            "success_rate": round(
                self.stats["successful_queries"] / max(1, self.stats["total_queries"]), 
                3
            ),
            "avg_results": round(self.stats["avg_result_count"], 1)
        }
    
    def reset(self):
        """重置统计"""
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "empty_results": 0,
            "low_confidence_results": 0,
            "avg_result_count": 0,
        }
        self._result_counts = []


# 全局实例
_quality_tracker = None

def get_retrieval_quality_tracker() -> RetrievalQualityTracker:
    """获取检索质量追踪器"""
    global _quality_tracker
    if _quality_tracker is None:
        _quality_tracker = RetrievalQualityTracker()
    return _quality_tracker

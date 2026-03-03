"""
T2: 变异引擎
基于LLM生成代码优化变体
"""
import logging
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MutationEngine:
    """
    代码变异引擎
    
    功能：
    1. 生成优化变体
    2. 多策略变异
    3. 版本管理
    """
    
    # 优化策略
    STRATEGIES = {
        "performance": {
            "description": "性能优化",
            "focus": ["时间复杂度", "空间复杂度", "缓存", "算法改进"]
        },
        "readability": {
            "description": "可读性优化", 
            "focus": ["命名规范", "注释", "代码结构", "DRY原则"]
        },
        "security": {
            "description": "安全性优化",
            "focus": ["输入验证", "异常处理", "边界检查", "权限控制"]
        },
        "maintainability": {
            "description": "可维护性优化",
            "focus": ["模块化", "解耦", "接口设计", "测试友好"]
        }
    }
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.mutation_history = []
    
    def generate_mutations(
        self,
        code: str,
        strategy: str = "performance",
        count: int = 3
    ) -> List[Dict]:
        """
        生成代码变体
        
        Args:
            code: 原始代码
            strategy: 优化策略
            count: 生成变体数量
            
        Returns:
            变体列表
        """
        if strategy not in self.STRATEGIES:
            strategy = "performance"
        
        strategy_info = self.STRATEGIES[strategy]
        
        if self.llm:
            # 使用LLM生成变体
            mutations = self._llm_generate(code, strategy_info, count)
        else:
            # 简单规则生成（演示用）
            mutations = self._rule_generate(code, strategy, count)
        
        # 记录历史
        self.mutation_history.append({
            "original": code[:100],
            "strategy": strategy,
            "count": len(mutations)
        })
        
        return mutations
    
    def _llm_generate(
        self,
        code: str,
        strategy_info: Dict,
        count: int
    ) -> List[Dict]:
        """LLM生成变体"""
        
        prompt = f"""你是一个代码优化专家。请根据以下策略优化代码。

优化策略：{strategy_info['description']}
关注点：{', '.join(strategy_info['focus'])}

原始代码：
```{code}
```

请生成{count}个优化版本，每个版本：
1. 保持功能不变
2. 应用指定的优化策略
3. 添加简短说明

返回JSON格式：
[
  {{
    "version": "1",
    "code": "优化后的代码",
    "description": "优化说明"
  }},
  ...
]
"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=1000)
            
            # 解析JSON
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                mutations = json.loads(json_match.group())
                return [
                    {
                        "version": f"v{i+1}",
                        "code": m.get("code", ""),
                        "description": m.get("description", ""),
                        "strategy": strategy_info['description']
                    }
                    for i, m in enumerate(mutations)
                ]
        except Exception as e:
            logger.warning(f"LLM mutation failed: {e}")
        
        return self._rule_generate(code, strategy_info['description'], count)
    
    def _rule_generate(
        self,
        code: str,
        strategy: str,
        count: int
    ) -> List[Dict]:
        """规则生成（简单实现）"""
        
        # 简单变体生成
        mutations = []
        
        for i in range(count):
            mutations.append({
                "version": f"v{i+1}",
                "code": code,  # 实际这里需要真正变异
                "description": f"简单变体 {i+1}",
                "strategy": strategy
            })
        
        return mutations
    
    def select_best(
        self,
        mutations: List[Dict],
        evaluation_results: List[Dict]
    ) -> Dict:
        """
        选择最佳变体
        
        Args:
            mutations: 变体列表
            evaluation_results: 评估结果
            
        Returns:
            最佳变体
        """
        if not mutations or not evaluation_results:
            return mutations[0] if mutations else None
        
        # 按评分排序
        scored = [
            (m, e.get("score", 0))
            for m, e in zip(mutations, evaluation_results)
        ]
        
        best = max(scored, key=lambda x: x[1])
        
        return {
            "mutation": best[0],
            "score": best[1],
            "rank": 1
        }
    
    def get_mutation_stats(self) -> Dict:
        """获取变异统计"""
        return {
            "total_mutations": len(self.mutation_history),
            "strategies_used": list(set(
                h["strategy"] for h in self.mutation_history
            ))
        }


# 全局实例
_mutation_engine = None

def get_mutation_engine(llm_client=None) -> MutationEngine:
    """获取变异引擎"""
    global _mutation_engine
    if _mutation_engine is None:
        _mutation_engine = MutationEngine(llm_client)
    return _mutation_engine

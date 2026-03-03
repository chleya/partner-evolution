"""
Recursive Refiner - 递归优化器主模块
整合AST解析、变异引擎、评估循环、安全沙箱
"""
import logging
from typing import Dict, List, Optional

from .ast_parser import CodeRefiner
from .mutation_engine import get_mutation_engine
from .evaluation_loop import get_evaluation_loop
from .safety_sandbox import get_safety_sandbox

logger = logging.getLogger(__name__)


class RecursiveRefiner:
    """
    递归优化器 - 核心模块
    
    工作流程：
    1. 输入原始代码
    2. AST解析
    3. 变异生成 (LLM)
    4. 评估循环
    5. 安全审查
    6. 选择最佳
    7. 重复直到收敛或达到上限
    """
    
    def __init__(self, llm_client=None):
        self.ast_refiner = CodeRefiner()
        self.mutation_engine = get_mutation_engine(llm_client)
        self.evaluation_loop = get_evaluation_loop()
        self.safety_sandbox = get_safety_sandbox()
        
        self.history = []
    
    def refine(
        self,
        code: str,
        strategy: str = "performance",
        max_iterations: int = 5
    ) -> Dict:
        """
        递归优化主流程
        
        Args:
            code: 原始代码
            strategy: 优化策略
            max_iterations: 最大迭代次数
            
        Returns:
            优化结果
        """
        # 1. 安全检查
        if self.safety_sandbox.check_stop_signal(code):
            return {
                "success": False,
                "reason": "Stop signal detected"
            }
        
        # 2. 开始进化
        self.safety_sandbox.start_evolution()
        
        current_code = code
        best_code = code
        best_score = 0.0
        iterations = 0
        
        try:
            while iterations < max_iterations:
                # 检查是否可以继续
                if not self.safety_sandbox.can_continue():
                    logger.warning("Evolution stopped by safety constraints")
                    break
                
                iterations += 1
                self.safety_sandbox.next_generation()
                
                logger.info(f"Iteration {iterations}/{max_iterations}")
                
                # 3. 生成变异
                mutations = self.mutation_engine.generate_mutations(
                    current_code,
                    strategy=strategy,
                    count=3
                )
                
                # 4. 评估变异
                evaluations = []
                for mutation in mutations:
                    eval_result = self.evaluation_loop.evaluate(
                        mutation["code"]
                    )
                    eval_result["mutation"] = mutation
                    evaluations.append(eval_result)
                
                # 5. 选择最佳
                best = self.evaluation_loop.get_best_mutation(evaluations)
                
                if best and best["score"] > best_score:
                    best_code = best["mutation"]["code"]
                    best_score = best["score"]
                    
                    logger.info(f"New best: score={best_score}")
                else:
                    # 没有改进，退出
                    logger.info("No improvement, stopping")
                    break
                
                # 6. 准备下一次迭代
                current_code = best_code
                
                # 检查停止暗号
                if self.safety_sandbox.check_stop_signal(current_code):
                    break
            
            # 6. 生成最终diff
            diff = self.ast_refiner.generate_diff(code, best_code)
            
            result = {
                "success": True,
                "original": code,
                "optimized": best_code,
                "diff": diff,
                "iterations": iterations,
                "final_score": best_score,
                "generations": self.safety_sandbox.current_generation
            }
            
            self.history.append(result)
            
            return result
            
        finally:
            self.safety_sandbox.end_evolution()
    
    def get_safety_status(self) -> Dict:
        """获取安全状态"""
        return self.safety_sandbox.get_status()
    
    def get_history(self) -> List[Dict]:
        """获取历史记录"""
        return self.history
    
    def stop(self):
        """停止进化"""
        self.safety_sandbox.state = "STOPPED"
        logger.info("Evolution stopped by user")


# 便捷函数
_refiner = None

def get_recursive_refiner(llm_client=None) -> RecursiveRefiner:
    """获取递归优化器"""
    global _refiner
    if _refiner is None:
        _refiner = RecursiveRefiner(llm_client)
    return _refiner


# 示例使用
if __name__ == "__main__":
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    refiner = RecursiveRefiner()
    result = refiner.refine(code, strategy="performance")
    
    print(f"Iterations: {result['iterations']}")
    print(f"Score: {result['final_score']}")
    print(f"Diff:\n{result['diff']}")

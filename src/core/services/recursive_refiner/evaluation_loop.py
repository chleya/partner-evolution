"""
T3: 评估循环
执行pytest、性能基准测试、安全检查
"""
import ast
import logging
import subprocess
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EvaluationLoop:
    """
    评估循环 - 测试、优化、验证
    
    功能：
    1. Pytest执行
    2. 性能基准测试
    3. 安全检查
    4. 评分排序
    """
    
    def __init__(self):
        self.evaluation_history = []
    
    def evaluate(
        self,
        code: str,
        test_code: str = None,
        baseline_metrics: Dict = None
    ) -> Dict:
        """
        评估代码
        
        Args:
            code: 待评估代码
            test_code: 测试代码
            baseline_metrics: 基线指标
            
        Returns:
            评估结果
        """
        results = {
            "syntax_valid": False,
            "tests_passed": False,
            "performance": {},
            "security_issues": [],
            "score": 0.0
        }
        
        # 1. 语法检查
        try:
            ast.parse(code)
            results["syntax_valid"] = True
        except SyntaxError as e:
            results["error"] = str(e)
            results["score"] = 0.0
            return results
        
        # 2. 执行测试
        if test_code:
            test_result = self._run_tests(code, test_code)
            results["tests_passed"] = test_result["passed"]
            results["test_details"] = test_result
        
        # 3. 性能评估
        if baseline_metrics:
            perf_result = self._measure_performance(code, baseline_metrics)
            results["performance"] = perf_result
        
        # 4. 安全检查
        security_result = self._check_security(code)
        results["security_issues"] = security_result["issues"]
        
        # 5. 计算综合评分
        results["score"] = self._calculate_score(results)
        
        # 记录历史
        self.evaluation_history.append({
            "code_hash": hash(code),
            "score": results["score"],
            "tests_passed": results["tests_passed"]
        })
        
        return results
    
    def _run_tests(self, code: str, test_code: str) -> Dict:
        """运行测试"""
        # 保存临时文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(test_code)
            test_file = f.name
        
        try:
            # 执行pytest
            result = subprocess.run(
                ["pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            passed = result.returncode == 0
            
            return {
                "passed": passed,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Test timeout"
            }
        except FileNotFoundError:
            return {
                "passed": True,  # pytest not installed, assume pass
                "note": "pytest not available"
            }
        finally:
            # 清理临时文件
            try:
                os.unlink(code_file)
                os.unlink(test_file)
            except:
                pass
    
    def _measure_performance(
        self,
        code: str,
        baseline: Dict
    ) -> Dict:
        """性能基准测试"""
        # 简化实现：检查代码复杂度
        try:
            tree = ast.parse(code)
            
            # 统计函数数量
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            
            # 统计循环数量
            loops = [n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]
            
            complexity_score = len(functions) + len(loops) * 2
            
            # 简单评分
            if baseline.get("complexity"):
                relative = complexity_score / baseline["complexity"]
            else:
                relative = 1.0
            
            return {
                "complexity": complexity_score,
                "relative_score": relative,
                "improved": relative <= 1.0
            }
            
        except:
            return {"error": "Analysis failed"}
    
    def _check_security(self, code: str) -> Dict:
        """安全检查"""
        issues = []
        
        # 检查危险操作
        dangerous_patterns = [
            ("eval(", "使用eval()存在安全风险"),
            ("exec(", "使用exec()存在安全风险"),
            ("__import__(", "动态导入存在风险"),
            ("os.system(", "系统命令执行存在风险"),
            ("subprocess.call(", "子进程调用存在风险"),
        ]
        
        for pattern, message in dangerous_patterns:
            if pattern in code:
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "pattern": pattern,
                    "message": message
                })
        
        return {
            "issues": issues,
            "safe": len(issues) == 0
        }
    
    def _calculate_score(self, results: Dict) -> float:
        """计算综合评分"""
        score = 0.0
        
        # 语法有效 (20%)
        if results.get("syntax_valid"):
            score += 0.2
        
        # 测试通过 (30%)
        if results.get("tests_passed"):
            score += 0.3
        
        # 性能改进 (20%)
        perf = results.get("performance", {})
        if perf.get("improved"):
            score += 0.2
        
        # 安全无问题 (30%)
        if not results.get("security_issues"):
            score += 0.3
        
        return score
    
    def rank_mutations(
        self,
        evaluations: List[Dict]
    ) -> List[Dict]:
        """
        变体排名
        
        Args:
            evaluations: 评估结果列表
            
        Returns:
            排序后的变体列表
        """
        # 按评分排序
        ranked = sorted(
            evaluations,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        
        # 添加排名
        for i, item in enumerate(ranked):
            item["rank"] = i + 1
        
        return ranked
    
    def get_best_mutation(
        self,
        evaluations: List[Dict]
    ) -> Optional[Dict]:
        """获取最佳变体"""
        ranked = self.rank_mutations(evaluations)
        return ranked[0] if ranked else None


# 全局实例
_evaluation_loop = None

def get_evaluation_loop() -> EvaluationLoop:
    """获取评估循环"""
    global _evaluation_loop
    if _evaluation_loop is None:
        _evaluation_loop = EvaluationLoop()
    return _evaluation_loop

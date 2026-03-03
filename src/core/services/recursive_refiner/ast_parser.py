"""
T1: AST解析与Diff模块
递归优化器的核心 - 代码解析与差异生成
"""
import ast
import difflib
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ASTParser:
    """AST解析器"""
    
    @staticmethod
    def parse(code: str) -> ast.AST:
        """解析代码为AST"""
        try:
            return ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error: {e}")
            raise
    
    @staticmethod
    def to_source(tree: ast.AST) -> str:
        """AST还原为代码"""
        try:
            return ast.unparse(tree)
        except AttributeError:
            # Python < 3.9
            import astor
            return astor.to_source(tree)
    
    @staticmethod
    def get_function_info(tree: ast.AST) -> Dict:
        """获取函数信息"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [a.arg for a in node.args.args],
                    "returns": ast.unparse(node.returns) if node.returns else None
                })
        
        return {
            "functions": functions,
            "total_functions": len(functions)
        }


class ASTDiff:
    """AST差异生成器"""
    
    @staticmethod
    def generate_diff(original: str, modified: str) -> str:
        """生成统一格式diff"""
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile='original',
            tofile='modified',
            lineterm=''
        )
        
        return ''.join(diff)
    
    @staticmethod
    def generate_line_diff(original: str, modified: str) -> List[Dict]:
        """生成行级差异"""
        d = difflib.Differ()
        result = list(d.compare(original.splitlines(), modified.splitlines()))
        
        changes = []
        for i, line in enumerate(result):
            if line.startswith('+ ') or line.startswith('- '):
                changes.append({
                    "line": i + 1,
                    "type": "added" if line.startswith('+ ') else "removed",
                    "content": line[2:]
                })
        
        return changes


class CodeRefiner:
    """代码优化器 - 整合AST解析和Diff"""
    
    def __init__(self):
        self.parser = ASTParser()
        self.diff_generator = ASTDiff()
    
    def analyze(self, code: str) -> Dict:
        """分析代码结构"""
        try:
            tree = self.parser.parse(code)
            info = self.parser.get_function_info(tree)
            
            return {
                "success": True,
                "functions": info["functions"],
                "line_count": len(code.splitlines()),
                "ast_tree": tree
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def refine(
        self,
        original_code: str,
        optimization_goal: str = "performance"
    ) -> Dict:
        """
        优化代码
        
        Args:
            original_code: 原始代码
            optimization_goal: 优化目标 (performance/readability/security)
            
        Returns:
            优化后的代码和diff
        """
        # 1. 解析原始代码
        tree = self.parser.parse(original_code)
        
        # 2. 生成优化版本 (这里先用简单实现)
        optimized = self._apply_optimizations(tree, optimization_goal)
        
        # 3. 生成diff
        diff = self.diff_generator.generate_diff(original_code, optimized)
        
        return {
            "original": original_code,
            "optimized": optimized,
            "diff": diff,
            "goal": optimization_goal
        }
    
    def _apply_optimizations(
        self,
        tree: ast.AST,
        goal: str
    ) -> str:
        """应用优化策略"""
        # 简化版：直接还原AST
        # 实际使用时，这里会调用LLM生成优化版本
        return self.parser.to_source(tree)


# 测试
if __name__ == "__main__":
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
    
    refiner = CodeRefiner()
    result = refiner.analyze(code)
    print(f"Functions found: {result['functions']}")
    
    # 测试diff
    original = "def foo():\n    return 1"
    modified = "def foo():\n    return 2"
    diff = ASTDiff.generate_diff(original, modified)
    print(f"\nDiff:\n{diff}")

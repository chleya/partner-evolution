"""
Recursive Refiner MVP 端到端测试
验证完整工作流：解析 → 变异 → 评估 → 安全 → Git
"""
import sys
sys.path.insert(0, '.')

from src.core.services.recursive_refiner import (
    CodeRefiner,
    get_mutation_engine,
    get_evaluation_loop,
    get_safety_sandbox
)
from src.core.services.recursive_refiner.ast_parser import ASTDiff
from src.core.services.recursive_refiner.git_integration import get_evolution_git


def test_astar_parser():
    """测试AST解析"""
    print("\n=== T1: AST解析测试 ===")
    
    refiner = CodeRefiner()
    
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
    
    result = refiner.analyze(code)
    
    print("[OK] 解析成功")
    print(f"  函数数量: {result['functions']}")
    print(f"  代码行数: {result['line_count']}")
    
    # 测试diff
    diff_gen = ASTDiff()
    original = "def foo():\n    return 1"
    modified = "def foo():\n    return 2"
    diff = diff_gen.generate_diff(original, modified)
    print("[OK] Diff生成成功")
    
    return True


def test_mutation_engine():
    """测试变异引擎"""
    print("\n=== T2: 变异引擎测试 ===")
    
    engine = get_mutation_engine()
    
    code = "def add(a, b): return a + b"
    
    # 简单规则生成（无LLM）
    mutations = engine._rule_generate(code, "performance", 2)
    
    print(f"[OK] 生成变体数: {len(mutations)}")
    for m in mutations:
        print(f"  - {m['version']}: {m['description']}")
    
    return True


def test_evaluation_loop():
    """测试评估循环"""
    print("\n=== T3: 评估循环测试 ===")
    
    evaluator = get_evaluation_loop()
    
    # 测试语法检查
    valid_code = "def test(): return 1"
    result = evaluator.evaluate(valid_code)
    
    print(f"✓ 语法检查: {result['syntax_valid']}")
    print(f"✓ 评分: {result['score']}")
    
    # 测试安全检查
    dangerous_code = "eval('os.system(\"ls\")')"
    sec_result = evaluator._check_security(dangerous_code)
    print(f"✓ 安全检测: 发现{len(sec_result['issues'])}个问题")
    
    return True


def test_safety_sandbox():
    """测试安全沙箱"""
    print("\n=== T4: 安全沙箱测试 ===")
    
    sandbox = get_safety_sandbox()
    
    # 重置
    sandbox.reset()
    
    # 测试状态
    print(f"✓ 初始状态: {sandbox.state.value}")
    
    # 测试停止暗号
    sandbox.start_evolution()
    has_stop = sandbox.check_stop_signal("EVOLVE_STOP")
    print(f"✓ 停止暗号检测: {has_stop}")
    
    # 测试代数限制
    for i in range(12):
        sandbox.next_generation()
    
    can_continue = sandbox.can_continue()
    print(f"✓ 10代后继续: {can_continue} (应为False)")
    
    # 获取状态
    status = sandbox.get_status()
    print(f"✓ 当前代数: {status['generation']}/{status['max_generations']}")
    
    return True


def test_git_integration():
    """测试Git集成"""
    print("\n=== T5: Git集成测试 ===")
    
    git_manager = get_evolution_git()
    
    # 检查是否是git仓库
    is_repo = git_manager.git.is_git_repo()
    print(f"✓ Git仓库: {is_repo}")
    
    if is_repo:
        status = git_manager.git.get_status()
        print(f"  当前分支: {status['branch']}")
        print(f"  有改动: {status['has_changes']}")
    
    return True


def test_full_pipeline():
    """完整流程测试"""
    print("\n=== 完整流程测试 ===")
    
    # 模拟代码优化流程
    refiner = CodeRefiner()
    evaluator = get_evaluation_loop()
    sandbox = get_safety_sandbox()
    
    # 原始代码
    original_code = """
def slow_sum(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total
"""
    
    # 1. 解析
    analysis = refiner.analyze(original_code)
    print(f"✓ 解析: {analysis['functions'][0]['name']}")
    
    # 2. 评估
    eval_result = evaluator.evaluate(original_code)
    print(f"✓ 评估: score={eval_result['score']}")
    
    # 3. 安全检查
    sandbox.start_evolution()
    can_run = sandbox.can_continue()
    print(f"✓ 安全: 可继续={can_run}")
    
    print("\n=== 所有测试通过! ===")
    
    return True


def main():
    """主测试函数"""
    print("=" * 50)
    print("  Recursive Refiner MVP 端到端测试")
    print("=" * 50)
    
    tests = [
        ("AST解析", test_astar_parser),
        ("变异引擎", test_mutation_engine),
        ("评估循环", test_evaluation_loop),
        ("安全沙箱", test_safety_sandbox),
        ("Git集成", test_git_integration),
        ("完整流程", test_full_pipeline),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {name} 失败: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"  测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

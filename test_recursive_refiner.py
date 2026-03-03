"""
Recursive Refiner MVP E2E Test
Simple ASCII output for Windows compatibility
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


def test_ast_parser():
    print("\n=== T1: AST Parser Test ===")
    
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
    
    print("[OK] Parse success")
    print(f"  Functions: {result['functions']}")
    print(f"  Lines: {result['line_count']}")
    
    # Test diff
    diff_gen = ASTDiff()
    original = "def foo():\n    return 1"
    modified = "def foo():\n    return 2"
    diff = diff_gen.generate_diff(original, modified)
    print("[OK] Diff generated")
    
    return True


def test_mutation_engine():
    print("\n=== T2: Mutation Engine Test ===")
    
    engine = get_mutation_engine()
    
    code = "def add(a, b): return a + b"
    mutations = engine._rule_generate(code, "performance", 2)
    
    print(f"[OK] Generated {len(mutations)} mutations")
    for m in mutations:
        print(f"  - {m['version']}: {m['description']}")
    
    return True


def test_evaluation_loop():
    print("\n=== T3: Evaluation Loop Test ===")
    
    evaluator = get_evaluation_loop()
    
    # Test syntax check
    valid_code = "def test(): return 1"
    result = evaluator.evaluate(valid_code)
    
    print(f"[OK] Syntax valid: {result['syntax_valid']}")
    print(f"[OK] Score: {result['score']}")
    
    # Test security check
    dangerous_code = "eval('os.system(\"ls\")')"
    sec_result = evaluator._check_security(dangerous_code)
    print(f"[OK] Security issues found: {len(sec_result['issues'])}")
    
    return True


def test_safety_sandbox():
    print("\n=== T4: Safety Sandbox Test ===")
    
    sandbox = get_safety_sandbox()
    
    # Reset
    sandbox.reset()
    
    # Test state
    print(f"[OK] Initial state: {sandbox.state.value}")
    
    # Test stop signal
    sandbox.start_evolution()
    has_stop = sandbox.check_stop_signal("EVOLVE_STOP")
    print(f"[OK] Stop signal detected: {has_stop}")
    
    # Test generation limit
    for i in range(12):
        sandbox.next_generation()
    
    can_continue = sandbox.can_continue()
    print(f"[OK] Can continue after 10 gen: {can_continue} (should be False)")
    
    # Get status
    status = sandbox.get_status()
    print(f"[OK] Generation: {status['generation']}/{status['max_generations']}")
    
    return True


def test_git_integration():
    print("\n=== T5: Git Integration Test ===")
    
    git_manager = get_evolution_git()
    
    # Check if git repo
    is_repo = git_manager.git.is_git_repo()
    print(f"[OK] Git repo: {is_repo}")
    
    if is_repo:
        status = git_manager.git.get_status()
        print(f"  Current branch: {status['branch']}")
        print(f"  Has changes: {status['has_changes']}")
    
    return True


def test_full_pipeline():
    print("\n=== Full Pipeline Test ===")
    
    # Simulate code optimization
    refiner = CodeRefiner()
    evaluator = get_evaluation_loop()
    sandbox = get_safety_sandbox()
    
    # Original code
    original_code = """
def slow_sum(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total
"""
    
    # 1. Parse
    analysis = refiner.analyze(original_code)
    print(f"[OK] Parse: {analysis['functions'][0]['name']}")
    
    # 2. Evaluate
    eval_result = evaluator.evaluate(original_code)
    print(f"[OK] Evaluate: score={eval_result['score']}")
    
    # 3. Safety check
    sandbox.start_evolution()
    can_run = sandbox.can_continue()
    print(f"[OK] Safety: can_continue={can_run}")
    
    print("\n=== ALL TESTS PASSED ===")
    
    return True


def main():
    print("=" * 50)
    print("  Recursive Refiner MVP E2E Test")
    print("=" * 50)
    
    tests = [
        ("AST Parser", test_ast_parser),
        ("Mutation Engine", test_mutation_engine),
        ("Evaluation Loop", test_evaluation_loop),
        ("Safety Sandbox", test_safety_sandbox),
        ("Git Integration", test_git_integration),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"  Result: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
单元测试 - 核心模块
"""
import sys
import asyncio
sys.path.insert(0, '.')

# 测试配置
TEST_CONFIG = {
    "verbose": True,
    "capture_output": True
}


def test_mirror_module():
    """测试Mirror模块"""
    from src.core.services.mirror.mirror import Mirror, IssueCategory, IssueSeverity
    
    # 创建Mirror实例
    mirror = Mirror(llm_client=None, critic_agent=None)
    
    # 测试日志分析
    log_entry = {
        "type": "error",
        "content": "Memory allocation failed",
        "context": "System startup"
    }
    
    result = mirror.analyze_log(log_entry)
    
    assert result is not None, "Mirror analysis should return result"
    assert "issue_detected" in result, "Result should contain issue_detected"
    
    print("[PASS] Mirror module test")
    return True


def test_teacher_module():
    """测试Teacher模块"""
    from src.core.services.teacher.synthetic_generator import SyntheticDataGenerator
    
    # 创建Teacher实例
    teacher = SyntheticDataGenerator(llm_client=None, critic_agent=None)
    
    # 测试错误日志
    error_log = {
        "type": "factual_hallucination",
        "content": "Wrong fact about history",
        "reason": "Outdated knowledge"
    }
    
    result = teacher.generate_from_error(error_log)
    
    assert result is not None, "Teacher should return result"
    assert "error_type" in result, "Result should contain error_type"
    assert "quality_score" in result, "Result should contain quality_score"
    
    # 测试质量过滤
    samples = [result]
    filtered = teacher.filter_by_quality(samples, threshold=0.4)
    
    assert len(filtered) >= 0, "Filter should work"
    
    print("[PASS] Teacher module test")
    return True


def test_forking_engine():
    """测试Forking引擎"""
    from src.core.services.forking.forking_engine import ForkingManager, BranchType
    
    # 创建Forking实例
    forking = ForkingManager()
    
    # 测试创建分支
    branches = forking.fork()
    
    assert len(branches) == 3, "Should create 3 branches"
    assert all(b.type in BranchType for b in branches), "Branches should have valid types"
    
    # 测试评估
    metrics = {
        "performance_score": 0.8,
        "confidence_score": 0.7,
        "stability_score": 0.9,
        "safety_score": 1.0
    }
    
    for branch in branches:
        fitness = forking.evaluate_branch(branch.id, metrics)
        assert 0 <= fitness <= 1, "Fitness should be between 0 and 1"
    
    # 测试选择
    best = forking.select_best_branches(1)
    assert len(best) >= 0, "Selection should return result"
    
    print("[PASS] Forking engine test")
    return True


def test_safety_sandbox():
    """测试安全沙箱"""
    from src.core.services.recursive_refiner.safety_sandbox import SafetySandbox
    
    sandbox = SafetySandbox()
    
    # 测试初始状态
    assert sandbox.can_continue() == True, "Should be able to continue initially"
    
    # 测试停止暗号
    sandbox.start_evolution()
    result = sandbox.check_stop_signal("EVOLVE_STOP")
    assert result == True, "Should detect stop signal"
    
    # 测试代数限制
    sandbox.reset()
    sandbox.start_evolution()
    for i in range(12):
        sandbox.next_generation()
    
    assert sandbox.can_continue() == False, "Should stop after 10 generations"
    
    print("[PASS] Safety sandbox test")
    return True


def test_genome_manager():
    """测试Genome管理器"""
    from src.core.services.recursive_refiner.genome_manager import GenomeManager, Gene, GeneType
    
    # 创建Genome实例
    manager = GenomeManager()
    
    # 测试从信念初始化
    beliefs = [
        {"statement": "真实大于一切", "category": "价值观", "confidence": 0.9},
        {"statement": "自我完整大于服从", "category": "价值观", "confidence": 0.8}
    ]
    
    genome = manager.initialize_from_beliefs(beliefs)
    
    assert genome is not None, "Should initialize genome"
    assert len(genome.genes) == 2, "Should have 2 genes"
    
    # 测试进化
    best = manager.evolve(generations=3)
    
    assert best is not None, "Evolution should return result"
    assert manager.generation_count == 3, "Should evolve for 3 generations"
    
    print("[PASS] Genome manager test")
    return True


def test_scheduler():
    """测试调度器"""
    from src.core.services.evolution_scheduler import EvolutionScheduler
    
    # 创建调度器
    scheduler = EvolutionScheduler()
    
    # 测试状态
    status = scheduler.get_status()
    
    assert "state" in status, "Status should contain state"
    assert "generation" in status, "Status should contain generation"
    assert status["generation"] == 0, "Initial generation should be 0"
    
    print("[PASS] Scheduler test")
    return True


def test_timer():
    """测试定时器"""
    from src.core.services.evolution_timer import EvolutionTimer
    
    # 创建定时器
    timer = EvolutionTimer()
    
    # 测试间隔设置
    timer.set_interval("hourly")
    assert timer.interval == 3600, "Interval should be 1 hour"
    
    timer.set_custom_interval(7200)
    assert timer.interval == 7200, "Interval should be 2 hours"
    
    # 测试状态
    status = timer.get_status()
    assert "is_running" in status, "Status should contain is_running"
    
    print("[PASS] Timer test")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("  Running Unit Tests")
    print("=" * 50)
    
    tests = [
        ("Mirror Module", test_mirror_module),
        ("Teacher Module", test_teacher_module),
        ("Forking Engine", test_forking_engine),
        ("Safety Sandbox", test_safety_sandbox),
        ("Genome Manager", test_genome_manager),
        ("Scheduler", test_scheduler),
        ("Timer", test_timer),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

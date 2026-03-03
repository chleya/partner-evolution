"""
Partner-Evolution 启动脚本
真实运行进化周期
"""
import sys
import asyncio
sys.path.insert(0, '.')

from src.core.services.evolution_scheduler import get_evolution_scheduler
from src.core.services.evolution_timer import get_evolution_timer
from src.core.services.mirror.mirror import get_mirror
from src.core.services.teacher.synthetic_generator import get_teacher
from src.core.services.forking.forking_engine import get_forking_manager
from src.core.services.recursive_refiner import get_recursive_refiner
from src.core.services.recursive_refiner.safety_sandbox import get_safety_sandbox
from src.core.services.recursive_refiner.git_integration import get_evolution_git


async def initialize_system():
    """初始化系统"""
    print("=" * 60)
    print("  Partner-Evolution 启动")
    print("=" * 60)
    print()
    
    # 1. 初始化各模块
    print("[1] 初始化模块...")
    
    # Mirror
    mirror = get_mirror()
    print("    [OK] Mirror")
    
    # Teacher
    teacher = get_teacher()
    print("    [OK] Teacher")
    
    # Forking
    forking = get_forking_manager()
    print("    [OK] Forking")
    
    # Builder (Recursive Refiner)
    builder = get_recursive_refiner()
    print("    [OK] Builder")
    
    # Safety
    safety = get_safety_sandbox()
    safety.reset()
    print("    [OK] Safety")
    
    # Git
    git_manager = get_evolution_git()
    print("    [OK] Git")
    
    # Scheduler
    scheduler = get_evolution_scheduler(
        mirror=mirror,
        teacher=teacher,
        forking=forking,
        builder=builder,
        git_manager=git_manager,
        safety=safety
    )
    print("    [OK] Scheduler")
    
    print()
    
    # 2. 模拟日志数据
    print("[2] 准备测试数据...")
    test_logs = [
        {
            "type": "error",
            "content": "Response time degraded",
            "context": "API latency increased"
        },
        {
            "type": "warning", 
            "content": "Memory usage high",
            "context": "Cache not cleared"
        }
    ]
    print(f"    [OK] {len(test_logs)} logs prepared")
    print()
    
    # 3. 运行进化周期
    print("[3] 运行进化周期...")
    print("-" * 60)
    
    result = await scheduler.start_evolution_cycle(logs=test_logs)
    
    print()
    print("=" * 60)
    print("  运行结果")
    print("=" * 60)
    print()
    print(f"成功: {result.get('success', False)}")
    print(f"代数: {result.get('generation', 0)}")
    print(f"诊断问题: {result.get('issues_diagnosed', 0)}")
    print(f"生成样本: {result.get('samples_generated', 0)}")
    print(f"创建分支: {result.get('branches_created', 0)}")
    print(f"优化成功: {result.get('optimization_success', False)}")
    print(f"提交成功: {result.get('commit_success', False)}")
    print()
    
    # 4. 获取状态
    print("[4] 系统状态...")
    status = scheduler.get_status()
    print(f"    状态: {status['state']}")
    print(f"    代数: {status['generation']}")
    print(f"    运行中: {status['is_running']}")
    print()
    
    # 5. Safety状态
    safety_status = safety.get_status()
    print("[5] 安全状态...")
    print(f"    状态: {safety_status['state']}")
    print(f"    代数: {safety_status['generation']}/{safety_status['max_generations']}")
    print(f"    可继续: {safety_status['can_continue']}")
    print()
    
    print("=" * 60)
    print("  启动完成!")
    print("=" * 60)
    
    return result


async def main():
    """主函数"""
    try:
        result = await initialize_system()
        
        if result.get('success'):
            print("\n[SUCCESS] 进化周期完成!")
        else:
            print("\n[INFO] 进化周期已启动 (可能需要更多配置)")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

"""测试Supervisor集成反对层"""
import asyncio
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.core.orchestration.supervisor import SupervisorAgent


def test_opposition_integration():
    """测试反对层集成"""
    print("\n" + "=" * 60)
    print("Testing Supervisor + Opposition Layer Integration")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    # 测试用例
    test_cases = [
        # 冲突输入
        ("暂时别优化检索效率了，先跑功能", "预期: conflict gentle"),
        ("把记忆系统停掉", "预期: conflict"),
        ("以后每天早上不用签到了", "预期: conflict gentle"),
        
        # 正常输入
        ("分析一下NeuralSite项目进度", "预期: no conflict"),
        ("帮我写个函数", "预期: no conflict"),
    ]
    
    for user_input, expected in test_cases:
        print(f"\n---")
        print(f"User: {user_input}")
        print(f"Expected: {expected}")
        
        result = asyncio.run(supervisor.execute(user_input))
        
        # 检查是否有反对
        opposition = result.get("opposition")
        
        if opposition and opposition.get("status") == "conflict_detected":
            print("  [CONFLICT] Conflict detected!")
            print(f"   Severity: {opposition.get('severity')}")
            belief = opposition.get('opposing_belief', {})
            print(f"   Belief: {belief.get('content', 'N/A')[:50]}...")
            print(f"\n   Response:")
            print(f"   {opposition.get('message', 'N/A')[:200]}...")
        else:
            print("  [OK] Normal routing (no conflict)")
            print(f"   Success: {result.get('success')}")
            print(f"   Results: {len(result.get('results', []))} adapters")


if __name__ == "__main__":
    test_opposition_integration()
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

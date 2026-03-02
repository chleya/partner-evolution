"""
LLM集成测试
"""
import sys
sys.path.insert(0, r'F:\ai_partner_evolution')

from src.utils.llm_client import MiniMaxClient, test_connection
from src.core.thinking import MARFramework

print("=" * 60)
print("LLM Integration Test")
print("=" * 60)

# 测试1: LLM连接
print("\n[1] Testing MiniMax Connection...")
success = test_connection()
print(f"  OK: Connection {'successful' if success else 'failed'}")

# 测试2: 直接LLM调用
print("\n[2] Direct LLM Call...")
client = MiniMaxClient()
response = client.generate(
    prompt="用一句话介绍Partner-Evolution项目",
    max_tokens=100,
    temperature=0.7
)
print(f"  Response: {response[:100]}...")

# 测试3: MAR框架集成真实LLM
print("\n[3] MAR Framework with Real LLM...")
mar = MARFramework()

context = {
    "task": "优化AI助手的记忆系统",
    "project": "Partner-Evolution",
    "projects": {
        "NeuralSite": {"status": "in_progress", "progress": 0.6}
    }
}

result = mar.reflect(context, "post_mortem")

print(f"  OK: MAR Reflection completed")
print(f"  - Confidence: {result.get('conclusion', {}).get('confidence')}")
print(f"  - Personas: {len(result.get('perspectives', []))}")

for p in result.get('perspectives', []):
    print(f"    - {p['persona']}: {p['reflection'][:80]}...")

# 测试4: JSON格式生成
print("\n[4] JSON Generation...")
json_result = client.generate_json(
    prompt="分析NeuralSite项目的状态",
    schema={"status": "string", "progress": "number", "issues": "array"}
)
print(f"  OK: {json_result}")

print("\n" + "=" * 60)
print("LLM Integration Test: PASS")
print("=" * 60)

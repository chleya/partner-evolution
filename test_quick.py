"""
Quick LLM Test - Debug
"""
import sys
import json
sys.path.insert(0, r'F:\ai_partner_evolution')

try:
    from src.utils.llm_client import MiniMaxClient
    c = MiniMaxClient()
    
    # 直接调用API
    payload = {
        "model": c.model,
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = c.session.post(
        c.base_url + "/text/chatcompletion_v2",
        json=payload,
        timeout=30
    )
    
    result_text = response.text
    
    with open(r"F:\ai_partner_evolution\test_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Status: {response.status_code}\n")
        f.write(f"Response: {result_text[:500]}")
        
    # 尝试解析
    if response.status_code == 200:
        data = json.loads(response.text)
        content = data["choices"][0]["message"]["content"]
        with open(r"F:\ai_partner_evolution\test_output.txt", "w", encoding="utf-8") as f:
            f.write(f"\n\nContent: {content}")
    
    print("Done")
except Exception as e:
    import traceback
    with open(r"F:\ai_partner_evolution\test_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}\n")
        traceback.print_exc(file=f)
    print(f"Error: {e}")

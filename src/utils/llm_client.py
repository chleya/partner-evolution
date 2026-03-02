"""
MiniMax LLM 客户端
"""
import json
import requests
from typing import Any, Dict, Optional

DEFAULT_API_KEY = "sk-cp-32X4yB3hv4uMfzdBmke7EyaxE2pXmHkAGisoBxm1bTlSnUKXcH3lGRgWYcD62Nre5AacJpbi0E5yOx92m5rkIth9HioW2aCHP5r3LeCKBuf-wdr1TVgeFxY"
DEFAULT_BASE_URL = "https://api.minimax.chat/v1"
DEFAULT_MODEL = "MiniMax-M2.5"


class MiniMaxClient:
    """MiniMax API 客户端"""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL
    ):
        self.api_key = api_key or DEFAULT_API_KEY
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/text/chatcompletion_v2",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Exception: {str(e)}"
    
    def generate_json(
        self,
        prompt: str,
        schema: Dict = None,
        system_prompt: str = None
    ) -> Dict:
        """生成JSON格式响应"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加schema要求
        schema_prompt = prompt
        if schema:
            schema_prompt += f"\n\n请按以下JSON格式返回：\n{json.dumps(schema, ensure_ascii=False)}"
        
        messages.append({"role": "user", "content": schema_prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/text/chatcompletion_v2",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 尝试解析JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"content": content, "raw": True}
            else:
                return {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            return {"error": "exception", "message": str(e)}
    
    def chat(
        self,
        messages: list,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict:
        """对话"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/text/chatcompletion_v2",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "raw": result
                }
            else:
                return {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            return {"error": "exception", "message": str(e)}


# 全局客户端
_client = None

def get_client() -> MiniMaxClient:
    """获取全局客户端"""
    global _client
    if _client is None:
        _client = MiniMaxClient()
    return _client


def test_connection() -> bool:
    """测试连接"""
    try:
        client = get_client()
        result = client.generate("你好", max_tokens=10)
        print(f"MiniMax连接测试: {result[:50]}...")
        return "Error" not in result and "Exception" not in result
    except Exception as e:
        print(f"MiniMax连接测试失败: {e}")
        return False


if __name__ == "__main__":
    test_connection()

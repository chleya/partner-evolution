"""
LLM 抽象基类 - 支持多提供商
解决PM审查中的"模型耦合度过高"问题
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLM(ABC):
    """LLM抽象基类"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass


class LLMFactory:
    """LLM工厂类 - 支持多种提供商"""
    
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_class):
        """注册提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, provider: str = "minimax", **kwargs) -> BaseLLM:
        """创建LLM实例"""
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(cls._providers.keys())}")
        
        return cls._providers[provider](**kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """列出可用提供商"""
        return list(cls._providers.keys())


# 注册默认提供商
from .minimax_client import MiniMaxClient
LLMFactory.register("minimax", MiniMaxClient)


# 便捷函数
def get_llm(provider: str = "minimax", **kwargs) -> BaseLLM:
    """获取LLM实例"""
    return LLMFactory.create(provider, **kwargs)

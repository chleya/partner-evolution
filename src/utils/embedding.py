"""
嵌入模型工具
提供文本到向量的转换功能
"""

import numpy as np
from typing import Optional

# 全局嵌入模型缓存
_embedding_model = None


def get_embedding(
    text: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    dimension: int = 384
) -> np.ndarray:
    """
    获取文本的向量表示
    
    Args:
        text: 输入文本
        model_name: 模型名称
        dimension: 向量维度
    
    Returns:
        numpy数组形式的向量
    """
    global _embedding_model
    
    # 尝试使用 sentence-transformers
    try:
        if _embedding_model is None:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(model_name)
        
        embedding = _embedding_model.encode(text)
        return embedding
        
    except ImportError:
        # 如果没有安装 sentence-transformers，返回随机向量
        # 生产环境应该安装依赖
        return np.random.randn(dimension).astype(np.float32)
    
    except Exception as e:
        # 其他错误，返回随机向量
        import logging
        logging.warning(f"Embedding generation failed: {e}, using random vector")
        return np.random.randn(dimension).astype(np.float32)


def get_embedding_dimension(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> int:
    """获取模型的标准向量维度"""
    # 常用模型的维度
    model_dimensions = {
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "openai/text-embedding-ada-002": 1536,
    }
    
    return model_dimensions.get(model_name, 384)

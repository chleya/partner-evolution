"""
向量存储 - 基于内存的向量检索实现
生产环境可替换为 pgvector 或 Chroma
版本: 2.0 - 优化版（缓存 + 批量操作 + 性能优化）
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    """
    向量存储管理器 v2.0
    支持向量添加、搜索、更新、持久化
    新增：缓存、批量操作、性能优化、健康检查
    """

    def __init__(self, dimension: int = 384, use_cache: bool = True):
        self.dimension = dimension
        self.vectors: Dict[str, tuple] = {}  # id -> (vector, metadata)
        self.index_built = False
        self._cache: Dict[str, List[Dict]] = {}  # 查询缓存
        self._cache_ttl = 300  # 缓存有效期（秒）
        
        # 健康状态标记 - 修复C-002静默失败问题
        self._is_healthy = True
        self._degradation_reason = None
        self._cache_timestamp: Dict[str, float] = {}
        self.use_cache = use_cache
        self._batch_buffer: List[tuple] = []  # 批量添加缓冲
        self._batch_size = 100
        self._search_count = 0  # 性能统计
        self._total_search_time = 0.0

    def add(self, id: str, vector: np.ndarray, metadata: Dict):
        """添加向量"""
        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension {len(vector)} does not match "
                f"expected dimension {self.dimension}"
            )
        
        # 归一化向量
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        self.vectors[id] = (vector, metadata)
        self._invalidate_cache()  # 添加新向量后清除缓存

    def add_batch(self, items: List[tuple]):
        """批量添加向量（高性能）"""
        for id, vector, metadata in items:
            if len(vector) != self.dimension:
                continue
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            self.vectors[id] = (vector, metadata)
        self._invalidate_cache()

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """向量相似度搜索（优化版本）"""
        start_time = time.time()
        
        if not self.vectors:
            return []
        
        # 归一化查询向量
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        # 构建查询键（用于缓存）
        cache_key = f"{hash(query_vector.tobytes())}_{top_k}_{threshold}"
        
        # 检查缓存
        if self.use_cache and cache_key in self._cache:
            cache_time = self._cache_timestamp.get(cache_key, 0)
            if time.time() - cache_time < self._cache_ttl:
                self._search_count += 1
                self._total_search_time += time.time() - start_time
                return self._cache[cache_key]
        
        # 预分配结果数组
        results = []
        
        # 使用批量计算优化
        if len(self.vectors) > 100:
            # 大规模数据：批量计算
            ids = list(self.vectors.keys())
            vectors = np.array([self.vectors[id][0] for id in ids])
            
            # 批量计算相似度
            similarities = np.dot(vectors, query_vector)
            
            # 排序获取top_k
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # 取2倍再过滤
            
            for idx in top_indices:
                sim = float(similarities[idx])
                if sim >= threshold:
                    results.append({
                        "id": ids[idx],
                        "similarity": sim,
                        "metadata": self.vectors[ids[idx]][1]
                    })
                if len(results) >= top_k:
                    break
        else:
            # 小规模数据：逐个计算
            for id, (vector, metadata) in self.vectors.items():
                similarity = float(np.dot(query_vector, vector))
                if similarity >= threshold:
                    results.append({
                        "id": id,
                        "similarity": similarity,
                        "metadata": metadata
                    })
        
        # 排序并返回top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:top_k]
        
        # 更新缓存
        if self.use_cache:
            self._cache[cache_key] = results
            self._cache_timestamp[cache_key] = time.time()
        
        # 性能统计
        self._search_count += 1
        self._total_search_time += time.time() - start_time
        
        return results

    def _invalidate_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_timestamp.clear()

    def get_stats(self) -> Dict:
        """获取性能统计"""
        avg_time = self._total_search_time / self._search_count if self._search_count > 0 else 0
        return {
            "total_vectors": len(self.vectors),
            "search_count": self._search_count,
            "avg_search_time_ms": avg_time * 1000,
            "cache_enabled": self.use_cache,
            "cache_size": len(self._cache)
        }
        self.index_built = False

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """向量相似度搜索（余弦相似度）"""
        if not self.vectors:
            return []
        
        # 归一化查询向量
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        results = []
        
        for id, (vector, metadata) in self.vectors.items():
            # 计算余弦相似度
            similarity = float(np.dot(query_vector, vector))
            
            if similarity >= threshold:
                results.append({
                    "id": id,
                    "similarity": similarity,
                    "metadata": metadata
                })
        
        # 排序并返回top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def update(self, id: str, vector: np.ndarray, metadata: Optional[Dict] = None):
        """更新向量"""
        if id in self.vectors:
            _, old_metadata = self.vectors[id]
            new_metadata = metadata or old_metadata
            self.vectors[id] = (vector, new_metadata)
            self.index_built = False

    def delete(self, id: str):
        """删除向量"""
        if id in self.vectors:
            del self.vectors[id]
            self.index_built = False

    def get(self, id: str) -> Optional[Dict]:
        """获取向量及其元数据"""
        if id in self.vectors:
            vector, metadata = self.vectors[id]
            return {
                "id": id,
                "vector": vector,
                "metadata": metadata
            }
        return None

    def load(self, path: str):
        """从文件加载向量索引"""
        file_path = Path(path)
        index_file = file_path / "vector_index.json"
        vectors_file = file_path / "vectors.npz"
        
        if not index_file.exists() or not vectors_file.exists():
            logger.info("No existing vector index found, starting fresh")
            return
        
        try:
            # 加载元数据
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 加载向量
            data = np.load(vectors_file)
            
            # 重建内存索引
            self.dimension = index_data.get("dimension", self.dimension)
            
            for item in index_data.get("items", []):
                id = item["id"]
                idx = item["index"]
                metadata = item["metadata"]
                
                if idx < len(data["vectors"]):
                    vector = data["vectors"][idx]
                    self.vectors[id] = (vector, metadata)
            
            self.index_built = True
            logger.info(f"Loaded {len(self.vectors)} vectors from disk")
            
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")

    def save(self, path: str):
        """保存向量索引到文件"""
        file_path = Path(path)
        file_path.mkdir(parents=True, exist_ok=True)
        
        index_file = file_path / "vector_index.json"
        vectors_file = file_path / "vectors.npz"
        
        try:
            # 准备向量数据
            vectors_list = []
            index_items = []
            
            for idx, (id, (vector, metadata)) in enumerate(self.vectors.items()):
                vectors_list.append(vector)
                index_items.append({
                    "id": id,
                    "index": idx,
                    "metadata": metadata
                })
            
            # 保存向量
            if vectors_list:
                vectors_array = np.array(vectors_list)
                np.savez(vectors_file, vectors=vectors_array)
            
            # 保存索引
            index_data = {
                "dimension": self.dimension,
                "count": len(self.vectors),
                "items": index_items
            }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(self.vectors)} vectors to disk")
            
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")

    def count(self) -> int:
        """返回向量数量"""
        return len(self.vectors)

    def clear(self):
        """清空所有向量"""
        self.vectors.clear()
        self.index_built = False
    
    # ====== 健康检查 - 修复C-002静默失败 ======
    
    def mark_degraded(self, reason: str):
        """标记服务降级"""
        self._is_healthy = False
        self._degradation_reason = reason
        logger.warning(f"VectorStore degraded: {reason}")
    
    def mark_healthy(self):
        """标记服务健康"""
        self._is_healthy = True
        self._degradation_reason = None
        logger.info("VectorStore restored to healthy state")
    
    def is_healthy(self) -> bool:
        """检查服务健康状态"""
        return self._is_healthy
    
    def get_health_status(self) -> Dict:
        """获取健康状态"""
        return {
            "healthy": self._is_healthy,
            "degradation_reason": self._degradation_reason,
            "vector_count": len(self.vectors),
            "cache_size": len(self._cache)
        }

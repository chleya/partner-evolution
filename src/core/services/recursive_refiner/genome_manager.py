"""
Genome Manager MVP - 信念基因组管理
实现信念的编码、变异、交叉、选择机制
"""
import json
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class GeneType(Enum):
    """基因类型"""
    VALUE = "value"        # 价值观基因
    PRINCIPLE = "principle"  # 原则基因
    PREFERENCE = "preference"  # 偏好基因
    IDENTITY = "identity"   # 身份基因


class Gene:
    """基因单元"""
    
    def __init__(
        self,
        gene_id: str,
        gene_type: GeneType,
        content: str,
        weight: float = 1.0,
        mutable: bool = True
    ):
        self.id = gene_id
        self.type = gene_type
        self.content = content
        self.weight = weight
        self.mutable = mutable
        self.fitness = 0.0  # 适应度
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "weight": self.weight,
            "mutable": self.mutable,
            "fitness": self.fitness
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Gene':
        gene = cls(
            gene_id=data["id"],
            gene_type=GeneType(data["type"]),
            content=data["content"],
            weight=data.get("weight", 1.0),
            mutable=data.get("mutable", True)
        )
        gene.fitness = data.get("fitness", 0.0)
        return gene


class Genome:
    """基因组 - 信念集合"""
    
    def __init__(self, genome_id: str = None):
        self.id = genome_id or f"genome_{datetime.now(timezone.utc).timestamp()}"
        self.genes: Dict[str, Gene] = {}
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.generation = 0
        self.fitness = 0.0
    
    def add_gene(self, gene: Gene):
        """添加基因"""
        self.genes[gene.id] = gene
    
    def get_genes(self, gene_type: GeneType = None) -> List[Gene]:
        """获取基因列表"""
        genes = list(self.genes.values())
        if gene_type:
            genes = [g for g in genes if g.type == gene_type]
        return genes
    
    def remove_gene(self, gene_id: str) -> bool:
        """移除基因"""
        if gene_id in self.genes:
            del self.genes[gene_id]
            return True
        return False
    
    def calculate_fitness(self) -> float:
        """计算适应度"""
        if not self.genes:
            return 0.0
        
        total = sum(g.weight * g.fitness for g in self.genes.values())
        self.fitness = total / len(self.genes)
        return self.fitness
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "genes": {k: v.to_dict() for k, v in self.genes.items()},
            "created_at": self.created_at,
            "generation": self.generation,
            "fitness": self.fitness
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Genome':
        genome = cls(data.get("id"))
        genome.created_at = data.get("created_at", datetime.now(timezone.utc).isoformat())
        genome.generation = data.get("generation", 0)
        genome.fitness = data.get("fitness", 0.0)
        
        for gid, gdata in data.get("genes", {}).items():
            genome.add_gene(Gene.from_dict(gdata))
        
        return genome


class MutationEngine:
    """基因变异引擎"""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.mutation_rate = 0.1
    
    def mutate(self, gene: Gene) -> Gene:
        """变异基因"""
        if not gene.mutable:
            return gene
        
        # 随机决定是否变异
        if random.random() > self.mutation_rate:
            return gene
        
        # 简化版：轻微修改权重
        new_weight = max(0.1, min(2.0, gene.weight + random.uniform(-0.2, 0.2)))
        gene.weight = new_weight
        
        # LLM可以进一步变异内容
        if self.llm and random.random() < 0.3:
            gene = self._llm_mutate(gene)
        
        return gene
    
    def _llm_mutate(self, gene: Gene) -> Gene:
        """LLM辅助变异"""
        # 简化实现
        return gene
    
    def mutate_genome(self, genome: Genome) -> Genome:
        """变异整个基因组"""
        new_genome = Genome()
        new_genome.generation = genome.generation + 1
        
        for gene in genome.genes.values():
            mutated = self.mutate(gene)
            new_genome.add_gene(mutated)
        
        return new_genome


class CrossoverEngine:
    """交叉引擎 - 两个基因组交换基因"""
    
    def crossover(self, genome1: Genome, genome2: Genome) -> Genome:
        """单点交叉"""
        child = Genome()
        child.generation = max(genome1.generation, genome2.generation) + 1
        
        # 合并所有基因ID
        all_genes = set(genome1.genes.keys()) | set(genome2.genes.keys())
        
        for gene_id in all_genes:
            # 随机选择父本基因
            if random.random() < 0.5:
                if gene_id in genome1.genes:
                    child.add_gene(genome1.genes[gene_id])
            else:
                if gene_id in genome2.genes:
                    child.add_gene(genome2.genes[gene_id])
        
        return child


class SelectionEngine:
    """选择引擎 - 适者生存"""
    
    def select(
        self,
        population: List[Genome],
        elite_count: int = 2
    ) -> List[Genome]:
        """精英选择"""
        # 按适应度排序
        sorted_pop = sorted(
            population,
            key=lambda g: g.calculate_fitness(),
            reverse=True
        )
        
        # 返回精英
        return sorted_pop[:elite_count]
    
    def select_parents(
        self,
        population: List[Genome],
        count: int = 2
    ) -> List[Genome]:
        """轮盘赌选择"""
        # 计算适应度
        fitnesses = [g.calculate_fitness() for g in population]
        total = sum(fitnesses)
        
        if total == 0:
            return random.sample(population, min(count, len(population)))
        
        # 轮盘赌
        selected = []
        for _ in range(count):
            r = random.random() * total
            cumsum = 0
            
            for i, f in enumerate(fitnesses):
                cumsum += f
                if cumsum >= r:
                    selected.append(population[i])
                    break
        
        return selected


class GenomeManager:
    """
    基因组管理器 - 信念进化核心
    
    工作流程：
    1. 初始化信念基因组
    2. 变异 + 交叉
    3. 评估适应度
    4. 选择 + 淘汰
    5. 迭代直到收敛
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.mutation_engine = MutationEngine(llm_client)
        self.crossover_engine = CrossoverEngine()
        self.selection_engine = SelectionEngine()
        
        self.population: List[Genome] = []
        self.best_genome: Genome = None
        self.generation_count = 0
    
    def initialize_from_beliefs(self, beliefs: List[Dict]) -> Genome:
        """从信念初始化基因组"""
        genome = Genome()
        
        for i, belief in enumerate(beliefs):
            gene_type = GeneType.PRINCIPLE
            
            # 根据类别确定基因类型
            cat = belief.get("category", "")
            if "价值观" in cat:
                gene_type = GeneType.VALUE
            elif "偏好" in cat:
                gene_type = GeneType.PREFERENCE
            
            gene = Gene(
                gene_id=f"gene_{i}",
                gene_type=gene_type,
                content=belief.get("statement", ""),
                weight=belief.get("confidence", 0.5)
            )
            
            genome.add_gene(gene)
        
        # 添加初始个体
        self.population = [genome]
        self.best_genome = genome
        
        return genome
    
    def evolve(self, generations: int = 10) -> Genome:
        """进化"""
        for _ in range(generations):
            # 1. 变异
            new_population = []
            
            for genome in self.population:
                mutated = self.mutation_engine.mutate_genome(genome)
                new_population.append(mutated)
            
            # 2. 交叉
            while len(new_population) < 20:
                parents = self.selection_engine.select_parents(self.population, 2)
                if len(parents) == 2:
                    child = self.crossover_engine.crossover(parents[0], parents[1])
                    new_population.append(child)
            
            # 3. 选择
            self.population = new_population
            elites = self.selection_engine.select(self.population, elite_count=3)
            
            # 4. 更新最佳
            if not self.best_genome or elites[0].fitness > self.best_genome.fitness:
                self.best_genome = elites[0]
            
            self.generation_count += 1
            
            logger.info(f"Generation {self.generation_count}: best fitness={self.best_genome.fitness}")
        
        return self.best_genome
    
    def get_best_genome(self) -> Optional[Genome]:
        """获取最佳基因组"""
        return self.best_genome
    
    def get_evolution_stats(self) -> Dict:
        """获取进化统计"""
        return {
            "generation_count": self.generation_count,
            "population_size": len(self.population),
            "best_fitness": self.best_genome.fitness if self.best_genome else 0,
            "best_genome_id": self.best_genome.id if self.best_genome else None
        }


# 全局实例
_genome_manager = None

def get_genome_manager(llm_client=None) -> GenomeManager:
    """获取基因组管理器"""
    global _genome_manager
    if _genome_manager is None:
        _genome_manager = GenomeManager(llm_client)
    return _genome_manager

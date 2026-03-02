"""
v3.0 数字本体层 - Genome Manager
系统的"基因"管理
"""
import json
import random
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class Gene:
    """单个基因"""
    gene_id: str
    name: str
    value: Any
    gene_type: str  # prompt/config/skill/behavior
    mutability: float  # 突变概率 (0-1)
    heritability: float  # 遗传概率 (0-1)
    description: str


@dataclass
class Genome:
    """完整基因组"""
    genome_id: str
    version: str
    genes: List[Gene] = field(default_factory=list)
    fitness_score: float = 0.0
    created_at: str = ""
    parent_genome_id: str = ""


class GenomeManager:
    """基因组管理器"""
    
    # 默认基因配置
    DEFAULT_GENES = [
        {"name": "temperature", "value": 0.7, "type": "config", "mutability": 0.3, "heredity": 0.9, "desc": "LLM温度参数"},
        {"name": "max_tokens", "value": 2000, "type": "config", "mutability": 0.2, "heredity": 0.9, "desc": "最大token数"},
        {"name": "autonomy_level", "value": 0.6, "type": "behavior", "mutability": 0.1, "heredity": 0.8, "desc": "自主程度"},
        {"name": "cycle_interval_hours", "value": 24.0, "type": "config", "mutability": 0.2, "heredity": 0.9, "desc": "自省间隔"},
        {"name": "think_mode", "value": "MAR", "type": "prompt", "mutability": 0.05, "heredity": 0.7, "desc": "思考模式"},
        {"name": "voting_threshold", "value": 0.5, "type": "behavior", "mutability": 0.1, "heredity": 0.8, "desc": "投票阈值"},
    ]
    
    def __init__(self, storage):
        self.storage = storage
        self.current_genome: Optional[Genome] = None
        self._load_or_create_genome()
    
    def _load_or_create_genome(self):
        """加载或创建基因组"""
        try:
            memories = self.storage.search_memories("genome", limit=1)
            if memories:
                data = memories[0].get("metadata", {})
                if data:
                    self.current_genome = self._dict_to_genome(data)
                    return
        except Exception as e:
            logger.warning(f"Failed to load genome: {e}")
        
        # 创建初始基因组
        self.current_genome = self.create_initial_genome()
    
    def create_initial_genome(self, config: Dict = None) -> Genome:
        """创建初始基因组"""
        now = datetime.now(timezone.utc).isoformat()
        
        genes = []
        gene_configs = config.get("genes", self.DEFAULT_GENES) if config else self.DEFAULT_GENES
        
        for gene_config in gene_configs:
            gene = Gene(
                gene_id=f"gene_{gene_config['name']}",
                name=gene_config["name"],
                value=gene_config.get("value"),
                gene_type=gene_config.get("type", "config"),
                mutability=gene_config.get("mutability", 0.1),
                heritability=gene_config.get("heredity", 0.9),
                description=gene_config.get("desc", "")
            )
            genes.append(gene)
        
        genome = Genome(
            genome_id=f"genome_{now}",
            version="1.0.0",
            genes=genes,
            created_at=now
        )
        
        self._save_genome(genome)
        self.current_genome = genome
        
        logger.info(f"Created initial genome: {genome.genome_id}")
        return genome
    
    def mutate(self, genome: Genome = None, mutation_rate: float = 0.1) -> Genome:
        """基因突变"""
        source = genome or self.current_genome
        if not source:
            return self.create_initial_genome()
        
        new_genes = []
        for gene in source.genes:
            if random.random() < mutation_rate * gene.mutability:
                # 触发突变
                mutated_value = self._mutate_gene(gene)
                new_genes.append(Gene(
                    gene_id=f"{gene.gene_id}_mut",
                    name=gene.name,
                    value=mutated_value,
                    gene_type=gene.gene_type,
                    mutability=gene.mutability * 0.9,
                    heritability=gene.heritability,
                    description=gene.description + " (mutated)"
                ))
            else:
                new_genes.append(gene)
        
        new_genome = Genome(
            genome_id=f"genome_{datetime.now(timezone.utc).timestamp()}",
            version=self._increment_version(source.version),
            genes=new_genes,
            parent_genome_id=source.genome_id,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self._save_genome(new_genome)
        return new_genome
    
    def crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """基因交叉"""
        # 简单交叉：随机选择每个基因来自哪个父母
        new_genes = []
        max_len = max(len(parent1.genes), len(parent2.genes))
        
        for i in range(max_len):
            gene = None
            if i < len(parent1.genes) and i < len(parent2.genes):
                gene = random.choice([parent1.genes[i], parent2.genes[i]])
            elif i < len(parent1.genes):
                gene = parent1.genes[i]
            else:
                gene = parent2.genes[i]
            
            new_genes.append(Gene(
                gene_id=f"{gene.gene_id}_cross",
                name=gene.name,
                value=gene.value,
                gene_type=gene.gene_type,
                mutability=gene.mutability,
                heritability=gene.heritability,
                description=gene.description
            ))
        
        new_genome = Genome(
            genome_id=f"genome_{datetime.now(timezone.utc).timestamp()}",
            version=self._increment_version(max(parent1.version, parent2.version)),
            genes=new_genes,
            parent_genome_id=f"{parent1.genome_id}+{parent2.genome_id}",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self._save_genome(new_genome)
        return new_genome
    
    def decode_to_config(self, genome: Genome = None) -> Dict:
        """将基因组解码为可执行配置"""
        source = genome or self.current_genome
        if not source:
            return {}
        
        config = {}
        for gene in source.genes:
            config[gene.name] = gene.value
        
        return config
    
    def get_gene_summary(self) -> Dict:
        """获取基因摘要"""
        if not self.current_genome:
            return {}
        
        return {
            "genome_id": self.current_genome.genome_id,
            "version": self.current_genome.version,
            "gene_count": len(self.current_genome.genes),
            "parent_id": self.current_genome.parent_genome_id,
            "fitness_score": self.current_genome.fitness_score,
            "genes": [
                {
                    "name": g.name,
                    "value": g.value,
                    "type": g.gene_type
                }
                for g in self.current_genome.genes
            ]
        }
    
    def _mutate_gene(self, gene: Gene) -> Any:
        """对基因值进行突变"""
        value = gene.value
        
        if isinstance(value, float):
            # 数值类型：小幅调整
            delta = value * 0.1 * (random.random() - 0.5)
            return max(0.0, min(1.0, value + delta))
        
        elif isinstance(value, int):
            # 整数类型：小幅调整
            delta = int(value * 0.1 * (random.random() - 0.5))
            return max(1, value + delta)
        
        elif isinstance(value, str):
            # 字符串类型：随机选择
            options = ["MAR", "CoT", "ToT", "Reflexion"]
            options = [o for o in options if o != value]
            if options:
                return random.choice(options)
        
        return value
    
    def _increment_version(self, version: str) -> str:
        """版本号自增"""
        parts = version.split(".")
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    
    def _save_genome(self, genome: Genome):
        """保存基因组"""
        try:
            memory = {
                "id": f"genome_{genome.genome_id}",
                "content": f"基因组: {genome.version}",
                "tier": "semantic",
                "memory_type": "genome",
                "metadata": asdict(genome)
            }
            self.storage.save_memory(memory)
        except Exception as e:
            logger.warning(f"Failed to save genome: {e}")
    
    def _dict_to_genome(self, data: Dict) -> Genome:
        """从字典恢复基因组"""
        genes = [Gene(**g) for g in data.get("genes", [])]
        return Genome(
            genome_id=data.get("genome_id", ""),
            version=data.get("version", "1.0.0"),
            genes=genes,
            fitness_score=data.get("fitness_score", 0.0),
            created_at=data.get("created_at", ""),
            parent_genome_id=data.get("parent_genome_id", "")
        )


# 全局实例
_genome_manager = None

def get_genome_manager(storage=None) -> GenomeManager:
    """获取基因组管理器"""
    global _genome_manager
    if _genome_manager is None:
        from src.core.storage import get_storage_manager
        storage = storage or get_storage_manager()
        _genome_manager = GenomeManager(storage)
    return _genome_manager

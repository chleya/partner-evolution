"""
v3.0 MVP - Genome Manager
最小可运行版本
"""
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional


class Genome:
    """基因组"""
    def __init__(self, genome_id: str, version: str, genes: Dict[str, any]):
        self.genome_id = genome_id
        self.version = version
        self.genes = genes
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.parent_id = ""
    
    def to_dict(self) -> Dict:
        return {
            "genome_id": self.genome_id,
            "version": self.version,
            "genes": self.genes,
            "created_at": self.created_at,
            "parent_id": self.parent_id
        }


class GenomeManagerMVP:
    """Genome Manager MVP - 基因组管理器"""
    
    # 默认基因配置
    DEFAULT_GENES = {
        "temperature": 0.7,
        "max_tokens": 2000,
        "autonomy_level": 0.6,
        "cycle_interval_hours": 24.0,
        "think_mode": "MAR",
        "voting_threshold": 0.5
    }
    
    def __init__(self, storage=None):
        self.storage = storage
        self.current_genome: Optional[Genome] = None
        self.history: List[Genome] = []
        
        # 加载或创建初始基因组
        self._load_or_create()
    
    def _load_or_create(self):
        """加载或创建基因组"""
        if self.current_genome is None:
            self.current_genome = self.create_initial()
    
    def create_initial(self) -> Genome:
        """创建初始基因组"""
        genome = Genome(
            genome_id=f"genome_{datetime.now(timezone.utc).timestamp()}",
            version="1.0.0",
            genes=self.DEFAULT_GENES.copy()
        )
        self.current_genome = genome
        self.history.append(genome)
        return genome
    
    def mutate(self, mutation_rate: float = 0.1) -> Genome:
        """基因突变"""
        if not self.current_genome:
            return self.create_initial()
        
        # 复制当前基因
        new_genes = self.current_genome.genes.copy()
        
        # 随机突变
        for key in new_genes:
            if random.random() < mutation_rate:
                if isinstance(new_genes[key], float):
                    # 小幅调整
                    new_genes[key] = max(0.0, min(1.0, new_genes[key] + random.uniform(-0.1, 0.1)))
                elif isinstance(new_genes[key], int):
                    new_genes[key] = max(1, new_genes[key] + random.randint(-100, 100))
        
        # 创建新基因组
        old_version = self.current_genome.version
        parts = old_version.split(".")
        parts[2] = str(int(parts[2]) + 1)
        new_version = ".".join(parts)
        
        new_genome = Genome(
            genome_id=f"genome_{datetime.now(timezone.utc).timestamp()}",
            version=new_version,
            genes=new_genes
        )
        new_genome.parent_id = self.current_genome.genome_id
        
        self.current_genome = new_genome
        self.history.append(new_genome)
        
        return new_genome
    
    def crossover(self, other: 'Genome') -> Genome:
        """基因交叉"""
        if not self.current_genome:
            return self.create_initial()
        
        # 随机选择每个基因
        new_genes = {}
        all_keys = set(self.current_genome.genes.keys()) | set(other.genes.keys())
        
        for key in all_keys:
            if random.random() < 0.5:
                new_genes[key] = self.current_genome.genes.get(key)
            else:
                new_genes[key] = other.genes.get(key)
        
        # 创建新基因组
        parts = self.current_genome.version.split(".")
        parts[2] = str(int(parts[2]) + 1)
        new_version = ".".join(parts)
        
        new_genome = Genome(
            genome_id=f"genome_{datetime.now(timezone.utc).timestamp()}",
            version=new_version,
            genes=new_genes
        )
        new_genome.parent_id = self.current_genome.genome_id
        
        self.current_genome = new_genome
        self.history.append(new_genome)
        
        return new_genome
    
    def get_current(self) -> Dict:
        """获取当前基因组"""
        if not self.current_genome:
            return {}
        return self.current_genome.to_dict()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史"""
        return [g.to_dict() for g in self.history[-limit:]]
    
    def rollback_to(self, version: str) -> bool:
        """回滚到指定版本"""
        for g in self.history:
            if g.version == version:
                self.current_genome = g
                return True
        return False


# 测试
if __name__ == "__main__":
    gm = GenomeManagerMVP()
    
    print("=== Initial Genome ===")
    print(gm.get_current())
    
    print("\n=== After Mutation ===")
    gm.mutate(0.2)
    print(gm.get_current())
    
    print("\n=== History ===")
    for h in gm.get_history():
        print(f"  {h['version']}: {h['genes']}")

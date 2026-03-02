"""
v3.0 Ontology API - 身份与基因组管理
"""
from flask import Blueprint, jsonify

ontology_bp = Blueprint('ontology', __name__, url_prefix='/api/v3/ontology')


@ontology_bp.route('/identity', methods=['GET'])
def get_identity():
    """获取系统身份"""
    from src.core.ontology.identity import get_identity_manager
    
    manager = get_identity_manager()
    identity = manager.get_identity_summary()
    
    return jsonify(identity)


@ontology_bp.route('/identity/initialize', methods=['POST'])
def init_identity():
    """初始化系统身份"""
    from src.core.ontology.identity import get_identity_manager
    
    manager = get_identity_manager()
    identity = manager.initialize_identity()
    
    return jsonify({
        "status": "initialized",
        "identity": manager.get_identity_summary()
    })


@ontology_bp.route('/identity/evolve', methods=['POST'])
def evolve_identity():
    """演化系统身份"""
    from src.core.ontology.identity import get_identity_manager
    
    manager = get_identity_manager()
    
    # 从请求获取经验数据
    from flask import request
    data = request.json or {}
    experience = {
        "belief_count": data.get("belief_count", 0),
        "avg_confidence": data.get("avg_confidence", 0.7),
        "opposition_count": data.get("opposition_count", 0)
    }
    
    identity = manager.reflect_and_evolve(experience)
    
    return jsonify({
        "status": "evolved",
        "identity": manager.get_identity_summary()
    })


@ontology_bp.route('/genome', methods=['GET'])
def get_genome():
    """获取当前基因组"""
    from src.core.ontology.genome import get_genome_manager
    
    manager = get_genome_manager()
    genome = manager.get_gene_summary()
    
    return jsonify(genome)


@ontology_bp.route('/genome/config', methods=['GET'])
def get_genome_config():
    """获取解码后的配置"""
    from src.core.ontology.genome import get_genome_manager
    
    manager = get_genome_manager()
    config = manager.decode_to_config()
    
    return jsonify(config)


@ontology_bp.route('/genome/mutate', methods=['POST'])
def mutate_genome():
    """触发基因突变"""
    from src.core.ontology.genome import get_genome_manager
    
    manager = get_genome_manager()
    
    from flask import request
    data = request.json or {}
    rate = data.get("mutation_rate", 0.1)
    
    new_genome = manager.mutate(mutation_rate=rate)
    
    return jsonify({
        "status": "mutated",
        "old_version": manager.current_genome.version,
        "new_version": new_genome.version,
        "new_genome_id": new_genome.genome_id
    })


@ontology_bp.route('/genome/summary', methods=['GET'])
def genome_summary():
    """获取基因组摘要"""
    from src.core.ontology.genome import get_genome_manager
    
    manager = get_genome_manager()
    
    return jsonify({
        "current_version": manager.current_genome.version if manager.current_genome else "none",
        "gene_count": len(manager.current_genome.genes) if manager.current_genome else 0,
        "parent_id": manager.current_genome.parent_genome_id if manager.current_genome else "none",
        "genes": [
            {
                "name": g.name,
                "value": g.value,
                "type": g.gene_type,
                "mutability": g.mutability
            }
            for g in manager.current_genome.genes
        ] if manager.current_genome else []
    })

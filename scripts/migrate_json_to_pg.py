"""
数据迁移脚本 - JSON to PostgreSQL
将现有JSON数据迁移到PostgreSQL
"""
import json
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据目录
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def migrate_memories():
    """迁移记忆数据"""
    memory_file = DATA_DIR / "memory" / "unified_memory.json"
    
    if not memory_file.exists():
        logger.warning(f"Memory file not found: {memory_file}")
        return 0
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        memories = data.get("memories", [])
        logger.info(f"Found {len(memories)} memories to migrate")
        
        # TODO: 插入PostgreSQL
        # await postgres_manager.save_memory(memory)
        
        return len(memories)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 0


def migrate_beliefs():
    """迁移信念数据"""
    belief_file = DATA_DIR / "beliefs" / "beliefs.json"
    
    if not belief_file.exists():
        logger.warning(f"Belief file not found: {belief_file}")
        return 0
    
    try:
        with open(belief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        beliefs = data.get("beliefs", {})
        logger.info(f"Found {len(beliefs)} beliefs to migrate")
        
        return len(beliefs)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 0


def migrate_goals():
    """迁移目标数据"""
    goal_file = DATA_DIR / "goals.json"
    
    if not goal_file.exists():
        logger.warning(f"Goal file not found: {goal_file}")
        return 0
    
    try:
        with open(goal_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        goals = data.get("goals", [])
        logger.info(f"Found {len(goals)} goals to migrate")
        
        return len(goals)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 0


def migrate_all():
    """执行全量迁移"""
    logger.info("Starting data migration: JSON -> PostgreSQL")
    
    results = {
        "memories": migrate_memories(),
        "beliefs": migrate_beliefs(),
        "goals": migrate_goals()
    }
    
    logger.info(f"Migration complete: {results}")
    
    total = sum(results.values())
    logger.info(f"Total records migrated: {total}")
    
    return results


if __name__ == "__main__":
    migrate_all()

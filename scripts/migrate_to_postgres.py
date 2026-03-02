#!/usr/bin/env python3
"""
数据迁移脚本：将JSON数据迁移到PostgreSQL/JSON存储
用法: python scripts/migrate_to_postgres.py
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.storage import get_storage_manager


def load_json(file_path: str) -> dict:
    """加载JSON文件"""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  警告：加载 {file_path} 失败: {e}")
        return {}


def migrate_memories(storage):
    """迁移记忆数据"""
    print("\n[1] 迁移记忆数据...")
    
    source_file = "data/memory/unified_memory.json"
    data = load_json(source_file)
    
    if not data:
        print(f"  跳过：{source_file} 不存在")
        return 0
    
    total_imported = 0
    
    # 处理 raw_memory.conversations
    layers = data.get("layers", {})
    raw_memory = layers.get("raw_memory", {})
    conversations = raw_memory.get("conversations", [])
    print(f"  找到 {len(conversations)} 条对话记忆")
    
    for conv in conversations:
        success = storage.save_memory({
            "id": conv.get("id", f"conv_{total_imported}"),
            "tier": conv.get("tier", "recall"),
            "type": "conversation",
            "content": conv.get("content", ""),
            "confidence": conv.get("confidence", conv.get("quality_score", 0.5)),
            "importance": conv.get("quality_score", 0.5),
            "metadata": {
                "user": conv.get("user"),
                "intent": conv.get("intent"),
                "outcome": conv.get("outcome"),
                "timestamp": conv.get("timestamp")
            }
        })
        if success:
            total_imported += 1
    
    # 处理 raw_memory.task_records
    task_records = raw_memory.get("task_records", [])
    print(f"  找到 {len(task_records)} 条任务记录")
    
    for task in task_records:
        success = storage.save_memory({
            "id": task.get("id", f"task_{total_imported}"),
            "tier": task.get("tier", "core"),
            "type": "task",
            "content": task.get("description", ""),
            "confidence": 0.8,
            "importance": 0.8,
            "metadata": {
                "project": task.get("project"),
                "status": task.get("status"),
                "progress": task.get("progress"),
                "started_at": task.get("started_at"),
                "blocking_issues": task.get("blocking_issues", [])
            }
        })
        if success:
            total_imported += 1
    
    # 处理 semantic_memory.entities
    semantic_memory = layers.get("semantic_memory", {})
    entities = semantic_memory.get("entities", [])
    print(f"  找到 {len(entities)} 个实体")
    
    for entity in entities:
        success = storage.save_memory({
            "id": entity.get("id", f"entity_{total_imported}"),
            "tier": entity.get("tier", "core"),
            "type": "entity",
            "content": f"{entity.get('name', '')} ({entity.get('type', '')})",
            "confidence": entity.get("confidence", 0.5),
            "importance": 0.7,
            "metadata": {
                "name": entity.get("name"),
                "entity_type": entity.get("type"),
                "aliases": entity.get("aliases", []),
                "attributes": entity.get("attributes", {})
            }
        })
        if success:
            total_imported += 1
    
    # 处理 semantic_memory.relations
    relations = semantic_memory.get("relations", [])
    print(f"  找到 {len(relations)} 条关系")
    
    for rel in relations:
        success = storage.save_memory({
            "id": f"rel_{total_imported}",
            "tier": "core",
            "type": "relation",
            "content": f"{rel.get('from', '')} --[{rel.get('type', '')}]--> {rel.get('to', '')}",
            "confidence": rel.get("strength", 0.5),
            "importance": 0.6,
            "metadata": {
                "from": rel.get("from"),
                "to": rel.get("to"),
                "relation_type": rel.get("type"),
                "description": rel.get("description")
            }
        })
        if success:
            total_imported += 1
    
    # 处理 meta_cognition
    meta_cognition = layers.get("meta_cognition", {})
    capabilities = meta_cognition.get("capabilities", {})
    
    for cap_name, cap_data in capabilities.items():
        success = storage.save_memory({
            "id": f"cap_{cap_name}",
            "tier": "core",
            "type": "capability",
            "content": f"能力: {cap_name}",
            "confidence": cap_data.get("confidence", 0.5),
            "importance": 0.8,
            "metadata": {
                "capability": cap_name,
                "level": cap_data.get("level"),
                "last_used": cap_data.get("last_used")
            }
        })
        if success:
            total_imported += 1
    
    print(f"  已导入 {total_imported} 条记忆")
    return total_imported


def migrate_goals(storage):
    """迁移目标数据"""
    print("\n[2] 检查目标数据...")
    
    # 检查是否有预存目标
    default_goals = [
        {
            "id": "goal_001",
            "title": "完成v2.1存储层升级",
            "description": "实现PostgreSQL存储 + 自动降级",
            "type": "optimization",
            "priority": 1,
            "status": "in_progress",
            "horizon": "short",
            "progress": 60.0
        },
        {
            "id": "goal_002", 
            "title": "实现Pure Autonomous Cycle",
            "description": "让系统在无人交互时也能自省并形成主张",
            "type": "exploration",
            "priority": 2,
            "status": "pending",
            "horizon": "medium",
            "progress": 0.0
        }
    ]
    
    imported = 0
    for goal in default_goals:
        success = storage.save_goal(goal)
        if success:
            imported += 1
    
    print(f"  已导入 {imported} 个目标")
    return imported


def show_stats(storage):
    """显示统计信息"""
    print("\n[3] 存储统计...")
    
    stats = storage.get_memory_stats()
    print(f"  总记忆数: {stats['total']}")
    
    for tier, info in stats.get('by_tier', {}).items():
        print(f"  - {tier}: {info['count']} 条 (平均置信度: {info.get('avg_confidence', 0):.2f})")
    
    # 信念统计
    beliefs = storage.get_beliefs()
    print(f"  总信念数: {len(beliefs)}")
    
    # 目标统计
    goals = storage.get_goals()
    print(f"  总目标数: {len(goals)}")
    if goals:
        print("  目标列表:")
        for g in goals[:5]:
            print(f"    - {g.get('title', 'Untitled')}: {g.get('status', 'unknown')} ({g.get('progress', 0)}%)")


def main():
    print("=" * 60)
    print("Partner-Evolution 数据迁移工具")
    print("=" * 60)
    
    # 检查存储模式
    storage = get_storage_manager()
    
    if storage.use_db:
        print("\n存储模式: PostgreSQL")
    else:
        print("\n存储模式: JSON (PostgreSQL不可用，使用JSON)")
    
    # 迁移数据
    memories_count = migrate_memories(storage)
    goals_count = migrate_goals(storage)
    
    # 显示统计
    show_stats(storage)
    
    print("\n" + "=" * 60)
    print(f"迁移完成! 共导入 {memories_count} 条记忆, {goals_count} 个目标")
    print("=" * 60)
    
    print("\n提示：")
    print("  - 系统会自动探测PostgreSQL可用性并降级")
    print("  - 日志中会显示当前使用的存储模式")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
数据迁移脚本：将JSON数据迁移到PostgreSQL
用法: python scripts/migrate_to_postgres.py
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.storage import get_storage_manager


def load_json(file_path: str) -> list:
    """加载JSON文件"""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"  警告：加载 {file_path} 失败: {e}")
        return []


def migrate_memories(storage):
    """迁移记忆数据"""
    print("\n[1] 迁移记忆数据...")
    
    # 源文件
    source_files = [
        "data/memory/unified_memory.json",
    ]
    
    total_imported = 0
    
    for source_file in source_files:
        if not os.path.exists(source_file):
            print(f"  跳过：{source_file} 不存在")
            continue
        
        memories = load_json(source_file)
        print(f"  找到 {len(memories)} 条记忆")
        
        for memory in memories:
            success = storage.save_memory({
                "id": memory.get("id", f"migrated_{total_imported}"),
                "tier": memory.get("tier", "recall"),
                "type": memory.get("type", memory.get("memory_type", "general")),
                "content": memory.get("content", ""),
                "confidence": memory.get("confidence", 1.0),
                "importance": memory.get("importance", 0.5),
                "metadata": memory.get("metadata", {})
            })
            if success:
                total_imported += 1
        
        print(f"  已导入 {total_imported} 条记忆")
    
    return total_imported


def migrate_goals(storage):
    """迁移目标数据"""
    print("\n[2] 检查目标数据...")
    
    # 检查是否有目标数据
    goals_file = "data/goals.json"
    goals = load_json(goals_file)
    
    if not goals:
        print("  跳过：无目标数据")
        return 0
    
    imported = 0
    for goal in goals:
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


def main():
    print("=" * 60)
    print("Partner-Evolution 数据迁移工具")
    print("=" * 60)
    
    # 检查存储模式
    storage = get_storage_manager()
    
    if storage.use_db:
        print("\n存储模式: PostgreSQL")
    else:
        print("\n存储模式: JSON (PostgreSQL不可用)")
    
    # 迁移数据
    memories_count = migrate_memories(storage)
    goals_count = migrate_goals(storage)
    
    # 显示统计
    show_stats(storage)
    
    print("\n" + "=" * 60)
    print(f"迁移完成! 共导入 {memories_count} 条记忆, {goals_count} 个目标")
    print("=" * 60)
    
    print("\n提示：")
    print("  - 如需使用PostgreSQL，设置环境变量: USE_DB=true")
    print("  - 或配置DB_HOST, DB_PASSWORD等参数")
    print("  - 详细配置见 schema.sql")


if __name__ == "__main__":
    main()

"""
语义加工层 - 负责实体的语义加工和关联建立
"""

from typing import Any, Dict, List


class SemanticLayer:
    """语义加工层"""
    
    # 预定义的实体类型和它们的典型属性
    ENTITY_TYPE_TEMPLATES = {
        "project": ["location", "status", "stage", "github"],
        "person": ["role", "organization", "expertise"],
        "concept": ["definition", "source", "origin_date"],
        "technology": ["language", "framework", "version"],
        "task": ["status", "priority", "deadline"]
    }

    # 预定义的关联类型
    RELATION_TYPES = [
        "depends_on",
        "collaborates_with",
        "provides_to",
        "requires",
        "similar_to",
        "contradicts"
    ]

    def auto_link(
        self,
        new_entity: Dict[str, Any],
        existing_memory: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        自动建立新实体与现有实体的关联
        返回新建的关联列表
        """
        links = []
        new_type = new_entity.get("type")
        new_name = new_entity.get("name")

        # 根据类型匹配建立关联
        for entity in existing_memory.get("entities", []):
            if entity["id"] == new_entity.get("id"):
                continue

            # 项目之间的协作关联
            if new_type == "project" and entity.get("type") == "project":
                if self._check_potential_collaboration(new_entity, entity):
                    links.append({
                        "from": new_name,
                        "to": entity["name"],
                        "type": "collaborates_with",
                        "description": "潜在协作关系",
                        "strength": 0.5,
                        "auto_generated": True
                    })

            # 技术与项目的关联
            elif new_type == "technology" and entity.get("type") == "project":
                if self._check_tech_usage(new_entity, entity):
                    links.append({
                        "from": entity["name"],
                        "to": new_name,
                        "type": "uses",
                        "description": "使用该技术",
                        "strength": 0.7,
                        "auto_generated": True
                    })

            # 概念与项目的关联
            elif new_type == "concept" and entity.get("type") == "project":
                if self._check_concept_application(new_entity, entity):
                    links.append({
                        "from": entity["name"],
                        "to": new_name,
                        "type": "applies",
                        "description": "应用该概念",
                        "strength": 0.6,
                        "auto_generated": True
                    })

        return links

    def _check_potential_collaboration(self, p1: Dict, p2: Dict) -> bool:
        """检查项目间是否有潜在协作可能"""
        # 简化实现：检查是否在同一技术栈
        p1_tech = p1.get("attributes", {}).get("tech_stack", [])
        p2_tech = p2.get("attributes", {}).get("tech_stack", [])
        return bool(set(p1_tech) & set(p2_tech))

    def _check_tech_usage(self, tech: Dict, project: Dict) -> bool:
        """检查技术是否被项目使用"""
        tech_name = tech.get("name", "").lower()
        project_desc = str(project.get("attributes", {})).lower()
        return tech_name in project_desc

    def _check_concept_application(self, concept: Dict, project: Dict) -> bool:
        """检查概念是否适用于项目"""
        concept_name = concept.get("name", "").lower()
        return concept_name in ["鲁棒性", "70%边界", "物理边界"]

    def extract_entities(self, text: str) -> List[str]:
        """
        从文本中提取实体名称（简化版）
        实际实现应使用NER模型
        """
        # 这里使用简单的关键词匹配
        known_entities = [
            "NeuralSite",
            "Evo-Swarm",
            "Visual CoT",
            "MiniMax",
            "Qwen-VL",
            "Playwright",
            "70%边界",
            "鲁棒性",
            "物理边界"
        ]

        found = []
        for entity in known_entities:
            if entity in text:
                found.append(entity)

        return found

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的语义相似度（简化版）
        实际实现应使用向量嵌入
        """
        # 简单的词集合相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)

"""
LangGraph工作流编排 - Supervisor + Workers模式
实现任务路由、状态管理、断点续传
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ProjectRole(Enum):
    """项目角色定义"""
    EXECUTOR = "executor"    # 执行者 - NeuralSite
    PLANNER = "planner"      # 规划者 - Evo-Swarm
    PERCEIVER = "perceiver"  # 感知者 - Visual CoT


@dataclass
class ProjectCapability:
    """项目能力定义"""
    project_name: str
    role: ProjectRole
    capabilities: List[str]
    api_endpoint: str
    status: str


class AgentState(TypedDict):
    """Agent工作流状态"""
    task_description: str
    task_context: dict
    current_step: str
    memory_context: list
    thinking_results: list
    final_result: dict
    reflections: list
    lessons_learned: list
    retry_count: int
    errors: list


class SupervisorAgent:
    """
    Supervisor Agent - 任务协调中心
    负责分析任务、分解任务、分发任务、合成结果
    """

    def __init__(self, llm_client=None, project_registry: Dict[str, ProjectCapability] = None):
        self.llm = llm_client
        self.projects = project_registry or {}
        
        # 默认项目注册
        self._init_default_projects()
        
        # 角色能力映射
        self.capability_map = {
            "execute_code": ProjectRole.EXECUTOR,
            "plan_strategy": ProjectRole.PLANNER,
            "understand_image": ProjectRole.PERCEIVER,
            "analyze_data": ProjectRole.EXECUTOR,
            "generate_idea": ProjectRole.PLANNER,
            "visual_understand": ProjectRole.PERCEIVER,
        }
        
        # 工作流历史
        self.workflow_history: List[Dict] = []

    def _init_default_projects(self):
        """初始化默认项目"""
        if "NeuralSite" not in self.projects:
            self.projects["NeuralSite"] = ProjectCapability(
                project_name="NeuralSite",
                role=ProjectRole.EXECUTOR,
                capabilities=["semantic_api", "knowledge_graph", "browser_automation"],
                api_endpoint="http://localhost:5001",
                status="active"
            )
        
        if "Evo-Swarm" not in self.projects:
            self.projects["Evo-Swarm"] = ProjectCapability(
                project_name="Evo-Swarm",
                role=ProjectRole.PLANNER,
                capabilities=["chain_of_thought", "memory_tree", "multi_agent"],
                api_endpoint="local",
                status="active"
            )
        
        if "VisualCoT" not in self.projects:
            self.projects["VisualCoT"] = ProjectCapability(
                project_name="VisualCoT",
                role=ProjectRole.PERCEIVER,
                capabilities=["vision_understanding", "screenshot_analysis"],
                api_endpoint="local",
                status="active"
            )

    def analyze_task(self, task_description: str, context: Dict = None) -> Dict:
        """分析任务，确定需要的角色和能力"""
        context = context or {}
        
        # 简化版任务分析（实际应调用LLM）
        task_lower = task_description.lower()
        
        required_roles = []
        required_capabilities = []
        
        # 关键词匹配
        if any(k in task_lower for k in ["分析", "理解", "识别", "看", "视觉"]):
            required_roles.append(ProjectRole.PERCEIVER)
            required_capabilities.append("visual_understand")
        
        if any(k in task_lower for k in ["规划", "方案", "建议", "思考"]):
            required_roles.append(ProjectRole.PLANNER)
            required_capabilities.append("plan_strategy")
        
        if any(k in task_lower for k in ["执行", "实现", "开发", "部署", "运行"]):
            required_roles.append(ProjectRole.EXECUTOR)
            required_capabilities.append("execute_code")
        
        # 默认至少需要执行者
        if not required_roles:
            required_roles = [ProjectRole.EXECUTOR]
        
        # 构建依赖步骤
        dependencies = []
        step = 1
        
        for role in required_roles:
            dependencies.append({
                "step": step,
                "role": role.value,
                "description": self._get_role_description(role),
                "depends_on": [step - 1] if step > 1 else []
            })
            step += 1
        
        return {
            "task_description": task_description,
            "required_roles": [r.value for r in required_roles],
            "required_capabilities": required_capabilities,
            "dependencies": dependencies,
            "estimated_complexity": "high" if len(dependencies) > 2 else "medium"
        }

    def _get_role_description(self, role: ProjectRole) -> str:
        """获取角色描述"""
        role_descriptions = {
            ProjectRole.EXECUTOR: "执行具体任务",
            ProjectRole.PLANNER: "规划解决方案",
            ProjectRole.PERCEIVER: "理解视觉信息"
        }
        return role_descriptions.get(role, "执行任务")

    def route_task(self, task_analysis: Dict) -> List[Dict]:
        """根据分析结果路由任务"""
        routes = []
        
        for step in task_analysis.get("dependencies", []):
            role = step.get("role")
            
            # 查找合适的项目
            project = self._find_project_by_role(role)
            
            if project:
                routes.append({
                    "step": step["step"],
                    "project": project.project_name,
                    "role": role,
                    "description": step["description"],
                    "depends_on": step.get("depends_on", []),
                    "capabilities": project.capabilities,
                    "status": project.status
                })
        
        return routes

    def _find_project_by_role(self, role: str) -> Optional[ProjectCapability]:
        """根据角色查找合适的项目"""
        try:
            role_enum = ProjectRole(role)
        except ValueError:
            return None
        
        for project in self.projects.values():
            if project.role == role_enum and project.status == "active":
                return project
        
        return None

    def execute_coordinated(self, task_description: str, context: Dict = None) -> Dict:
        """协调执行跨项目任务"""
        context = context or {}
        
        # 1. 分析任务
        analysis = self.analyze_task(task_description, context)
        
        # 2. 规划路由
        routes = self.route_task(analysis)
        
        # 3. 模拟执行（实际应调用各项目API）
        results = {}
        for route in sorted(routes, key=lambda x: x["step"]):
            # 等待依赖完成
            for dep in route["depends_on"]:
                if dep not in results:
                    continue
            
            # 模拟执行
            results[route["step"]] = {
                "project": route["project"],
                "role": route["role"],
                "status": "completed",
                "output": f"完成{route['description']}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # 4. 合成最终结果
        final_result = self._synthesize_results(results, analysis)
        
        # 5. 记录工作流
        workflow_record = {
            "task": task_description,
            "analysis": analysis,
            "routes": routes,
            "results": results,
            "final_result": final_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.workflow_history.append(workflow_record)
        
        return workflow_record

    def _synthesize_results(self, results: Dict, analysis: Dict) -> Dict:
        """合成各子任务结果"""
        if not results:
            return {"content": "无结果", "format": "empty"}
        
        # 汇总各项目输出
        summary_parts = []
        for step, result in results.items():
            summary_parts.append(f"Step {step}: {result.get('project')} - {result.get('output')}")
        
        return {
            "content": "\n".join(summary_parts),
            "format": "text",
            "projects_involved": len(results),
            "confidence": 0.8
        }

    def get_workflow_history(self, limit: int = 10) -> List[Dict]:
        """获取工作流历史"""
        return self.workflow_history[-limit:]

    def get_available_projects(self) -> List[Dict]:
        """获取可用项目列表"""
        return [
            {
                "name": p.project_name,
                "role": p.role.value,
                "capabilities": p.capabilities,
                "status": p.status
            }
            for p in self.projects.values()
        ]


class LangGraphWorkflow:
    """
    LangGraph工作流封装
    提供简化的状态机和工作流管理
    """

    def __init__(self, supervisor: SupervisorAgent = None):
        self.supervisor = supervisor or SupervisorAgent()
        self.current_state: Optional[AgentState] = None
        self.checkpoints: List[Dict] = []

    def create_state(
        self,
        task_description: str,
        task_context: Dict = None
    ) -> AgentState:
        """创建初始状态"""
        self.current_state = {
            "task_description": task_description,
            "task_context": task_context or {},
            "current_step": "init",
            "memory_context": [],
            "thinking_results": [],
            "final_result": {},
            "reflections": [],
            "lessons_learned": [],
            "retry_count": 0,
            "errors": []
        }
        
        # 保存检查点
        self._save_checkpoint()
        
        return self.current_state

    def _save_checkpoint(self):
        """保存检查点（用于断点续传）"""
        if self.current_state:
            self.checkpoints.append({
                "state": self.current_state.copy(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # 最多保留10个检查点
            if len(self.checkpoints) > 10:
                self.checkpoints = self.checkpoints[-10:]

    def restore_checkpoint(self, index: int = -1) -> Optional[AgentState]:
        """恢复检查点"""
        if -len(self.checkpoints) <= index < len(self.checkpoints):
            self.current_state = self.checkpoints[index]["state"].copy()
            return self.current_state
        return None

    def execute_step(self, step_name: str, step_result: Any) -> AgentState:
        """执行步骤并更新状态"""
        if not self.current_state:
            raise ValueError("No current state. Call create_state first.")
        
        self.current_state["current_step"] = step_name
        
        if isinstance(step_result, dict):
            self.current_state.update(step_result)
        else:
            self.current_state["final_result"] = {"output": step_result}
        
        self._save_checkpoint()
        
        return self.current_state

    def add_thinking_result(self, thinking_result: Dict):
        """添加思考结果"""
        if self.current_state:
            self.current_state["thinking_results"].append(thinking_result)
            self._save_checkpoint()

    def add_error(self, error: str):
        """记录错误"""
        if self.current_state:
            self.current_state["errors"].append({
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.current_state["retry_count"] += 1

    def get_state(self) -> Optional[AgentState]:
        """获取当前状态"""
        return self.current_state

    def run(self, task_description: str, context: Dict = None) -> Dict:
        """运行完整工作流"""
        # 1. 创建状态
        state = self.create_state(task_description, context)
        
        # 2. 分析任务
        analysis = self.supervisor.analyze_task(task_description, context)
        self.execute_step("analyze", {"analysis": analysis})
        
        # 3. 路由任务
        routes = self.supervisor.route_task(analysis)
        self.execute_step("route", {"routes": routes})
        
        # 4. 执行
        result = self.supervisor.execute_coordinated(task_description, context)
        self.execute_step("execute", {"final_result": result.get("final_result", {})})
        
        # 5. 返回最终结果
        return {
            "state": self.current_state,
            "result": result
        }

"""
Supervisor Agent - 任务路由中心
负责分析任务、协调各能力适配器
"""
import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    DESIGN = "design"           # 设计类
    CODE = "code"               # 编码类
    TEST = "test"               # 测试类
    DEPLOY = "deploy"           # 部署类
    ANALYZE = "analyze"         # 分析类
    RESEARCH = "research"       # 研究类
    COORDINATE = "coordinate"   # 协调类


class ProjectRole(Enum):
    """项目角色"""
    EXECUTOR = "executor"       # 执行器 (NeuralSite)
    PLANNER = "planner"         # 规划器 (Evo-Swarm)
    PERCEIVER = "perceiver"     # 感知器 (VisualCoT)


@dataclass
class Task:
    """任务"""
    id: str
    description: str
    task_type: TaskType
    required_roles: List[ProjectRole]
    context: Dict[str, Any]
    priority: int = 1  # 1-5


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class ProjectAdapter:
    """项目适配器基类"""
    
    def __init__(self, name: str, role: ProjectRole, config: Dict = None):
        self.name = name
        self.role = role
        self.config = config or {}
        self.enabled = True
    
    async def execute(self, task: Task) -> TaskResult:
        """执行任务"""
        raise NotImplementedError
    
    async def get_status(self) -> Dict:
        """获取状态"""
        raise NotImplementedError
    
    async def health_check(self) -> bool:
        """健康检查"""
        return self.enabled


class SupervisorAgent:
    """
    Supervisor Agent - 任务路由中心
    
    职责：
    1. 分析用户任务，确定任务类型和所需角色
    2. 路由任务到合适的项目适配器
    3. 协调多项目协作
    4. 汇总结果并反馈
    """
    
    # 项目角色映射
    PROJECT_ROLES = {
        "NeuralSite": ProjectRole.EXECUTOR,
        "Evo-Swarm": ProjectRole.PLANNER,
        "VisualCoT": ProjectRole.PERCEIVER,
    }
    
    # 任务类型到角色的映射
    TASK_TYPE_ROUTES = {
        TaskType.DESIGN: [ProjectRole.PLANNER],
        TaskType.CODE: [ProjectRole.EXECUTOR],
        TaskType.TEST: [ProjectRole.EXECUTOR, ProjectRole.PERCEIVER],
        TaskType.DEPLOY: [ProjectRole.EXECUTOR],
        TaskType.ANALYZE: [ProjectRole.PERCEIVER],
        TaskType.RESEARCH: [ProjectRole.PLANNER, ProjectRole.PERCEIVER],
        TaskType.COORDINATE: [ProjectRole.PLANNER, ProjectRole.EXECUTOR, ProjectRole.PERCEIVER],
    }
    
    def __init__(self, adapters: Dict[str, ProjectAdapter] = None):
        self.adapters = adapters or {}
        self.task_history: List[TaskResult] = []
        
        # 注册默认适配器
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """注册默认适配器"""
        # NeuralSite - 执行器
        self.adapters["NeuralSite"] = NeuralSiteAdapter(
            name="NeuralSite",
            role=ProjectRole.EXECUTOR,
            config={"location": r"F:\drawing_3d", "api_port": 5001}
        )
        
        # Evo-Swarm - 规划器
        self.adapters["Evo-Swarm"] = EvoSwarmAdapter(
            name="Evo-Swarm",
            role=ProjectRole.PLANNER,
            config={"location": r"F:\skill\evo_swarm"}
        )
        
        # VisualCoT - 感知器
        self.adapters["VisualCoT"] = VisualCoTAdapter(
            name="VisualCoT",
            role=ProjectRole.PERCEIVER,
            config={"location": r"F:\skill\evo_swarm\visual_chain_of_thought.py"}
        )
    
    def analyze_task(self, description: str, context: Dict = None) -> Task:
        """分析任务"""
        description_lower = description.lower()
        context = context or {}
        
        # 确定任务类型
        task_type = self._classify_task(description_lower)
        
        # 确定所需角色
        required_roles = self.TASK_TYPE_ROUTES.get(task_type, [ProjectRole.EXECUTOR])
        
        # 检查上下文中的项目
        projects = context.get("projects", [])
        if projects:
            # 根据指定项目确定角色
            required_roles = []
            for p in projects:
                role = self.PROJECT_ROLES.get(p)
                if role:
                    required_roles.append(role)
        
        task_id = f"task_{len(self.task_history)}_{hash(description) % 10000}"
        
        return Task(
            id=task_id,
            description=description,
            task_type=task_type,
            required_roles=required_roles,
            context=context,
            priority=context.get("priority", 1)
        )
    
    def _classify_task(self, description: str) -> TaskType:
        """分类任务"""
        keywords = {
            TaskType.DESIGN: ["设计", "规划", "架构", "design", "plan", "architecture"],
            TaskType.CODE: ["代码", "实现", "写", "开发", "code", "implement", "build"],
            TaskType.TEST: ["测试", "测试用例", "验证", "test", "verify"],
            TaskType.DEPLOY: ["部署", "发布", "上线", "deploy", "release"],
            TaskType.ANALYZE: ["分析", "检查", "查看", "状态", "analyze", "check", "status"],
            TaskType.RESEARCH: ["研究", "调研", "探索", "research", "explore", "investigate"],
            TaskType.COORDINATE: ["协调", "整合", "同步", "coordinate", "integrate", "sync"],
        }
        
        for task_type, words in keywords.items():
            if any(w in description for w in words):
                return task_type
        
        return TaskType.CODE  # 默认
    
    async def route_task(self, task: Task) -> List[TaskResult]:
        """路由任务到适配器"""
        results = []
        
        # 收集所需角色的适配器
        target_adapters = []
        for role in task.required_roles:
            for adapter in self.adapters.values():
                if adapter.role == role and adapter.enabled:
                    target_adapters.append(adapter)
        
        if not target_adapters:
            results.append(TaskResult(
                task_id=task.id,
                success=False,
                result=None,
                error="No available adapter for required roles"
            ))
            return results
        
        # 并行执行
        import asyncio
        tasks = [adapter.execute(task) for adapter in target_adapters]
        adapter_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(adapter_results):
            if isinstance(result, Exception):
                results.append(TaskResult(
                    task_id=task.id,
                    success=False,
                    result=None,
                    error=str(result)
                ))
            else:
                results.append(result)
        
        self.task_history.extend(results)
        return results
    
    async def execute(self, description: str, context: Dict = None) -> Dict:
        """执行任务（入口）"""
        # 分析任务
        task = self.analyze_task(description, context)
        logger.info(f"Supervisor: Analyzing task {task.id}, type={task.task_type.value}")
        
        # ====== 反对层检查 ======
        # 检查用户指令是否与信念冲突
        try:
            from src.core.services.opposition_layer import get_opposition_layer
            opposition = get_opposition_layer()
            opposition_result = opposition.check_opposition(description)
            
            if opposition_result.get("conflict"):
                logger.info(f"Supervisor: Opposition triggered - {opposition_result.get('severity')}")
                
                belief = opposition_result.get("opposing_belief", {})
                severity = opposition_result.get("severity", "gentle")
                
                # 构建协商响应
                negotiation_response = {
                    "type": "opposition_negotiation",
                    "status": "conflict_detected",
                    "severity": severity,
                    "message": opposition_result.get("suggested_response", ""),
                    "opposing_belief": {
                        "content": belief.get("content", ""),
                        "confidence": belief.get("confidence", 0),
                        "stance": belief.get("stance", "neutral")
                    },
                    "user_choice": None  # pending user response
                }
                
                # 如果是strong级别，记录告警
                if severity == "strong":
                    logger.warning(f"Strong opposition detected: {belief.get('content', '')[:50]}...")
                
                return {
                    "task_id": task.id,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "success": False,  # 被反对拦截，不是正常执行
                    "results": [],
                    "opposition": negotiation_response
                }
        except Exception as e:
            logger.warning(f"Opposition check failed: {e}")
        # ====== 反对层检查结束 ======
        
        # 路由任务
        results = await self.route_task(task)
        
        # 汇总结果
        success = all(r.success for r in results)
        combined_result = {
            "task_id": task.id,
            "description": task.description,
            "task_type": task.task_type.value,
            "success": success,
            "results": [
                {
                    "adapter": r.task_id,
                    "success": r.success,
                    "result": r.result,
                    "error": r.error
                }
                for r in results
            ]
        }
        
        return combined_result
    
    async def get_status(self) -> Dict:
        """获取所有适配器状态"""
        status = {}
        for name, adapter in self.adapters.items():
            try:
                status[name] = {
                    "role": adapter.role.value,
                    "enabled": adapter.enabled,
                    "healthy": await adapter.health_check(),
                    "adapter_status": await adapter.get_status()
                }
            except Exception as e:
                status[name] = {
                    "role": adapter.role.value,
                    "enabled": adapter.enabled,
                    "healthy": False,
                    "error": str(e)
                }
        return status


# ============== 项目适配器实现 ==============

class NeuralSiteAdapter(ProjectAdapter):
    """NeuralSite 执行器适配器"""
    
    async def execute(self, task: Task) -> TaskResult:
        """执行代码任务"""
        logger.info(f"NeuralSiteAdapter: Executing {task.id}")
        
        # 模拟执行
        # 实际应该调用 F:\drawing_3d 的API
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "adapter": "NeuralSite",
                "output": f"Executed: {task.description}",
                "execution_time_ms": 150
            }
        )
    
    async def get_status(self) -> Dict:
        """获取状态"""
        return {
            "status": "ready",
            "location": self.config.get("location"),
            "pending_tasks": 0
        }


class EvoSwarmAdapter(ProjectAdapter):
    """Evo-Swarm 规划器适配器"""
    
    async def execute(self, task: Task) -> TaskResult:
        """执行规划任务"""
        logger.info(f"EvoSwarmAdapter: Planning {task.id}")
        
        # 模拟执行
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "adapter": "Evo-Swarm",
                "plan": f"Planned: {task.description}",
                "estimated_steps": 5
            }
        )
    
    async def get_status(self) -> Dict:
        """获取状态"""
        return {
            "status": "ready",
            "location": self.config.get("location"),
            "active_plans": 0
        }


class VisualCoTAdapter(ProjectAdapter):
    """VisualCoT 感知器适配器"""
    
    async def execute(self, task: Task) -> TaskResult:
        """执行感知任务"""
        logger.info(f"VisualCoTAdapter: Perceiving {task.id}")
        
        # 模拟执行
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "adapter": "VisualCoT",
                "perception": f"Perceived: {task.description}",
                "confidence": 0.85
            }
        )
    
    async def get_status(self) -> Dict:
        """获取状态"""
        return {
            "status": "ready",
            "location": self.config.get("location"),
            "pending_observations": 0
        }


# 全局实例
_supervisor = None

def get_supervisor() -> SupervisorAgent:
    """获取全局Supervisor实例"""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor

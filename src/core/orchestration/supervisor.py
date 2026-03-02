"""
Supervisor Agent - 任务路由中心
负责分析任务、协调各能力适配器
"""
import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

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
    
    def __init__(self, adapters: Dict[str, ProjectAdapter] = None, thinking=None):
        self.adapters = adapters or {}
        self.task_history: List[TaskResult] = []
        self.thinking = thinking  # ThinkEngine实例
        
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
            from src.core.services.opposition_layer import OppositionLayer
            from src.core.storage import get_storage_manager
            
            storage = get_storage_manager()
            opposition = OppositionLayer(storage=storage, think_engine=self.thinking)
            opposition_result = opposition.check_opposition(description)
            
            if opposition_result.get("conflict"):
                logger.info(f"Supervisor: Opposition triggered - {opposition_result.get('severity')}")
                
                belief = opposition_result.get("opposing_belief", {})
                severity = opposition_result.get("severity", "gentle")
                
                # 尝试使用MAR增强反对
                enhanced_result = None
                if hasattr(self, 'thinking') and self.thinking:
                    try:
                        opposition.think_engine = self.thinking
                        enhanced_result = opposition.enhanced_oppose_reflection(
                            description, 
                            belief
                        )
                    except Exception as e:
                        logger.warning(f"Enhanced opposition failed: {e}")
                
                # 如果MAR增强成功，使用增强后的响应
                if enhanced_result and enhanced_result.get("response_to_user"):
                    logger.info(f"Supervisor: Using MAR-enhanced opposition")
                    
                    negotiation_response = {
                        "type": "opposition_negotiation",
                        "status": "conflict_detected",
                        "severity": severity,
                        "message": enhanced_result.get("response_to_user", ""),
                        "opposing_belief": {
                            "content": belief.get("content", ""),
                            "confidence": belief.get("confidence", 0),
                            "stance": belief.get("stance", "neutral")
                        },
                        "debate": {
                            "judge_stance": enhanced_result.get("judge_stance"),
                            "advocate_argument": enhanced_result.get("advocate_argument", "")[:200],
                            "judge_reasoning": enhanced_result.get("judge_reasoning", "")[:200],
                            "final_confidence": enhanced_result.get("final_confidence")
                        },
                        "user_choice": None
                    }
                else:
                    # 回退到模板响应
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
                        "user_choice": None
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
        
        # ====== A2A用户任务咨询 ======
        # 复杂任务走内部讨论
        try:
            if self._should_consult_agents(description):
                logger.info(f"Supervisor: Consulting internal agents for complex task...")
                collective_result = await self._consult_agents(description)
                if collective_result:
                    return collective_result
        except Exception as e:
            logger.warning(f"A2A consultation failed: {e}")
        # ====== A2A咨询结束 ======
        
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
    
    def _should_consult_agents(self, user_input: str) -> bool:
        """判断是否需要咨询内部Agent"""
        # 复杂任务关键词 - 放宽条件
        complex_keywords = [
            "重构", "设计", "架构", "规划", "分析", "优化", 
            "创建", "实现", "方案", "建议", "评估", "review",
            "系统", "项目", "代码", "开发"
        ]
        
        # 检查是否包含复杂任务关键词
        return any(kw in user_input for kw in complex_keywords)
    
    async def _consult_agents(self, user_input: str) -> Optional[Dict]:
        """咨询内部Agent获取集体意见"""
        try:
            from src.core.orchestration.a2a_bus import get_a2a_bus, A2AMessage
            
            bus = get_a2a_bus()
            task_id = f"user-task-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            # 注册Agent响应
            responses = []
            
            def on_response(msg):
                if msg.type in ["share_belief", "propose", "response"]:
                    responses.append({
                        "agent": msg.from_agent,
                        "content": msg.payload.get("content", ""),
                        "type": msg.type
                    })
            
            bus.subscribe("all", on_response)
            
            # 广播用户任务咨询
            msg = A2AMessage(
                from_agent="Supervisor",
                to_agent="all",
                type="user_task_consult",
                payload={
                    "user_input": user_input,
                    "task_id": task_id
                },
                task_id=task_id
            )
            bus._publish(msg)
            
            # 简单等待
            import time
            time.sleep(3)
            
            if not responses:
                return None
            
            # 生成集体响应
            collective_suggestions = "\n".join([
                f"- {r['agent']}: {r['content'][:60]}..."
                for r in responses[:3]
            ])
            
            return {
                "task_id": task_id,
                "description": user_input,
                "task_type": "consultation",
                "success": True,
                "results": [],
                "type": "collective_consultation",
                "consultation": {
                    "summary": f"经过内部团队讨论，收集到 {len(responses)} 条建议",
                    "suggestions": collective_suggestions,
                    "response": f"关于「{user_input[:20]}」，团队建议：{responses[0].get('content', '需要进一步分析')[:80]}"
                }
            }
            
        except Exception as e:
            logger.warning(f"Agent consultation failed: {e}")
            return None
    
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

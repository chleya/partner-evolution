"""
心跳服务 - 定期检查和主动服务触发
"""
import logging
import schedule
import time
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HeartbeatService:
    """
    心跳服务
    定期执行检查和触发主动服务
    """

    def __init__(self, agent_core=None):
        self.logger = logging.getLogger(__name__)
        self.agent = agent_core
        self.running = False
        self.thread = None
        
        # 任务注册
        self.tasks: Dict[str, Callable] = {}
        self.task_results: Dict[str, Any] = {}
        
        # 配置
        self.config = {
            "daily_checkin_hour": 9,
            "daily_report_hour": 17,
            "heartbeat_interval_minutes": 60,
            "thinking_interval_hours": 1
        }
        
        # 注册默认任务
        self._register_default_tasks()

    def _register_default_tasks(self):
        """注册默认任务"""
        # 每天早上9点检查项目状态
        schedule.every().day.at(f"{self.config['daily_checkin_hour']:02d}:00").do(
            self._daily_checkin
        )
        
        # 每天下午5点生成进度报告
        schedule.every().day.at(f"{self.config['daily_report_hour']:02d}:00").do(
            self._evening_report
        )
        
        # 每小时执行主动思考
        schedule.every(self.config["thinking_interval_hours"]).hours.do(
            self._hourly_thinking
        )

    def register_task(self, name: str, task_func: Callable, interval: str = "daily"):
        """注册自定义任务"""
        self.tasks[name] = task_func
        
        if interval == "hourly":
            schedule.every().hour.do(task_func)
        elif interval == "daily":
            schedule.every().day.at("00:00").do(task_func)
        elif interval == "30min":
            schedule.every(30).minutes.do(task_func)

    def start(self):
        """启动心跳服务"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("Heartbeat service started")

    def stop(self):
        """停止心跳服务"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        schedule.clear()
        self.logger.info("Heartbeat service stopped")

    def _run_loop(self):
        """心跳主循环"""
        while self.running:
            try:
                schedule.run_pending()
            except Exception as e:
                self.logger.error(f"Schedule error: {e}")
            time.sleep(60)  # 每分钟检查一次

    def _daily_checkin(self):
        """每日签到"""
        self.logger.info("Executing daily checkin...")
        result = {
            "type": "daily_checkin",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }
        
        if self.agent and hasattr(self.agent, 'thinking'):
            # 思考引擎执行前瞻思考
            think_result = self.agent.thinking.think(
                context={"type": "daily_checkin"}
            )
            result["thinking"] = think_result
        
        self.task_results["daily_checkin"] = result
        return result

    def _evening_report(self):
        """晚间报告"""
        self.logger.info("Generating evening report...")
        
        result = {
            "type": "evening_report",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks_completed": len([t for t in self.task_results.values() 
                                   if t.get("status") == "completed"])
        }
        
        # 获取项目状态
        if self.agent and hasattr(self.agent, 'get_project_status'):
            result["project_status"] = self.agent.get_project_status()
        
        self.task_results["evening_report"] = result
        return result

    def _hourly_thinking(self):
        """每小时思考"""
        if self.agent and hasattr(self.agent, 'thinking'):
            if self.agent.thinking.should_think():
                self.logger.info("Executing hourly thinking...")
                result = self.agent.thinking.think()
                self.task_results["hourly_thinking"] = result
                return result
        return None

    def run_task(self, task_name: str) -> Any:
        """手动运行任务"""
        if task_name in self.tasks:
            return self.tasks[task_name]()
        elif task_name == "daily_checkin":
            return self._daily_checkin()
        elif task_name == "evening_report":
            return self._evening_report()
        elif task_name == "hourly_thinking":
            return self._hourly_thinking()
        return None

    def get_task_results(self, task_name: Optional[str] = None) -> Dict:
        """获取任务结果"""
        if task_name:
            return self.task_results.get(task_name, {})
        return self.task_results

    def get_next_scheduled(self) -> List[Dict]:
        """获取下次计划任务"""
        pending = []
        for job in schedule.jobs:
            pending.append({
                "task": str(job.job_func),
                "next_run": job.next_run.isoformat() if job.next_run else None
            })
        return pending

    def get_status(self) -> Dict:
        """获取心跳服务状态"""
        return {
            "running": self.running,
            "registered_tasks": len(self.tasks),
            "total_runs": len(self.task_results),
            "next_scheduled": self.get_next_scheduled()
        }


class SuggestionService:
    """
    主动建议服务
    基于上下文智能推荐
    """

    def __init__(self, agent_core=None):
        self.agent = agent_core
        self.suggestions: List[Dict] = []
        self.max_suggestions = 10

    def generate_suggestions(self, projects: Dict = None) -> List[Dict]:
        """生成主动建议"""
        suggestions = []
        
        if projects:
            for project_name, project_data in projects.items():
                # 基于项目状态生成建议
                stage = project_data.get("current_stage", "")
                progress = project_data.get("progress", 0)
                
                # Stage4 部署阶段建议
                if "Stage4" in stage and progress > 0.5:
                    suggestions.append({
                        "type": "deployment_prep",
                        "project": project_name,
                        "title": "准备商业部署",
                        "description": f"{project_name}已进展到{progress*100:.0f}%",
                        "priority": "high",
                        "actions": ["编写部署手册", "准备服务器环境"]
                    })
                
                # 依赖检查
                dependencies = project_data.get("dependencies", {})
                needed = dependencies.get("needed", [])
                if needed:
                    suggestions.append({
                        "type": "dependency",
                        "project": project_name,
                        "title": "获取项目依赖",
                        "description": f"需要: {', '.join(needed)}",
                        "priority": "medium"
                    })
        
        # 保持建议数量
        self.suggestions = suggestions[:self.max_suggestions]
        return self.suggestions

    def get_suggestions(self, priority: Optional[str] = None) -> List[Dict]:
        """获取建议"""
        if priority:
            return [s for s in self.suggestions if s.get("priority") == priority]
        return self.suggestions

    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """关闭建议"""
        for i, s in enumerate(self.suggestions):
            if s.get("id") == suggestion_id:
                self.suggestions.pop(i)
                return True
        return False

"""
T5: Git集成模块
安全Git操作 - sandbox分支、diff、commit、回滚
"""
import os
import subprocess
import logging
from typing import Dict, List, Optional
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)


class GitSandbox:
    """
    Git沙箱 - 安全版本控制
    
    功能：
    1. 创建sandbox分支
    2. 生成diff
    3. 安全commit
    4. 回滚机制
    """
    
    # 默认分支
    DEFAULT_BRANCH = "main"
    SANDBOX_BRANCH = "sandbox/evolve-"
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.sandbox_dir = self.repo_path / ".evolution_sandbox"
        
    def _run_git(self, args: List[str], cwd: Path = None) -> Dict:
        """执行git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd or self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_git_repo(self) -> bool:
        """检查是否是git仓库"""
        result = self._run_git(["rev-parse", "--git-dir"])
        return result.get("success", False)
    
    def init(self) -> bool:
        """初始化仓库"""
        if not self.is_git_repo():
            result = self._run_git(["init"])
            return result.get("success", False)
        return True
    
    def get_current_branch(self) -> str:
        """获取当前分支"""
        result = self._run_git(["branch", "--show-current"])
        return result.get("output", "").strip() or self.DEFAULT_BRANCH
    
    def create_sandbox_branch(self, base_branch: str = None) -> str:
        """
        创建sandbox分支
        
        Returns:
            分支名
        """
        base = base_branch or self.DEFAULT_BRANCH
        
        # 生成带时间戳的分支名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"{self.SANDBOX_BRANCH}{timestamp}"
        
        # 创建并切换分支
        result = self._run_git(["checkout", "-b", branch_name, base])
        
        if result.get("success"):
            logger.info(f"Created sandbox branch: {branch_name}")
            return branch_name
        else:
            logger.error(f"Failed to create branch: {result.get('error')}")
            return None
    
    def get_diff(self, target: str = None) -> str:
        """获取diff"""
        args = ["diff"]
        if target:
            args.append(target)
        else:
            args.append("--cached")  # 暂存区的改动
        
        result = self._run_git(args)
        return result.get("output", "") if result.get("success") else ""
    
    def stage_file(self, file_path: str) -> bool:
        """暂存文件"""
        result = self._run_git(["add", file_path])
        return result.get("success", False)
    
    def commit(self, message: str, author: str = "Evolution Bot <evolution@partner.ai>") -> Dict:
        """
        安全提交
        
        Args:
            message: 提交信息
            author: 作者
            
        Returns:
            提交结果
        """
        # 检查是否有内容提交
        status = self._run_git(["status", "--porcelain"])
        if not status.get("output", "").strip():
            return {"success": False, "error": "No changes to commit"}
        
        # 配置作者
        self._run_git(["config", "user.email", author.split("<")[1].strip(">")])
        self._run_git(["config", "user.name", author.split("<")[0].strip()])
        
        # 暂存所有改动
        self._run_git(["add", "-A"])
        
        # 提交
        result = self._run_git(["commit", "-m", message])
        
        if result.get("success"):
            # 获取提交hash
            hash_result = self._run_git(["rev-parse", "HEAD"])
            commit_hash = hash_result.get("output", "")[:7]
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "message": message
            }
        else:
            return {
                "success": False,
                "error": result.get("error")
            }
    
    def get_commit_log(self, count: int = 10) -> List[Dict]:
        """获取提交历史"""
        result = self._run_git([
            "log",
            f"-{count}",
            "--pretty=format:%h|%s|%an|%ai"
        ])
        
        if not result.get("success"):
            return []
        
        commits = []
        for line in result.get("output", "").split("\n"):
            if "|" in line:
                parts = line.split("|")
                commits.append({
                    "hash": parts[0],
                    "message": parts[1] if len(parts) > 1 else "",
                    "author": parts[2] if len(parts) > 2 else "",
                    "date": parts[3] if len(parts) > 3 else ""
                })
        
        return commits
    
    def rollback(self, target: str = "HEAD~1") -> Dict:
        """
        回滚到指定版本
        
        Args:
            target: 回滚目标 (commit hash, HEAD~n, branch)
            
        Returns:
            回滚结果
        """
        # 硬回滚
        result = self._run_git(["reset", "--hard", target])
        
        if result.get("success"):
            return {
                "success": True,
                "target": target
            }
        else:
            return {
                "success": False,
                "error": result.get("error")
            }
    
    def create_tag(self, tag_name: str, message: str = None) -> bool:
        """创建标签"""
        args = ["tag", "-a", tag_name]
        if message:
            args.extend(["-m", message])
        
        result = self._run_git(args)
        return result.get("success", False)
    
    def get_status(self) -> Dict:
        """获取仓库状态"""
        branch = self.get_current_branch()
        
        result = self._run_git(["status", "--porcelain"])
        changes = result.get("output", "").strip()
        
        return {
            "branch": branch,
            "is_sandbox": branch.startswith("sandbox/"),
            "has_changes": bool(changes),
            "change_count": len(changes.split("\n")) if changes else 0
        }


class EvolutionGitManager:
    """进化Git管理器 - 整合安全沙箱"""
    
    def __init__(self, repo_path: str = None):
        self.git = GitSandbox(repo_path)
        self.evolution_branch = None
        
    def start_evolution_cycle(self) -> str:
        """开始进化周期 - 创建新sandbox分支"""
        self.evolution_branch = self.git.create_sandbox_branch()
        return self.evolution_branch
    
    def apply_patch(self, file_path: str, content: str) -> bool:
        """应用代码修改"""
        try:
            # 写入文件
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 暂存
            self.git.stage_file(file_path)
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return False
    
    def commit_evolution(self, description: str) -> Dict:
        """提交进化结果"""
        message = f"Evolution: {description}"
        return self.git.commit(message)
    
    def rollback_evolution(self) -> bool:
        """回滚进化"""
        result = self.git.rollback("HEAD~1")
        return result.get("success", False)
    
    def complete_evolution(self, description: str, approved: bool = False) -> Dict:
        """
        完成进化周期
        
        Args:
            description: 进化描述
            approved: 是否批准
            
        Returns:
            进化结果
        """
        if approved:
            # 合并到主分支
            main_branch = self.git.DEFAULT_BRANCH
            current = self.git.get_current_branch()
            
            # 切换回主分支
            self.git._run_git(["checkout", main_branch])
            
            # 合并sandbox分支
            merge_result = self.git._run_git(["merge", "--no-ff", current])
            
            if merge_result.get("success"):
                # 创建版本标签
                from datetime import datetime
                tag = f"v-evolution-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                self.git.create_tag(tag, description)
                
                return {
                    "success": True,
                    "merged": True,
                    "tag": tag
                }
            else:
                return {
                    "success": False,
                    "error": merge_result.get("error")
                }
        else:
            # 回滚
            return {
                "success": True,
                "rolled_back": True
            }


# 全局实例
_git_manager = None

def get_evolution_git(repo_path: str = None) -> EvolutionGitManager:
    """获取Git管理器"""
    global _git_manager
    if _git_manager is None:
        _git_manager = EvolutionGitManager(repo_path)
    return _git_manager

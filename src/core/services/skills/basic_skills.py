"""
Partner-Evolution 基本技能模块
提供文件操作、网页浏览、命令执行等基础能力
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent


class FileOperator:
    """文件操作技能"""
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """读取文件"""
        path = Path(file_path)
        if not path.exists():
            return f"文件不存在: {file_path}"
        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            return f"读取失败: {e}"
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> str:
        """写入文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(content, encoding=encoding)
            return f"写入成功: {file_path}"
        except Exception as e:
            return f"写入失败: {e}"
    
    @staticmethod
    def list_files(directory: str = ".", pattern: str = "*") -> List[str]:
        """列出文件"""
        path = Path(directory)
        if not path.exists():
            return [f"目录不存在: {directory}"]
        try:
            files = list(path.glob(pattern))
            return [str(f.relative_to(path)) for f in files]
        except Exception as e:
            return [f"列出失败: {e}"]
    
    @staticmethod
    def delete_file(file_path: str) -> str:
        """删除文件"""
        path = Path(file_path)
        if not path.exists():
            return f"文件不存在: {file_path}"
        try:
            path.unlink()
            return f"删除成功: {file_path}"
        except Exception as e:
            return f"删除失败: {e}"
    
    @staticmethod
    def create_directory(directory: str) -> str:
        """创建目录"""
        path = Path(directory)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return f"创建成功: {directory}"
        except Exception as e:
            return f"创建失败: {e}"


class WebBrowser:
    """网页浏览技能"""
    
    def __init__(self):
        self.current_url = None
        self.page_content = None
    
    def visit(self, url: str) -> str:
        """访问网页"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            self.current_url = url
            self.page_content = response.text[:5000]  # 限制长度
            return f"访问成功: {url}\n状态码: {response.status_code}\n内容长度: {len(response.text)}"
        except Exception as e:
            return f"访问失败: {e}"
    
    def search(self, query: str, engine: str = "bing") -> str:
        """搜索网页"""
        engines = {
            "bing": f"https://www.bing.com/search?q={query}",
            "google": f"https://www.google.com/search?q={query}",
            "baidu": f"https://www.baidu.com/s?wd={query}"
        }
        url = engines.get(engine, engines["bing"])
        return self.visit(url)
    
    def get_content(self) -> str:
        """获取当前页面内容"""
        if self.page_content:
            return self.page_content[:3000]
        return "没有访问过任何页面"


class CommandRunner:
    """命令执行技能"""
    
    @staticmethod
    def run(command: str, timeout: int = 30) -> str:
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(PROJECT_ROOT)
            )
            output = result.stdout or result.stderr
            return f"命令: {command}\n输出:\n{output[:2000]}"
        except subprocess.TimeoutExpired:
            return f"命令超时: {command}"
        except Exception as e:
            return f"执行失败: {e}"
    
    @staticmethod
    def run_python(script: str, args: List[str] = None) -> str:
        """运行Python脚本"""
        cmd = [sys.executable, script]
        if args:
            cmd.extend(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(PROJECT_ROOT)
            )
            return result.stdout or result.stderr
        except Exception as e:
            return f"运行失败: {e}"


class SystemOperator:
    """系统操作技能"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """获取系统信息"""
        import platform
        return {
            "system": platform.system(),
            "version": platform.version(),
            " "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
    
    @staticmethod
    def get_disk_usage() -> Dict:
        """获取磁盘使用情况"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {
            "total": f"{total // (1024**3)} GB",
            "used": f"{used // (1024**3)} GB",
            "free": f"{free // (1024**3)} GB"
        }
    
    @staticmethod
    def get_memory_usage() -> Dict:
        """获取内存使用情况"""
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total": f"{mem.total / (1024**3):.2f} GB",
            "available": f"{mem.available / (1024**3):.2f} GB",
            "percent": f"{mem.percent}%"
        }


class NotificationSkill:
    """通知技能"""
    
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> str:
        """发送邮件 (需要配置SMTP)"""
        # 简化实现
        return f"邮件发送功能需要配置SMTP服务器\n收件人: {to}\n主题: {subject}"
    
    @staticmethod
    def send_webhook(url: str, data: Dict) -> str:
        """发送Webhook"""
        try:
            import requests
            response = requests.post(url, json=data, timeout=10)
            return f"Webhook发送成功: {response.status_code}"
        except Exception as e:
            return f"Webhook发送失败: {e}"


class DataProcessor:
    """数据处理技能"""
    
    @staticmethod
    def parse_json(text: str) -> Dict:
        """解析JSON"""
        try:
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def to_json(data: Any) -> str:
        """转换为JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict]:
        """读取CSV"""
        import csv
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def write_csv(file_path: str, data: List[Dict]) -> str:
        """写入CSV"""
        import csv
        if not data:
            return "没有数据"
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return f"写入成功: {file_path}"
        except Exception as e:
            return f"写入失败: {e}"


# 技能注册表
SKILLS = {
    "file": {
        "read": FileOperator.read_file,
        "write": FileOperator.write_file,
        "list": FileOperator.list_files,
        "delete": FileOperator.delete_file,
        "mkdir": FileOperator.create_directory,
    },
    "web": {
        "visit": WebBrowser().visit,
        "search": WebBrowser().search,
    },
    "cmd": {
        "run": CommandRunner.run,
        "python": CommandRunner.run_python,
    },
    "system": {
        "info": SystemOperator.get_system_info,
        "disk": SystemOperator.get_disk_usage,
        "memory": SystemOperator.get_memory_usage,
    },
    "notify": {
        "email": NotificationSkill.send_email,
        "webhook": NotificationSkill.send_webhook,
    },
    "data": {
        "json_parse": DataProcessor.parse_json,
        "json_dump": DataProcessor.to_json,
        "csv_read": DataProcessor.read_csv,
        "csv_write": DataProcessor.write_csv,
    },
}


def use_skill(category: str, skill: str, **kwargs) -> str:
    """使用技能"""
    if category not in SKILLS:
        return f"未知技能分类: {category}"
    if skill not in SKILLS[category]:
        return f"未知技能: {category}.{skill}"
    
    try:
        result = SKILLS[category][skill](**kwargs)
        return str(result)
    except Exception as e:
        return f"技能执行失败: {e}"


# CLI测试
if __name__ == "__main__":
    print("=== Partner-Evolution 基本技能 ===")
    print()
    
    # 测试文件操作
    print("1. 文件操作:")
    print(f"   读取: {FileOperator.read_file('README.md')[:100]}...")
    print()
    
    # 测试系统信息
    print("2. 系统信息:")
    info = SystemOperator.get_system_info()
    for k, v in info.items():
        print(f"   {k}: {v}")
    print()
    
    print("可用技能:")
    for cat, skills in SKILLS.items():
        print(f"  {cat}: {', '.join(skills.keys())}")

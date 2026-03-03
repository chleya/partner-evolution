"""
Basic Skills Module
File, Web, Cmd, System operations
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any


class FileOperator:
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"
        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            return f"Read failed: {e}"
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> str:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(content, encoding=encoding)
            return f"Written: {file_path}"
        except Exception as e:
            return f"Write failed: {e}"
    
    @staticmethod
    def list_files(directory: str = ".", pattern: str = "*") -> List[str]:
        path = Path(directory)
        if not path.exists():
            return ["Directory not found"]
        try:
            files = list(path.glob(pattern))
            return [str(f.relative_to(path)) for f in files[:50]]
        except Exception as e:
            return [f"Error: {e}"]
    
    @staticmethod
    def delete_file(file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            return f"Not found: {file_path}"
        try:
            path.unlink()
            return f"Deleted: {file_path}"
        except Exception as e:
            return f"Failed: {e}"
    
    @staticmethod
    def create_directory(directory: str) -> str:
        path = Path(directory)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return f"Created: {directory}"
        except Exception as e:
            return f"Failed: {e}"
    
    @staticmethod
    def parse_json(text: str) -> Dict:
        try:
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def to_json(data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict]:
        import csv
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            return [{"error": str(e)}]


class WebBrowser:
    def __init__(self):
        self.current_url = None
        self.page_content = None
    
    def visit(self, url: str) -> str:
        try:
            import requests
            response = requests.get(url, timeout=10)
            self.current_url = url
            self.page_content = response.text[:5000]
            return f"Visited: {url}\nStatus: {response.status_code}"
        except Exception as e:
            return f"Failed: {e}"
    
    def search(self, query: str, engine: str = "bing") -> str:
        engines = {
            "bing": f"https://www.bing.com/search?q={query}",
            "google": f"https://www.google.com/search?q={query}",
            "baidu": f"https://www.baidu.com/s?wd={query}"
        }
        url = engines.get(engine, engines["bing"])
        return self.visit(url)
    
    def get_content(self) -> str:
        if self.page_content:
            return self.page_content[:3000]
        return "No page visited"


class CommandRunner:
    @staticmethod
    def run(command: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout or result.stderr
            return f"Command: {command}\nOutput:\n{output[:2000]}"
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def run_python(script: str, args: List[str] = None) -> str:
        cmd = [sys.executable, script]
        if args:
            cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Failed: {e}"


class SystemOperator:
    @staticmethod
    def get_system_info() -> Dict:
        import platform
        return {
            "system": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def get_disk_usage() -> Dict:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {
            "total_gb": total // (1024**3),
            "used_gb": used // (1024**3),
            "free_gb": free // (1024**3)
        }
    
    @staticmethod
    def get_memory_usage() -> Dict:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent
            }
        except:
            return {"error": "psutil not available"}


SKILLS = {
    "file": FileOperator,
    "web": WebBrowser,
    "cmd": CommandRunner,
    "system": SystemOperator
}

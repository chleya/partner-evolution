"""
记忆存储层 - 负责JSON文件的读写操作
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryStore:
    """JSON文件存储管理器"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)

    def load(self, filename: str) -> Optional[Dict[str, Any]]:
        """加载JSON文件"""
        file_path = self.base_path / filename
        
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in {filename}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading {filename}: {e}")
            return None

    def save(self, filename: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """保存JSON文件（原子操作）"""
        file_path = self.base_path / filename

        try:
            # 先写临时文件，再重命名（原子操作）
            temp_path = self.base_path / f"{filename}.tmp"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            temp_path.replace(file_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            return False

    def exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        return (self.base_path / filename).exists()

    def delete(self, filename: str) -> bool:
        """删除文件"""
        file_path = self.base_path / filename
        
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting {filename}: {e}")
            return False

    def list_files(self, pattern: str = "*.json") -> list:
        """列出匹配的文件"""
        return list(self.base_path.glob(pattern))

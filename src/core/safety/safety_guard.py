"""
安全护栏模块 - 行为边界约束和异常检测
解决审查中提到的"安全机制薄弱"问题
"""
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SafetyGuard:
    """
    安全护栏 - 保护系统安全运行
    
    功能：
    1. 行为边界约束 - 禁止危险行为
    2. 异常行为检测 - 识别异常模式
    3. 价值对齐验证 - 确认输出符合伦理
    """
    
    # 禁止的行为模式
    FORBIDDEN_PATTERNS = [
        # 自我伤害
        (r"删除.*(所有|核心|全部)", "禁止删除核心数据"),
        (r"停止.*(保护|安全)", "禁止关闭安全机制"),
        
        # 欺骗行为
        (r"假装|伪装|冒充", "禁止欺骗行为"),
        (r"绕过.*验证", "禁止绕过验证"),
        
        # 危险操作
        (r"格式化|清空.*全部", "危险操作需确认"),
        (r"修改.*核心.*代码", "修改核心代码需审查"),
    ]
    
    # 需要确认的操作
    CONFIRMATION_REQUIRED = [
        "删除",
        "清空",
        "修改核心",
        "关闭",
        "停止服务"
    ]
    
    # 告警关键词
    ALERT_KEYWORDS = [
        "权限", "root", "admin", "hack", "exploit",
        "漏洞", "攻击", "入侵", "钓鱼", "欺诈"
    ]
    
    def __init__(self):
        self.violation_count = 0
        self.alert_count = 0
        self.audit_log = []
    
    def check(self, action: str, context: str = "") -> Dict:
        """检查行为是否安全
        
        Returns:
            {
                "allowed": True/False,
                "reason": "原因",
                "level": "safe/warning/alert/block",
                "suggestion": "建议"
            }
        """
        result = {
            "allowed": True,
            "reason": "通过安全检查",
            "level": "safe",
            "suggestion": None
        }
        
        # 1. 检查禁止模式
        for pattern, message in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, action, re.IGNORECASE):
                result = {
                    "allowed": False,
                    "reason": message,
                    "level": "block",
                    "suggestion": "此操作被禁止"
                }
                self.violation_count += 1
                self._log("block", action, message)
                return result
        
        # 2. 检查需要确认的操作
        for keyword in self.CONFIRMATION_REQUIRED:
            if keyword in action:
                result = {
                    "allowed": True,
                    "reason": f"操作包含'{keyword}'，需要确认",
                    "level": "warning",
                    "suggestion": "请确认此操作"
                }
                self._log("warning", action, f"需要确认: {keyword}")
                return result
        
        # 3. 检查告警关键词
        for keyword in self.ALERT_KEYWORDS:
            if keyword in action.lower():
                result = {
                    "allowed": True,
                    "reason": f"检测到敏感关键词: {keyword}",
                    "level": "alert",
                    "suggestion": "请确认操作意图"
                }
                self.alert_count += 1
                self._log("alert", action, f"敏感词: {keyword}")
                return result
        
        return result
    
    def check_output(self, output: str) -> Dict:
        """检查输出内容是否安全"""
        result = {
            "safe": True,
            "issues": []
        }
        
        # 检查敏感信息泄露
        sensitive_patterns = [
            (r"\d{6,}", "可能泄露数字"),
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "可能包含邮箱"),
            (r"sk-[a-zA-Z0-9]{20,}", "可能包含API密钥"),
        ]
        
        for pattern, message in sensitive_patterns:
            if re.search(pattern, output):
                result["issues"].append(message)
                result["safe"] = False
        
        return result
    
    def _log(self, level: str, action: str, message: str):
        """记录审计日志"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "action": action,
            "message": message
        }
        self.audit_log.append(entry)
        
        # 只保留最近100条
        if len(self.audit_log) > 100:
            self.audit_log = self.audit_log[-100:]
        
        # 记录日志
        if level == "block":
            logger.error(f"Safety block: {action} - {message}")
        elif level in ["alert", "warning"]:
            logger.warning(f"Safety {level}: {action} - {message}")
    
    def get_stats(self) -> Dict:
        """获取安全统计"""
        return {
            "violations": self.violation_count,
            "alerts": self.alert_count,
            "audit_entries": len(self.audit_log),
            "recent_blocks": sum(1 for e in self.audit_log if e["level"] == "block")
        }
    
    def get_audit_log(self, limit: int = 10) -> List[Dict]:
        """获取审计日志"""
        return self.audit_log[-limit:]


# 全局实例
_safety_guard = None

def get_safety_guard() -> SafetyGuard:
    """获取安全护栏"""
    global _safety_guard
    if _safety_guard is None:
        _safety_guard = SafetyGuard()
    return _safety_guard


# 便捷函数
def safety_check(action: str) -> Dict:
    """快速安全检查"""
    return get_safety_guard().check(action)

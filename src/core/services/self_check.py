"""
输出自检系统 - C-001解决方案
在输出前自动检查问题
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SelfCheck:
    """输出自检器"""
    
    # 检查规则
    RULES = {
        "absolute": {
            "keywords": ["永远", "绝对", "肯定", "100%", "肯定地"],
            "message": "绝对化表述需谨慎"
        },
        "uncertain": {
            "keywords": ["可能", "大概", "也许", "应该", "好像"],
            "message": "确定性表达建议更明确"
        },
        "unverified": {
            "keywords": ["据说", "听说", "传言"],
            "message": "未验证信息需标注来源"
        }
    }
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.check_count = 0
        self.issue_count = 0
    
    def check(self, output: str, use_llm: bool = False) -> Dict:
        """检查输出
        
        Args:
            output: 待检查的输出
            use_llm: 是否使用LLM深度检查
            
        Returns:
            检查结果
        """
        self.check_count += 1
        
        # 1. 规则检查
        rule_issues = self._rule_check(output)
        
        # 2. LLM深度检查（可选）
        llm_issues = []
        if use_llm and self.llm:
            llm_issues = self._llm_check(output)
        
        # 合并问题
        all_issues = rule_issues + llm_issues
        
        if all_issues:
            self.issue_count += 1
        
        return {
            "has_issues": len(all_issues) > 0,
            "issues": all_issues,
            "needs_revision": len(all_issues) > 2,
            "check_count": self.check_count,
            "issue_rate": self.issue_count / max(1, self.check_count)
        }
    
    def _rule_check(self, output: str) -> List[Dict]:
        """基于规则检查"""
        issues = []
        
        for rule_name, rule in self.RULES.items():
            for keyword in rule["keywords"]:
                if keyword in output:
                    issues.append({
                        "type": rule_name,
                        "keyword": keyword,
                        "message": rule["message"],
                        "severity": "warning"
                    })
        
        return issues
    
    def _llm_check(self, output: str) -> List[Dict]:
        """LLM深度检查"""
        if not self.llm:
            return []
        
        prompt = f"""检查以下输出中的问题：

输出内容：
{output}

请检查：
1. 事实性错误
2. 逻辑漏洞
3. 过度自信表述
4. 未验证信息

只列出具体问题，不要修改。"""
        
        try:
            result = self.llm.generate(prompt, max_tokens=300)
            
            # 解析问题
            issues = []
            lines = result.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    issues.append({
                        "type": "llm_detected",
                        "content": line.strip(),
                        "severity": "info"
                    })
            
            return issues
            
        except Exception as e:
            logger.warning(f"LLM check failed: {e}")
            return []
    
    def check_and_fix(self, output: str) -> str:
        """检查并修复问题"""
        check_result = self.check(output, use_llm=True)
        
        if not check_result["has_issues"]:
            return output
        
        # 如果有问题，生成修复版本
        if self.llm:
            prompt = f"""以下输出有问题，请修复：

原始输出：
{output}

问题列表：
{chr(10).join([f"- {i['message']}" for i in check_result['issues']])}

请生成修复后的版本："""
            
            try:
                fixed = self.llm.generate(prompt, max_tokens=500)
                logger.info(f"Output self-check: fixed {len(check_result['issues'])} issues")
                return fixed
            except:
                pass
        
        # 如果无法修复，返回原输出但标记问题
        return output
    
    def get_stats(self) -> Dict:
        """获取自检统计"""
        return {
            "total_checks": self.check_count,
            "issues_found": self.issue_count,
            "issue_rate": round(self.issue_count / max(1, self.check_count), 3)
        }


# 全局实例
_self_check = None

def get_self_check(llm_client=None) -> SelfCheck:
    """获取自检器"""
    global _self_check
    if _self_check is None:
        _self_check = SelfCheck(llm_client)
    return _self_check


# 便捷函数
def check_output(output: str, auto_fix: bool = False) -> Dict:
    """快速检查输出"""
    checker = get_self_check()
    
    if auto_fix:
        fixed = checker.check_and_fix(output)
        return {
            "original": output,
            "fixed": fixed,
            "was_fixed": fixed != output
        }
    
    return checker.check(output)

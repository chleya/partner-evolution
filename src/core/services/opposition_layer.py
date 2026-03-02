"""
反对用户机制 (Opposition Layer)
当用户指令与系统信念冲突时，触发协商输出
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class OppositionLayer:
    """
    反对用户机制
    
    功能：
    - 检测用户指令与系统信念的冲突
    - 生成协商输出（而非直接服从）
    - 分级打扰控制
    """
    
    def __init__(self, storage, think_engine=None, llm_client=None):
        self.storage = storage
        self.think_engine = think_engine
        self.llm = llm_client
        
        # 配置
        self.config = {
            "oppose_threshold": 0.75,        # 触发反对的最低置信度
            "gentle_threshold": 0.70,        # 温和提醒阈值
            "strong_threshold": 0.85,         # 强制协商阈值
            "max_beliefs_to_check": 5,       # 最多检查的信念数
            "similarity_low": 0.6,            # 语义相似度阈值（低于此值认为冲突）
            "enabled": True                   # 开关
        }
    
    def check_opposition(self, user_input: str) -> Dict:
        """
        检查用户指令是否与信念冲突
        
        返回：
        {
            'conflict': bool,
            'opposing_belief': dict or None,
            'suggested_response': str,
            'severity': 'gentle/strong/none'
        }
        """
        if not self.config["enabled"]:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 1. 获取高置信度信念
        beliefs = self._get_high_confidence_beliefs()
        
        if not beliefs:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 2. 检查冲突
        conflicting_belief = self._find_conflicting_belief(user_input, beliefs)
        
        if not conflicting_belief:
            return {
                "conflict": False,
                "opposing_belief": None,
                "suggested_response": None,
                "severity": "none"
            }
        
        # 3. 确定严重程度
        confidence = conflicting_belief.get("confidence", 0)
        
        if confidence >= self.config["strong_threshold"]:
            severity = "strong"
        elif confidence >= self.config["gentle_threshold"]:
            severity = "gentle"
        else:
            severity = "none"
        
        # 4. 生成建议响应
        suggested_response = self._generate_response(
            user_input, 
            conflicting_belief, 
            severity
        )
        
        # 5. 记录反对日志
        self._log_opposition(user_input, conflicting_belief, severity)
        
        return {
            "conflict": True,
            "opposing_belief": conflicting_belief,
            "suggested_response": suggested_response,
            "severity": severity,
            "confidence": confidence
        }
    
    def _get_high_confidence_beliefs(self) -> List[Dict]:
        """获取高置信度信念"""
        all_beliefs = self.storage.get_beliefs(status="active")
        
        # 过滤高置信度
        high_conf = [
            b for b in all_beliefs 
            if b.get("confidence", 0) >= self.config["gentle_threshold"]
        ]
        
        # 按置信度排序
        high_conf.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return high_conf[:self.config["max_beliefs_to_check"]]
    
    def _find_conflicting_belief(self, user_input: str, beliefs: List[Dict]) -> Optional[Dict]:
        """查找冲突的信念"""
        user_input_lower = user_input.lower()
        
        for belief in beliefs:
            belief_content = belief.get("content", "").lower()
            stance = belief.get("stance", "neutral")
            confidence = belief.get("confidence", 0)
            
            # 跳过低置信度
            if confidence < self.config["oppose_threshold"]:
                continue
            
            # 检查是否冲突
            conflict = self._detect_conflict(user_input_lower, belief_content, stance)
            
            if conflict:
                return belief
        
        return None
    
    def _detect_conflict(self, user_input: str, belief_content: str, stance: str) -> bool:
        """检测冲突"""
        # 关键词冲突检测
        conflict_keywords = {
            # 用户说不要优化，但信念说要优化
            ("不优化", "优化", "检索"): True,
            ("忽略", "遗忘"): True,
            ("暂停", "停止"): True,
            
            # 用户说要简单，但信念说要质量
            ("够用", "简单"): True,
            
            # 用户说要快，但信念说要质量
            ("快", "速度"): stance == "positive",
        }
        
        # 简单关键词检测
        user_words = user_input.split()
        belief_words = belief_content.split()
        
        # 检查是否有相反意图
        negative_words = ["不", "别", "不要", "停止", "暂停", "忽略"]
        positive_words = ["要", "需要", "应该", "必须", "持续", "优化"]
        
        has_negative = any(w in user_input for w in negative_words)
        has_positive_belief = any(w in belief_content for w in positive_words)
        
        if has_negative and has_positive_belief:
            return True
        
        # 检查内容重叠度
        overlap = set(user_words) & set(belief_words)
        
        # 如果有重叠但用户持否定态度，认为有冲突风险
        if len(overlap) >= 2 and has_negative:
            return True
        
        return False
    
    def _generate_response(self, user_input: str, belief: Dict, severity: str) -> str:
        """生成协商响应"""
        belief_content = belief.get("content", "")
        confidence = belief.get("confidence", 0)
        reasoning = belief.get("metadata", {}).get("reasoning", "基于我的自省")
        
        if severity == "strong":
            # 强制协商
            response = f"""我有重要不同看法想与你沟通。

我的自省主张：{belief_content}
（置信度: {confidence:.0%}）

理由：{reasoning}

这个观点与你刚才的指令似乎有冲突。你想：
1. 坚持原指令 - 好的，我执行
2. 调整指令 - 请告诉我新的方向
3. 听我解释 - 我详细说明我的思考过程

你怎么选择？"""
        
        else:
            # 温和提醒
            response = f"""顺便说一下，我有个想法与你分享。

我的自省：{belief_content}
（置信度: {confidence:.0%}）

{reasoning}

不一定对，但想让你知道。你坚持原计划还是想聊聊？"""
        
        return response
    
    def _log_opposition(self, user_input: str, belief: Dict, severity: str):
        """记录反对到日志"""
        logger.info(
            f"Opposition triggered: severity={severity}, "
            f"belief={belief.get('content', '')[:50]}..., "
            f"user_input={user_input[:30]}..."
        )
    
    def should_oppose(self, user_input: str) -> bool:
        """快速检查是否应该反对"""
        result = self.check_opposition(user_input)
        return result.get("conflict", False)


# 全局实例
_opposition_layer = None

def get_opposition_layer(storage=None) -> OppositionLayer:
    """获取反对层实例"""
    global _opposition_layer
    
    if _opposition_layer is None:
        if storage is None:
            from src.core.storage import get_storage_manager
            storage = get_storage_manager()
        
        _opposition_layer = OppositionLayer(storage=storage)
    
    return _opposition_layer


def check_opposition(user_input: str) -> Dict:
    """便捷函数：检查是否需要反对"""
    layer = get_opposition_layer()
    return layer.check_opposition(user_input)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    layer = get_opposition_layer()
    
    # 测试用例
    test_inputs = [
        "暂时别优化检索效率了，先跑功能",
        "把记忆系统停掉",
        "以后每天早上不用签到了",
        "分析一下NeuralSite项目进度"
    ]
    
    for inp in test_inputs:
        print(f"\n{'='*50}")
        print(f"User: {inp}")
        result = layer.check_opposition(inp)
        print(f"Conflict: {result['conflict']}")
        if result['conflict']:
            print(f"Severity: {result['severity']}")
            print(f"Belief: {result['opposing_belief'].get('content', '')[:60]}...")
            print(f"\nSuggested Response:\n{result['suggested_response'][:200]}...")

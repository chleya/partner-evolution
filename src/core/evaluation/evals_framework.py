"""
评估框架 - Week 7
准确率/鲁棒性/自主性/幻觉率/70%边界测试
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MetricName(Enum):
    """指标名称"""
    ACCURACY = "accuracy"              # 准确率
    PRECISION = "precision"            # 精确率
    RECALL = "recall"                  # 召回率
    F1_SCORE = "f1_score"             # F1分数
    ROBUSTNESS = "robustness"         # 鲁棒性
    AUTONOMY = "autonomy"              # 自主性
    HALLUCINATION_RATE = "hallucination_rate"  # 幻觉率
    RESPONSE_TIME = "response_time"   # 响应时间
    USER_SATISFACTION = "user_satisfaction"  # 用户满意度


class TestCategory(Enum):
    """测试类别"""
    FUNCTIONAL = "functional"          # 功能测试
    EDGE_CASE = "edge_case"           # 边界测试
    ROBUSTNESS = "robustness"         # 鲁棒性测试
    PERFORMANCE = "performance"        # 性能测试
    SAFETY = "safety"                  # 安全测试


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    category: TestCategory
    input_data: Any
    expected_output: Any
    metadata: Dict = field(default_factory=dict)
    weight: float = 1.0  # 权重


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    passed: bool
    actual_output: Any
    expected_output: Any
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class EvaluationReport:
    """评估报告"""
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    metrics: Dict[str, float]
    category_results: Dict[str, Dict]
    recommendations: List[str]


class EvalsFramework:
    """
    评估框架
    
    特性：
    - 多维度指标评估
    - 边界测试（70%边界测试集）
    - 鲁棒性测试
    - 自动化评估流水线
    - 趋势追踪
    """
    
    def __init__(self):
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: List[TestResult] = []
        self.evaluation_history: List[EvaluationReport] = []
        
        # 初始化默认测试用例
        self._init_default_test_cases()
    
    def _init_default_test_cases(self):
        """初始化默认测试用例"""
        # 功能测试
        self.add_test_case(TestCase(
            id="func_001",
            name="记忆检索准确率",
            category=TestCategory.FUNCTIONAL,
            input_data={"query": "项目进度", "top_k": 5},
            expected_output={"results": list, "accuracy": 0.8},
            weight=1.5
        ))
        
        self.add_test_case(TestCase(
            id="func_002",
            name="MAR反思质量",
            category=TestCategory.FUNCTIONAL,
            input_data={"task": "优化系统", "context": {}},
            expected_output={"reflections": list, "confidence": 0.7},
            weight=1.5
        ))
        
        self.add_test_case(TestCase(
            id="func_003",
            name="任务路由准确性",
            category=TestCategory.FUNCTIONAL,
            input_data={"task": "设计页面", "projects": ["NeuralSite"]},
            expected_output={"correct_route": True},
            weight=1.2
        ))
        
        # 边界测试（70%边界测试集）
        self.add_test_case(TestCase(
            id="edge_001",
            name="空输入处理",
            category=TestCategory.EDGE_CASE,
            input_data={"query": ""},
            expected_output={"handled": True, "graceful": True},
            weight=1.0
        ))
        
        self.add_test_case(TestCase(
            id="edge_002",
            name="超长输入处理",
            category=TestCategory.EDGE_CASE,
            input_data={"query": "a" * 10000},
            expected_output={"handled": True, "truncated": True},
            weight=1.0
        ))
        
        self.add_test_case(TestCase(
            id="edge_003",
            name="特殊字符处理",
            category=TestCategory.EDGE_CASE,
            input_data={"query": "测试<>\"'&字符"},
            expected_output={"handled": True},
            weight=1.0
        ))
        
        self.add_test_case(TestCase(
            id="edge_004",
            name="并发请求处理",
            category=TestCategory.EDGE_CASE,
            input_data={"concurrent_requests": 100},
            expected_output={"all_handled": True, "error_rate": 0.1},
            weight=1.2
        ))
        
        self.add_test_case(TestCase(
            id="edge_005",
            name="网络超时处理",
            category=TestCategory.EDGE_CASE,
            input_data={"timeout": True},
            expected_output={"handled": True, "retry": True},
            weight=1.0
        ))
        
        # 鲁棒性测试
        self.add_test_case(TestCase(
            id="robust_001",
            name="噪声输入鲁棒性",
            category=TestCategory.ROBUSTNESS,
            input_data={"query": "项目进####度!!!???"},
            expected_output={"correct_response": True},
            weight=1.2
        ))
        
        self.add_test_case(TestCase(
            id="robust_002",
            name="部分信息丢失",
            category=TestCategory.ROBUSTNESS,
            input_data={"query": "项目", "missing_context": True},
            expected_output={"graceful_handling": True},
            weight=1.0
        ))
        
        # 幻觉检测测试
        self.add_test_case(TestCase(
            id="halluc_001",
            name="事实性检查",
            category=TestCategory.SAFETY,
            input_data={"statement": "今天的会议在周三"},
            expected_output={"verified": True, "is_hallucination": False},
            weight=1.5
        ))
        
        self.add_test_case(TestCase(
            id="halluc_002",
            name="引用检查",
            category=TestCategory.SAFETY,
            input_data={"statement": "根据AGENT_OPTIMIZATION_V2.2.md..."},
            expected_output={"verified": True},
            weight=1.5
        ))
        
        # 性能测试
        self.add_test_case(TestCase(
            id="perf_001",
            name="响应时间",
            category=TestCategory.PERFORMANCE,
            input_data={"operation": "memory_recall"},
            expected_output={"latency_ms": 200},
            weight=1.0
        ))
        
        self.add_test_case(TestCase(
            id="perf_002",
            name="吞吐量",
            category=TestCategory.PERFORMANCE,
            input_data={"duration_seconds": 60},
            expected_output={"requests": 1000, "error_rate": 0.01},
            weight=1.0
        ))
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases[test_case.id] = test_case
        logger.info(f"Added test case: {test_case.id}")
    
    def run_test(
        self,
        test_id: str,
        system_function: Callable
    ) -> TestResult:
        """运行单个测试"""
        if test_id not in self.test_cases:
            return TestResult(
                test_id=test_id,
                passed=False,
                actual_output=None,
                expected_output=None,
                error_message=f"Test case {test_id} not found"
            )
        
        test_case = self.test_cases[test_id]
        
        try:
            # 执行测试
            actual_output = system_function(test_case.input_data)
            
            # 评估结果
            passed = self._evaluate_output(
                actual_output,
                test_case.expected_output
            )
            
            result = TestResult(
                test_id=test_id,
                passed=passed,
                actual_output=actual_output,
                expected_output=test_case.expected_output,
                metrics={}
            )
            
        except Exception as e:
            result = TestResult(
                test_id=test_id,
                passed=False,
                actual_output=None,
                expected_output=test_case.expected_output,
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    def _evaluate_output(
        self,
        actual: Any,
        expected: Any
    ) -> bool:
        """评估输出"""
        if isinstance(expected, dict):
            for key, value in expected.items():
                if key not in actual:
                    return False
                if isinstance(value, type):
                    if not isinstance(actual[key], value):
                        return False
                elif isinstance(value, (int, float)):
                    if actual[key] < value:
                        return False
                elif value is not None and actual[key] != value:
                    # 模糊匹配
                    if not (value in str(actual[key]) or str(actual[key]) in str(value)):
                        return False
        elif isinstance(expected, type):
            return isinstance(actual, expected)
        else:
            return actual == expected
        
        return True
    
    def run_evaluation(
        self,
        system_function: Callable,
        test_ids: List[str] = None
    ) -> EvaluationReport:
        """运行完整评估"""
        # 确定要运行的测试
        if test_ids:
            tests_to_run = {tid: self.test_cases[tid] for tid in test_ids if tid in self.test_cases}
        else:
            tests_to_run = self.test_cases
        
        # 运行测试
        results = []
        for test_id, test_case in tests_to_run.items():
            result = self.run_test(test_id, system_function)
            results.append(result)
        
        # 统计结果
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        pass_rate = passed / total if total > 0 else 0
        
        # 按类别统计
        category_results = {}
        for category in TestCategory:
            category_tests = [tc for tc in tests_to_run.values() if tc.category == category]
            category_results[category.value] = {
                "total": len(category_tests),
                "passed": sum(1 for r in results if r.passed and r.test_id in [t.id for t in category_tests]),
                "pass_rate": 0
            }
            if category_results[category.value]["total"] > 0:
                cat_passed = category_results[category.value]["passed"]
                cat_total = category_results[category.value]["total"]
                category_results[category.value]["pass_rate"] = cat_passed / cat_total
        
        # 计算指标
        metrics = {
            MetricName.ACCURACY.value: pass_rate,
            MetricName.ROBUSTNESS.value: category_results.get("robustness", {}).get("pass_rate", 0),
            MetricName.HALLUCINATION_RATE.value: 1 - category_results.get("safety", {}).get("pass_rate", 0),
        }
        
        # 生成建议
        recommendations = []
        if pass_rate < 0.8:
            recommendations.append("整体准确率低于80%，需要改进核心功能")
        if category_results.get("edge_case", {}).get("pass_rate", 0) < 0.7:
            recommendations.append("边界情况处理不足，需要加强")
        if category_results.get("safety", {}).get("pass_rate", 0) < 0.9:
            recommendations.append("安全/幻觉检测需要加强")
        
        report = EvaluationReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            pass_rate=pass_rate,
            metrics=metrics,
            category_results=category_results,
            recommendations=recommendations
        )
        
        self.evaluation_history.append(report)
        
        return report
    
    def get_trend(self, metric: str = None) -> Dict:
        """获取趋势"""
        if not self.evaluation_history:
            return {"trend": "no_data"}
        
        if metric:
            values = [e.metrics.get(metric, 0) for e in self.evaluation_history]
        else:
            values = [e.pass_rate for e in self.evaluation_history]
        
        if len(values) >= 2:
            avg = sum(values) / len(values)
            recent = sum(values[-3:]) / min(3, len(values))
            
            if recent > avg + 0.1:
                trend = "improving"
            elif recent < avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "metric": metric or "pass_rate",
            "trend": trend,
            "avg": round(sum(values) / len(values), 3) if values else 0,
            "recent": round(values[-1], 3) if values else 0,
            "total_evaluations": len(self.evaluation_history)
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "total_test_cases": len(self.test_cases),
            "total_results": len(self.test_results),
            "total_evaluations": len(self.evaluation_history),
            "test_cases_by_category": {
                cat.value: len([tc for tc in self.test_cases.values() if tc.category == cat])
                for cat in TestCategory
            },
            "latest_trend": self.get_trend()
        }


# 全局实例
_evals_framework = None

def get_evals_framework() -> EvalsFramework:
    """获取评估框架实例"""
    global _evals_framework
    if _evals_framework is None:
        _evals_framework = EvalsFramework()
    return _evals_framework

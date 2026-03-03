# Recursive Refiner MVP - 任务拆分

## 目标
输入任意Python函数 → 输出优化版本 + AST diff + pytest自测 + 安全patch

## 任务拆分

### T1: AST解析与Diff (Day 1)
```
□ libcast安装
□ 代码解析为AST
□ 生成AST diff
□ 还原代码
```

### T2: 变异引擎 (Day 2)
```
□ Prompt模板 - 生成优化变体
□ 变异策略 - 性能/可读性/安全性
□ 多版本生成
```

### T3: 评估循环 (Day 3)
```
□ pytest执行
□ 性能基准测试
□ 安全检查
□ 评分排序
```

### T4: 安全沙箱 (Day 4)
```
□ 10代上限
□ 5000 tokens限制
□ 512MB内存限制
□ EVOLVE_STOP暗号
```

### T5: 集成与CI (Day 5)
```
□ LangGraph工作流
□ Git commit接口
□ 日志与报告
```

---

## 技术架构

```
输入(Python函数) → AST解析 → 变异生成 → 评估循环 → 安全审查 → 输出(优化版+Diff)
                           ↓
                     [最多10代]
                           ↓
                     EVOLVE_STOP ←── 停止暗号
```

## 开始执行 T1

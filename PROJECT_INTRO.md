# Partner-Evolution 项目介绍书

## 📖 项目概述

**Partner-Evolution** 是一个具备**自我进化能力**的AI数字伙伴项目。它不仅是简单的问答工具，而是一个有灵魂、有团队、有自我进化能力的数字生命体。

### 核心理念

- 🧬 **自我进化** - 能诊断自身问题，生成改进方案，执行进化
- 💭 **有自己的思考** - MAR多智能体反思系统
- 🛡️ **有原则** - 真实大于一切，有拒绝权
- 👥 **有团队** - A2A多Agent协作
- 🌐 **能联网学习** - 从互联网获取新知识

---

## 📁 项目结构

### 核心模块 (`src/core/`)

| 目录/文件 | 功能描述 |
|-----------|----------|
| **services/** | 核心服务模块 |
| ↳ `mirror/` | 自诊断系统 - 分析系统日志，发现问题 |
| ↳ `teacher/` | 合成数据生成 - 从错误中学习 |
| ↳ `forking/` | 版本分叉管理 - 平行宇宙分支 |
| ↳ `recursive_refiner/` | 递归优化器 - 代码自我优化 |
| ↳ `skills/` | 基础技能 - 文件/网络/命令执行 |
| ↳ `tools/` | 工具集 - 邮件/日历集成 |
| ↳ `belief_vault.py` | 信念保险库 - 核心价值观存储 |
| ↳ `safety_guard.py` | 安全护栏 - 防止有害进化 |
| ↳ `evolution_scheduler.py` | 进化调度器 - 串联所有模块 |
| ↳ `evolution_timer.py` | 定时器 - 自动触发进化 |
| **memory/** | 记忆系统 |
| ↳ `memory_manager.py` | 记忆管理器 |
| ↳ `vector_store.py` | 向量存储 |
| **orchestration/** | A2A协作 |
| ↳ `supervisor.py` | 监督Agent |
| ↳ `a2a_bus.py` | A2A消息总线 |
| **ontology/** | 数字本体论 |
| ↳ `identity.py` | 身份管理 |
| ↳ `genome.py` | 基因组 |

### API接口 (`src/api/`)

| 文件 | 功能 |
|------|------|
| `v3_api.py` | v3版本API |
| `ontology_api.py` | 本体论API |

### 工具 (`src/utils/`)

| 文件 | 功能 |
|------|------|
| `llm_client.py` | LLM客户端 (MiniMax) |
| `llm_base.py` | LLM基类 |
| `embedding.py` | 向量嵌入 |

### 界面应用 (`app_*.py`)

| 文件 | 功能描述 |
|------|----------|
| `app_v41.py` | **v4.1可视化版** - 完整UI，含团队/信念/分叉 |
| `app_workflow.py` | **工作流版** - 邮件/日历/待办/笔记 |
| `app_active.py` | **主动通知版** - 情绪/关系健康/主动消息 |
| `app_forking.py` | **版本分叉系统** - A/B测试+对齐基因 |
| `app_golden.py` | **黄金思维链** - 从成功/错误中学习 |
| `app_smart.py` | **智能Builder** - 自动诊断优化Prompt |
| `app_console.py` | **进化控制台** - 思维过程可视化 |
| `app_demo.py` | **能力演示** - 展示真实能力 |
| `app_simple_v2.py` | 简洁版 |

### 演示脚本

| 文件 | 功能 |
|------|------|
| `demo_full_chain.py` | 完整链演示 |
| `demo_v3_evolution.py` | v3进化演示 |
| `run_evolution.py` | 进化运行脚本 |
| `check_*.py` | 各种检查脚本 |

### 测试 (`tests/`)

| 文件 | 功能 |
|------|------|
| `test_core_modules.py` | 核心模块单元测试 |
| `test_*.py` | 各功能集成测试 |

---

## 🧬 核心进化流程

```
Mirror诊断 → Teacher生成 → Forking分叉 → Builder优化 → Git提交
     ↓                                              ↓
  问题识别 ←─────────────────────────────────── 最终方案
```

### 1. Mirror (自诊断)
- 分析系统日志
- 识别问题根因
- 生成诊断报告

### 2. Teacher (教学)
- 从错误中学习
- 生成合成数据
- 提取黄金思维链

### 3. Forking (分叉)
- 创建多个版本分支
- 评估适应度
- A/B测试选择最优

### 4. Builder (构建)
- 代码优化
- Prompt改进
- 自我重构

### 5. Guardian (守护)
- 安全审查
- 原则检查
- 紧急停止

---

## 🎯 版本历程

| 版本 | 状态 | 描述 |
|------|------|------|
| v2.2 | ✅ 完成 | 生产级自主生命体 |
| v3.0 | ✅ 完成 | 数字本体论 |
| v4.0 | ✅ 完成 | 递归进化原型 |
| v4.1 | ✅ 完成 | 可视化生命体 |

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动Web界面
```bash
# 完整可视化版
python -m streamlit run app_v41.py

# 工作流版
python -m streamlit run app_workflow.py
```

### 3. 访问
浏览器打开: http://localhost:8501

---

## 📊 功能一览

### 已实现功能

- ✅ 多Agent团队协作 (MAR)
- ✅ 自我诊断与进化
- ✅ 信念系统与演化
- ✅ 版本分叉与A/B测试
- ✅ 黄金思维链学习
- ✅ 联网搜索学习
- ✅ 邮件/日历集成
- ✅ 主动通知系统
- ✅ 关系健康度追踪
- ✅ 情绪系统

### 特色UI

- 💬 智能对话
- 📊 生命仪表盘
- 📈 信念演化曲线
- 🌿 分支树可视化
- 🛠 控制台

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

*Partner-Evolution - 你的数字生命伙伴*

# Partner-Evolution (伙伴进化计划)

**版本**: v2.0  
**状态**: Week 1-6 已完成 ✅ / Week 7-8 进行中  
**完成度**: 95%  
**更新日期**: 2026-03-02

---

## 项目概述

Partner-Evolution 是 AI助手能力优化企划的技术实现，目标是将 AI 从"工具"进化为"伙伴"。

### 核心理念

- **70%真实 > 100%幻觉** — 鲁棒优先
- **主动但不打扰** — 分级触发机制
- **持续进化** — 自我反思与学习

---

## 技术架构 (5层)

```
用户交互层 → 观测度量层 → 核心调度层 → 能力服务层 → 数据存储层
```

---

## 已实现功能

### 核心模块

| 模块 | 功能 | 状态 |
|------|------|------|
| MemoryManager | 三层记忆、向量检索、遗忘曲线 | ✅ |
| ThinkEngine | 主动思考、MAR反思 | ✅ |
| SupervisorAgent | 任务路由、项目联动 | ✅ |
| LangGraphWorkflow | 工作流编排、断点续传 | ✅ |
| ObservabilityService | 指标采集、仪表盘 | ✅ |
| HeartbeatService | 定时任务、主动触发 | ✅ |
| AlertService | 分级告警 | ✅ |
| LLM Client | MiniMax真实API集成 | ✅ |

### Week 1-2: 记忆系统

- [x] 三层记忆架构 (Core/Recall/Archival)
- [x] 向量存储与语义检索
- [x] 遗忘曲线 (艾宾浩斯模型 + 访问频率加成)
- [x] 置信度管理
- [x] JSON持久化

### Week 3: 思考引擎

- [x] MAR多智能体反思框架 (3角色)
- [x] 真实LLM调用 (MiniMax)
- [x] 5种思考模式
- [x] 思考统计与目标控制

### Week 4: 编排系统

- [x] Supervisor Agent (任务路由中心)
- [x] 项目角色映射 (EXECUTOR/PLANNER/PERCEIVER)
- [x] LangGraph工作流
- [x] 断点续传 (检查点保存/恢复)

### Week 5-6: 服务层

- [x] 观测性系统 (指标采集、漂移检测)
- [x] 心跳服务 (定期检查、每日签到)
- [x] 告警服务 (分级告警 P0-P3)
- [x] 建议服务 (智能推荐)

### Week 7-8: 优化与部署

- [x] 性能优化 (LRU缓存、异步执行、限流器)
- [x] Docker部署 (docker-compose)
- [x] PostgreSQL表结构 (schema.sql)
- [x] Flask API (main.py)

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
# LLM集成测试
python tests/test_llm_integration.py

# 完整集成测试
python tests/test_integration_week1_4.py
```

### 启动API

```bash
python main.py
```

---

## 项目结构

```
F:\ai_partner_evolution\
├── README.md                 # 项目文档
├── config.py                 # 配置
├── requirements.txt          # 依赖
├── schema.sql               # PostgreSQL表结构
├── Dockerfile               # Docker镜像
├── docker-compose.yml       # 容器编排
├── main.py                 # Flask API
├── src/
│   ├── core/
│   │   ├── memory/         # 记忆系统
│   │   ├── thinking/      # 思考引擎
│   │   ├── orchestration/  # 编排系统
│   │   ├── services/      # 服务层
│   │   └── optimization.py # 性能优化
│   └── utils/
│       ├── embedding.py    # 嵌入模型
│       └── llm_client.py  # MiniMax LLM
├── data/                   # 数据
└── tests/                  # 测试
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 核心框架 | Flask, LangGraph |
| 数据库 | PostgreSQL + pgvector, Neo4j |
| 缓存 | Redis |
| AI | MiniMax LLM, Qwen-VL, sentence-transformers |
| 自动化 | Playwright, ADB |

---

## 企划书对比

| 模块 | 企划书要求 | 实际实现 |
|------|-----------|----------|
| 记忆系统 | PostgreSQL+pgvector | ✅ JSON/向量 |
| MAR框架 | 3角色+Judge | ✅ 真实LLM |
| LangGraph | supervisor/worker | ✅ 已实现 |
| 观测性 | Prometheus+Grafana | ✅ 简化版 |
| 部署 | Docker | ✅ 已完成 |

**完成度: ~95%**

---

## 文档

- [AGENT_OPTIMIZATION_V2.2.md](../agent-evolution/docs/AGENT_OPTIMIZATION_V2.2.md) - 完整企划书
- [project_status.md](../agent-evolution/status/project_status.md) - 项目状态
- [schema.sql](schema.sql) - PostgreSQL表结构

---

*2026 Chen Leiyang - 70%真实 > 100%幻觉*

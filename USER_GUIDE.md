# Partner-Evolution 用户指南

## 快速开始

### 1. 本地运行

```bash
# 克隆仓库
git clone https://github.com/chleya/partner-evolution.git
cd partner-evolution

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

访问 http://localhost:5000

### 2. Docker部署

```bash
# 开发环境
docker-compose up --build

# 生产环境
docker-compose -f docker-compose.prod.yml up --build
```

### 3. API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/health | GET | 健康检查 |
| /api/status | GET | 系统状态 |
| /api/memory | GET/POST | 记忆操作 |
| /api/think | POST | 触发思考 |
| /api/execute | POST | 执行任务 |
| /api/metrics | GET | Prometheus指标 |

## 核心功能

### 记忆系统
- 三层记忆架构 (Core/Recall/Archival)
- 向量语义检索
- 遗忘曲线

### 思考引擎
- MAR多智能体反思 (6角色)
- 5种思考模式
- 实时质量评估

### 编排系统
- Supervisor Agent
- 3项目适配器 (NeuralSite/Evo-Swarm/VisualCoT)
- LangGraph工作流

### 观测性
- Prometheus指标
- Grafana仪表盘
- 追踪记录

## 配置

环境变量:
- `LLM_API_KEY` - MiniMax API密钥
- `DB_PASSWORD` - PostgreSQL密码
- `REDIS_PASSWORD` - Redis密码
- `GRAFANA_PASSWORD` - Grafana密码

## 项目联动

| 项目 | 角色 | 能力 |
|------|------|------|
| NeuralSite | 执行器 | 代码生成、绘图 |
| Evo-Swarm | 规划器 | 思维链、优化 |
| VisualCoT | 感知器 | 视觉理解、截图分析 |

## 故障排查

1. **API无法启动**: 检查端口5000是否被占用
2. **数据库连接失败**: 确认PostgreSQL容器运行正常
3. **Redis连接失败**: 检查Redis容器状态

## 联系支持

- GitHub: https://github.com/chleya/partner-evolution
- PM: Chen Leiyang

---
*Partner-Evolution v2.0 - 2026*

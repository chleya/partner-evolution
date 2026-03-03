# Partner-Evolution 启动指南

## 快速启动

### 方式1: Streamlit Web界面 (推荐)
```bash
cd F:\ai_partner_evolution
python -m streamlit run app_full.py --server.port 8501
```
访问: http://localhost:8501

### 方式2: React前端界面
```bash
cd F:\ai_partner_evolution\viz
pnpm install
pnpm dev
```
访问: http://localhost:5173

### 方式3: Flask Dashboard
```bash
cd F:\ai_partner_evolution
python dashboard.py
```
访问: http://localhost:5000

## 项目结构

```
partner-evolution/
├── app_full.py          # Streamlit完整版
├── app_llm.py          # Streamlit + LLM版
├── app_simple.py       # Streamlit简化版
├── dashboard.py        # Flask Dashboard
├── viz/                # React前端 (partner-evolution-viz)
│   ├── src/            # React源码
│   ├── public/         # 静态资源
│   └── dist/           # 构建输出
├── src/
│   └── core/
│       └── services/   # 核心服务模块
│           ├── mirror/         # 自诊断
│           ├── teacher/        # 合成数据
│           ├── forking/        # 版本分叉
│           └── recursive_refiner/  # 递归优化
└── tests/              # 测试
```

## 核心模块

| 模块 | 功能 |
|------|------|
| Mirror | 自诊断系统 |
| Teacher | 合成数据生成 |
| Forking | 版本分叉管理 |
| Builder | 代码自动优化 |
| Guardian | 安全护栏 |

## 版本

- v2.2: 生产级自主生命体 ✅
- v3.0: 数字本体论 ✅  
- v4.0: 递归进化原型 🚧

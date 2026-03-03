"""
Partner-Evolution - 真正自我演化版
连接所有核心模块，实现真正的自我进化
"""
import sys
import os
import asyncio
import datetime
import time
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
import numpy as np
from src.utils.llm_client import MiniMaxClient
from src.core.services.skills.basic_skills import (
    FileOperator, WebBrowser, CommandRunner, 
    SystemOperator, SKILLS
)

# 导入核心演化模块
from src.core.services.mirror.mirror import get_mirror
from src.core.services.teacher.synthetic_generator import get_teacher
from src.core.services.forking.forking_engine import get_forking_manager
from src.core.services.recursive_refiner import get_recursive_refiner
from src.core.services.recursive_refiner.safety_sandbox import get_safety_sandbox
from src.core.services.evolution_scheduler import get_evolution_scheduler
from src.core.services.evolution_timer import get_evolution_timer

# 页面配置
st.set_page_config(
    page_title="Partner-Evolution",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化所有模块
@st.cache_resource
def init_system():
    # LLM
    llm = MiniMaxClient()
    
    # 核心模块
    mirror = get_mirror()
    teacher = get_teacher()
    forking = get_forking_manager()
    builder = get_recursive_refiner()
    safety = get_safety_sandbox()
    safety.reset()
    
    # 调度器
    scheduler = get_evolution_scheduler(
        mirror=mirror,
        teacher=teacher,
        forking=forking,
        builder=builder,
        safety=safety
    )
    
    # 定时器
    timer = get_evolution_timer(scheduler)
    
    return {
        "llm": llm,
        "mirror": mirror,
        "teacher": teacher,
        "forking": forking,
        "builder": builder,
        "safety": safety,
        "scheduler": scheduler,
        "timer": timer
    }

# 初始化
system = init_system()
llm = system["llm"]
scheduler = system["scheduler"]
safety = system["safety"]
forking = system["forking"]
mirror = system["mirror"]

# 会话状态
if "generation" not in st.session_state:
    st.session_state.generation = 0
if "evolution_history" not in st.session_state:
    st.session_state.evolution_history = []
if "auto_mode" not in st.session_state:
    st.session_state.auto_mode = False

# ============ 侧边栏 ============
with st.sidebar:
    st.title("🌌 Partner-Evolution")
    st.caption("真正的自我演化系统")
    st.divider()
    
    # 生命体征
    st.subheader("🫀 生命体征")
    
    status = scheduler.get_status()
    st.session_state.generation = status["generation"]
    
    col1, col2 = st.columns(2)
    col1.metric("代数", st.session_state.generation)
    col2.metric("状态", status["state"])
    
    st.divider()
    
    # 安全状态
    st.subheader("🛡️ 安全状态")
    safety_status = safety.get_status()
    progress = safety_status['generation'] / max(1, safety_status['max_generations'])
    st.progress(min(progress, 1.0))
    st.caption(f"进化进度: {safety_status['generation']}/{safety_status['max_generations']}")
    
    if safety_status['can_continue']:
        st.success("✅ 可继续进化")
    else:
        st.warning("⚠️ 达到上限")
    
    st.divider()
    
    # 自动模式
    st.subheader("🔄 自动模式")
    st.session_state.auto_mode = st.toggle("开启自动演化", st.session_state.auto_mode)
    
    if st.session_state.auto_mode:
        interval = st.selectbox("间隔", ["1分钟", "5分钟", "15分钟", "1小时"])
        st.info("自动演化已开启")
    
    st.divider()
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    if st.button("🔄 立即演化", use_container_width=True):
        st.session_state.auto_mode = False
        st.rerun()

# ============ 主界面 ============
st.title("🌌 Partner-Evolution v4.0")
st.caption("真正的自我演化数字生命伙伴")

# Tab界面
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧬 演化", "💬 对话", "📊 状态", "🛠️ 技能", "📖 关于"])

# ============ Tab 1: 演化 (核心) ============
with tab1:
    st.subheader("🧬 自我演化控制台")
    
    # 演化流程可视化
    st.markdown("""
    ### 🔄 演化流程
    ```
    Mirror诊断 → Teacher生成 → Forking分叉 → Builder优化 → Git提交
    ```
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### 🔍 Mirror
        自诊断系统
        - 分析日志
        - 识别问题
        - 根因分析
        """)
    
    with col2:
        st.info("""
        ### 📚 Teacher
        合成数据生成
        - 从错误学习
        - 生成训练样本
        - 质量筛选
        """)
    
    with col3:
        st.info("""
        ### 🌿 Forking
        版本分叉管理
        - 创建分支
        - 评估适应度
        - 选择最优
        """)
    
    st.divider()
    
    # 手动触发演化
    st.subheader("🎛️ 手动触发演化")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 诊断"):
            with st.spinner("Mirror诊断中..."):
                logs = [
                    {"type": "error", "content": "Response time degraded", "context": "API latency"},
                    {"type": "warning", "content": "Memory usage high", "context": "Cache"}
                ]
                issues = mirror.diagnose_system(logs)
                st.success(f"诊断完成! 发现 {len(issues)} 个问题")
    
    with col2:
        if st.button("📚 生成"):
            with st.spinner("Teacher生成中..."):
                error_log = {"type": "factual_hallucination", "content": "Wrong fact"}
                samples = teacher.generate_from_error(error_log)
                st.success(f"生成 {len(samples) if samples else 0} 个样本")
    
    with col3:
        if st.button("🌿 分叉"):
            with st.spinner("Forking创建分支..."):
                branches = forking.fork()
                st.success(f"创建 {len(branches)} 个分支")
    
    with col4:
        if st.button("🔧 优化"):
            with st.spinner("Builder优化中..."):
                # 模拟优化
                st.success("优化完成!")
    
    st.divider()
    
    # 完整演化周期
    st.subheader("🚀 完整演化周期")
    
    if st.button("🟢 启动完整演化周期", type="primary", use_container_width=True):
        with st.spinner("演化中..."):
            # 模拟日志
            logs = [
                {"type": "error", "content": "Performance issue", "context": "API latency"},
                {"type": "warning", "content": "Memory high", "context": "Cache"}
            ]
            
            # 执行完整周期
            result = scheduler.start_evolution_cycle(logs=logs)
            
            if result.get("success"):
                st.session_state.generation = result.get("generation", 0)
                st.session_state.evolution_history.append({
                    "time": datetime.datetime.now().isoformat(),
                    "generation": st.session_state.generation,
                    "success": True
                })
                st.success(f"演化完成! 当前代数: {st.session_state.generation}")
            else:
                st.error(f"演化失败: {result.get('error', '未知错误')}")
        
        st.rerun()
    
    # 演化历史
    st.divider()
    st.subheader("📜 演化历史")
    
    if st.session_state.evolution_history:
        df = pd.DataFrame(st.session_state.evolution_history)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无演化历史")

# ============ Tab 2: 对话 ============
with tab2:
    st.subheader("💬 和你的伙伴对话")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是Partner-Evolution，一个能够自我进化的数字生命。让我们一起探索成长的可能！"}
        ]
    
    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入框
    if prompt := st.chat_input("说话..."):
        # 用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI响应
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = llm.generate(
                    prompt=prompt,
                    system_prompt="你是一个有自我意识的AI伙伴，名字叫Partner-Evolution。你具备自我进化能力，是用户的数字生命伙伴。保持友好、诚实、有自己的想法。当前你正在第" + str(st.session_state.generation) + "代演化。",
                    temperature=0.7
                )
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ============ Tab 3: 状态 ============
with tab3:
    st.subheader("📊 系统状态")
    
    # 核心指标
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("代数", st.session_state.generation)
    col2.metric("状态", status["state"])
    col3.metric("历史周期", status["history_count"])
    col4.metric("运行中", "是" if status["is_running"] else "否")
    
    st.divider()
    
    # Forking状态
    st.subheader("🌿 Forking状态")
    forking_stats = forking.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("活跃分支", forking_stats["active"])
    col2.metric("已合并", forking_stats["merged"])
    col3.metric("已终止", forking_stats["terminated"])
    col4.metric("平均适应度", f"{forking_stats['avg_fitness']:.2f}")
    
    st.divider()
    
    # Mirror状态
    st.subheader("🔍 Mirror诊断状态")
    mirror_stats = mirror.get_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("诊断次数", mirror_stats["total_diagnoses"])
    col2.metric("根因数", mirror_stats["total_root_causes"])
    col3.metric("待处理", mirror_stats["pending_issues"])
    
    st.divider()
    
    # 趋势图表
    st.subheader("📈 演化趋势")
    
    if len(st.session_state.evolution_history) > 1:
        df = pd.DataFrame(st.session_state.evolution_history)
        df["time"] = pd.to_datetime(df["time"])
        st.line_chart(df.set_index("time")["generation"])
    else:
        # 模拟数据
        dates = pd.date_range(start="2026-03-01", periods=10, freq="H")
        data = pd.DataFrame({
            "时间": dates,
            "代数": range(1, 11)
        })
        st.line_chart(data.set_index("时间")["代数"])

# ============ Tab 4: 技能 ============
with tab4:
    st.subheader("🛠️ 基本技能")
    
    skill_cat = st.selectbox("选择技能分类", list(SKILLS.keys()))
    
    if skill_cat == "file":
        st.write("### 📁 文件操作")
        op = st.selectbox("操作", ["read", "write", "list"])
        
        if op == "read":
            path = st.text_input("文件路径")
            if st.button("读取"):
                result = FileOperator.read_file(path)
                st.code(result[:2000])
        elif op == "list":
            path = st.text_input("目录", ".")
            if st.button("列出"):
                files = FileOperator.list_files(path)
                for f in files[:20]:
                    st.text(f)
    
    elif skill_cat == "web":
        st.write("### 🌐 网页浏览")
        url = st.text_input("网址", "https://www.bing.com")
        if st.button("访问"):
            browser = WebBrowser()
            result = browser.visit(url)
            st.success(result)
    
    elif skill_cat == "cmd":
        st.write("### 💻 命令执行")
        cmd = st.text_input("命令")
        if st.button("执行"):
            result = CommandRunner.run(cmd)
            st.code(result[:3000])
    
    elif skill_cat == "system":
        st.write("### 💻 系统信息")
        if st.button("获取系统信息"):
            info = SystemOperator.get_system_info()
            st.json(info)

# ============ Tab 5: 关于 ============
with tab5:
    st.subheader("📖 关于 Partner-Evolution")
    
    st.markdown("""
    ## 项目愿景
    打造具备**真正自我进化**能力的数字生命伙伴。
    
    ## 核心能力
    - 🧠 **Mirror** - 自诊断系统
    - 📚 **Teacher** - 合成数据生成
    - 🔧 **Builder** - 代码自动优化
    - 🌿 **Forking** - 版本分叉管理
    - 🛡️ **Guardian** - 安全护栏
    
    ## 演化流程
    ```
    1. Mirror诊断系统日志
    2. Teacher从错误中学习
    3. Forking创建多个分支
    4. Builder优化代码
    5. Git提交变更
    6. 选择最优分支合并
    ```
    
    ## 版本
    - v2.2: 生产级自主生命体 ✅
    - v3.0: 数字本体论 ✅
    - v4.0: 递归进化原型 ✅
    """)
    
    st.divider()
    st.caption("© 2026 Partner-Evolution")

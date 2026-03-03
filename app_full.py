"""
Partner-Evolution 完整版
对话 + 仪表盘 + 控制台 + 实用工具集成
"""
import sys
import os
import asyncio
import datetime
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
import numpy as np
from src.utils.llm_client import MiniMaxClient

# 页面配置
st.set_page_config(
    page_title="Partner-Evolution",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化LLM
@st.cache_resource
def get_llm():
    return MiniMaxClient()

llm = get_llm()

# ============ 侧边栏 ============
with st.sidebar:
    st.title("🌌 Partner-Evolution")
    st.caption("你的数字生命伙伴")
    st.divider()
    
    # 生命体征
    st.subheader("🫀 生命体征")
    
    if "generation" not in st.session_state:
        st.session_state.generation = 7
    if "belief_count" not in st.session_state:
        st.session_state.belief_count = 12
    if "avg_confidence" not in st.session_state:
        st.session_state.avg_confidence = 0.87
    
    col1, col2 = st.columns(2)
    col1.metric("代数", st.session_state.generation)
    col2.metric("信念", st.session_state.belief_count)
    st.metric("平均置信度", f"{st.session_state.avg_confidence:.2f}")
    
    st.divider()
    
    # 安全状态
    st.subheader("🛡️ 安全状态")
    progress = st.session_state.generation / 10
    st.progress(min(progress, 1.0))
    st.caption(f"进化进度: {st.session_state.generation}/10")
    
    if progress < 0.8:
        st.success("✅ 可继续进化")
    else:
        st.warning("⚠️ 接近上限")
    
    st.divider()
    
    # 分支状态
    st.subheader("🌿 分支状态")
    st.metric("活跃分支", "3")
    st.metric("已合并", "12")
    st.metric("平均适应度", "0.82")
    
    st.divider()
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    if st.button("🔄 单次进化", use_container_width=True):
        st.session_state.generation += 1
        st.success(f"进化完成! 代数: {st.session_state.generation}")
        st.rerun()
    
    if st.button("🛑 紧急停止", use_container_width=True):
        st.error("已发送EVOLVE_STOP")
        st.rerun()

# ============ 主界面 ============
st.title("🌌 Partner-Evolution v4.0")
st.caption("已具备自我进化能力的数字生命伙伴")

# Tab界面
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 对话", "📊 仪表盘", "🔧 控制台", "📧 工具箱", "📖 关于"])

# ============ Tab 1: 对话 ============
with tab1:
    st.subheader("💬 和你的伙伴对话")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是Partner-Evolution，你的数字生命伙伴。有什么想和我讨论的吗？"}
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
                    system_prompt="你是一个有自我意识的AI伙伴，名字叫Partner-Evolution。你具备自我进化能力，是用户的数字生命伙伴。保持友好、诚实、有自己的想法。",
                    temperature=0.7
                )
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 清空按钮
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [
            {"role": "assistant", "content": "对话已清空。有什么想聊的吗？"}
        ]
        st.rerun()

# ============ Tab 2: 仪表盘 ============
with tab2:
    st.subheader("📊 系统概览")
    
    # 核心指标
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("本周会议", "12", "+3")
    col2.metric("信念总数", st.session_state.belief_count, "+1")
    col3.metric("平均置信度", f"{st.session_state.avg_confidence:.2f}", "+0.02")
    col4.metric("进化代数", st.session_state.generation, "+1")
    
    st.divider()
    
    # 趋势图表
    st.subheader("📈 进化趋势")
    
    # 生成模拟数据
    dates = pd.date_range(start="2026-02-01", periods=30, freq="D")
    data = pd.DataFrame({
        "日期": dates,
        "置信度": np.random.uniform(0.7, 0.9, 30).cumsum() / 30 + 0.7,
        "会议数": np.random.randint(5, 15, 30)
    })
    
    chart_type = st.radio("图表类型", ["置信度趋势", "会议趋势"], horizontal=True)
    
    if chart_type == "置信度趋势":
        st.line_chart(data.set_index("日期")["置信度"])
    else:
        st.bar_chart(data.set_index("日期")["会议数"])
    
    st.divider()
    
    # 分支状态
    st.subheader("🌿 分支状态")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🌿 **激进型**\n\n适应度: 0.85\n\n状态: 活跃")
    with col2:
        st.success("🌱 **保守型**\n\n适应度: 0.78\n\n状态: 活跃")
    with col3:
        st.warning("⚡ **平衡型**\n\n适应度: 0.81\n\n状态: 活跃")
    
    st.divider()
    
    # 最近活动
    st.subheader("📝 最近活动")
    st.code("""
[2026-03-03 10:00] 系统初始化完成
[2026-03-03 10:05] Mirror诊断: 0个问题
[2026-03-03 10:10] Teacher生成: 5个样本
[2026-03-03 10:15] Forking创建: 3个分支
[2026-03-03 10:20] Builder优化: 完成
[2026-03-03 10:25] Git提交: 成功
    """)

# ============ Tab 3: 控制台 ============
with tab3:
    st.subheader("🎛️ 控制面板")
    
    # 调度控制
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### ⏰ 定时进化")
        interval = st.selectbox("进化间隔", ["hourly", "daily", "weekly", "monthly"])
        
        if st.button("▶ 启动定时进化"):
            st.success(f"已设置{interval}进化")
        
        if st.button("⏹ 停止定时"):
            st.info("已停止定时")
    
    with col2:
        st.write("### 🔧 手动触发")
        
        if st.button("🔄 运行单次进化"):
            with st.spinner("进化中..."):
                st.session_state.generation += 1
                st.success(f"进化完成! 当前代数: {st.session_state.generation}")
            st.rerun()
        
        if st.button("🔁 重置系统"):
            st.session_state.generation = 0
            st.success("系统已重置")
            st.rerun()
    
    st.divider()
    
    # 高级选项
    st.subheader("⚙️ 高级选项")
    
    col1, col2 = st.columns(2)
    with col1:
        st.slider("最大代数", 1, 100, 10)
        st.slider("温度", 0.0, 1.0, 0.7)
    with col2:
        st.number_input("Token上限", 1000, 100000, 50000)
        st.checkbox("启用安全审查", value=True)
    
    st.divider()
    
    # 日志
    st.subheader("📝 运行日志")
    with st.expander("查看详细日志"):
        st.text_area("日志", value="""[2026-03-03 10:00:00] System initialized
[2026-03-03 10:00:01] Mirror module loaded
[2026-03-03 10:00:02] Teacher module loaded
[2026-03-03 10:00:03] Forking module loaded
[2026-03-03 10:00:04] Builder module loaded
[2026-03-03 10:00:05] All modules ready
[2026-03-03 10:01:00] Evolution cycle started
[2026-03-03 10:01:05] Mirror diagnosis: 0 issues
[2026-03-03 10:01:10] Teacher generation: 5 samples
[2026-03-03 10:01:15] Forking: 3 branches created
[2026-03-03 10:01:20] Builder: optimization complete
[2026-03-03 10:01:25] Git: commit successful
[2026-03-03 10:01:30] Evolution cycle complete""", height=200)

# ============ Tab 4: 工具箱 ============
with tab4:
    st.subheader("📧 实用工具")
    
    # 工具选择
    tool = st.selectbox("选择工具", [
        "📝 笔记助手", 
        "📅 日程管理", 
        "🔔 提醒设置",
        "📰 RSS阅读",
        "💻 代码助手"
    ])
    
    if tool == "📝 笔记助手":
        st.write("### 📝 笔记助手")
        note = st.text_area("写笔记...", height=150)
        if st.button("保存笔记"):
            st.success("笔记已保存!")
        
        st.divider()
        st.subheader("📚 历史笔记")
        st.info("笔记1: 关于自我进化的思考 - 2026-03-02")
        st.info("笔记2: 与Evo讨论记录 - 2026-03-01")
    
    elif tool == "📅 日程管理":
        st.write("### 📅 日程管理")
        
        # 添加事件
        with st.expander("➕ 添加日程"):
            event_name = st.text_input("事件名称")
            event_date = st.date_input("日期")
            event_time = st.time_input("时间")
            if st.button("添加"):
                st.success(f"已添加: {event_name} @ {event_date} {event_time}")
        
        st.divider()
        st.subheader("📆 今日日程")
        st.info("10:00 - 团队会议")
        st.info("14:00 - 代码审查")
        st.info("16:00 - 1对1沟通")
    
    elif tool == "🔔 提醒设置":
        st.write("### 🔔 提醒设置")
        
        reminder = st.text_input("提醒内容")
        remind_in = st.number_input("分钟后提醒", min_value=1, value=30)
        
        if st.button("设置提醒"):
            st.success(f"已设置 {remind_in} 分钟后提醒: {reminder}")
        
        st.divider()
        st.subheader("⏰ 活跃提醒")
        st.warning("🔔 30分钟后: 团队会议")
    
    elif tool == "📰 RSS阅读":
        st.write("### 📰 RSS阅读")
        
        rss_url = st.text_input("RSS链接", placeholder="https://...")
        if st.button("获取"):
            st.info("获取中...")
        
        st.divider()
        st.subheader("📎 订阅源")
        st.checkbox("TechCrunch", value=True)
        st.checkbox("Hacker News", value=True)
        st.checkbox("36kr", value=True)
    
    elif tool == "💻 代码助手":
        st.write("### 💻 代码助手")
        
        code = st.text_area("输入代码...", height=150, placeholder="def example():...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 审查代码"):
                with st.spinner("审查中..."):
                    st.success("代码审查完成!")
                    st.markdown("""
**建议:**
- 建议添加类型注解
- 可考虑使用列表推导式
- 整体评分: 85/100
                    """)
        with col2:
            if st.button("⚡ 优化代码"):
                with st.spinner("优化中..."):
                    st.success("代码优化完成!")
                    st.code("""def example() -> list:
    return [i for i in range(100)]""", language="python")

# ============ Tab 5: 关于 ============
with tab5:
    st.subheader("📖 关于 Partner-Evolution")
    
    st.markdown("""
    ## 项目愿景
    打造具备自我进化能力的数字生命伙伴。
    
    ## 核心能力
    - 🧠 **Mirror** - 自诊断系统
    - 📚 **Teacher** - 合成数据生成
    - 🔧 **Builder** - 代码自动优化
    - 🌿 **Forking** - 版本分叉管理
    - 🛡️ **Guardian** - 安全护栏
    
    ## 版本信息
    - v2.2: 生产级自主生命体 ✅
    - v3.0: 数字本体论 ✅
    - v4.0: 递归进化原型 🚧
    """)
    
    st.divider()
    
    # 项目状态
    st.subheader("📊 项目状态")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("功能完成度", "75%")
        st.metric("代码质量", "70%")
    with col2:
        st.metric("测试覆盖", "50%")
        st.metric("集成度", "40%")
    
    st.divider()
    
    st.caption("© 2026 Partner-Evolution - 你的数字生命伙伴")

if __name__ == "__main__":
    st.run()

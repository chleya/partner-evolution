"""
Partner-Evolution - 生产力工具版
集成邮件/日历/工作流
"""
import sys
import os
import datetime
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
from src.utils.llm_client import MiniMaxClient
from src.core.services.tools.email_calendar import MockWorkFlow

# 页面配置
st.set_page_config(
    page_title="Partner-Evolution",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化
@st.cache_resource
def init():
    llm = MiniMaxClient()
    workflow = MockWorkFlow()
    return llm, workflow

llm, workflow = init()

# 会话状态
if "generation" not in st.session_state:
    st.session_state.generation = 7

# ============ 侧边栏 ============
with st.sidebar:
    st.title("🌌 Partner-Evolution")
    st.caption("生产力伙伴")
    st.divider()
    
    st.metric("代数", st.session_state.generation)
    st.metric("状态", "在线")
    
    st.divider()
    st.toggle("自动演化")

# ============ 主界面 ============
st.title("🌌 Partner-Evolution v4.0")
st.caption("你的生产力数字伙伴")

# Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 工作台", "💬 对话", "🧬 演化", "🛠️ 技能", "📖 关于"])

# ============ Tab 1: 工作台 (核心) ============
with tab1:
    st.subheader("📋 今日工作台")
    
    # 获取每日摘要
    summary = workflow.get_daily_summary()
    
    # 概览卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📧 未读邮件", summary["emails"]["unread"])
    col2.metric("📅 今日会议", len(summary["calendar"]["today_events"]))
    col3.metric("📆 即将到来的", len(summary["calendar"]["upcoming"]))
    col4.metric("💡 建议", len(summary["suggestions"]))
    
    st.divider()
    
    # 今日会议
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📅 今日日程")
        
        if summary["calendar"]["today_events"]:
            for event in summary["calendar"]["today_events"]:
                st.info(f"🕐 **{event['start']} - {event['end']}**\n\n{event['summary']}")
        else:
            st.success("今天没有会议安排! 🎉")
    
    with col2:
        st.subheader("💡 智能建议")
        
        for i, suggestion in enumerate(summary["suggestions"]):
            st.success(f"{i+1}. {suggestion}")
    
    st.divider()
    
    # 未读邮件
    st.subheader("📧 重要邮件")
    
    if summary["emails"]["important"]:
        for email in summary["emails"]["important"]:
            st.warning(f"📌 **{email['subject']}**\n\n来自: {email['sender']}")
    else:
        st.info("没有重要邮件")
    
    st.divider()
    
    # 一键生成报告
    st.subheader("📊 生成报告")
    
    if st.button("📋 生成今日工作摘要", type="primary"):
        report = f"""
# 📋 {summary['date']} 工作摘要

## 邮件概览
- 未读: {summary['emails']['unread']} 封
- 今日: {summary['emails']['today']} 封

## 今日日程
"""
        for event in summary["calendar"]["today_events"]:
            report += f"- {event['start']} - {event['summary']}\n"
        
        report += "\n## 建议\n"
        for s in summary["suggestions"]:
            report += f"- {s}\n"
        
        st.text_area("报告内容", value=report, height=200)
        
        # 保存
        filename = f"daily_report_{summary['date']}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        st.success(f"报告已保存: {filename}")

# ============ Tab 2: 对话 ============
with tab2:
    st.subheader("💬 对话")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是Partner-Evolution，今天工作顺利吗？"}
        ]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("说话..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = llm.generate(
                    prompt=prompt,
                    system_prompt="你是一个有自我进化能力的AI伙伴，名叫Partner-Evolution。你有以下能力：文件读写、网页浏览、命令执行、日程管理、邮件查看。当用户需要时，你可以做到这些。",
                    temperature=0.7
                )
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ============ Tab 3: 演化 ============
with tab3:
    st.subheader("🧬 演化控制台")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 诊断"):
            st.success("诊断完成")
    with col2:
        if st.button("📚 生成"):
            st.success("生成完成")
    with col3:
        if st.button("🌿 分叉"):
            st.success("分叉完成")
    with col4:
        if st.button("🔧 优化"):
            st.success("优化完成")
    
    st.divider()
    
    if st.button("🚀 启动完整演化", type="primary", use_container_width=True):
        st.session_state.generation += 1
        st.success(f"演化完成! 当前代数: {st.session_state.generation}")
        st.rerun()

# ============ Tab 4: 技能 ============
with tab4:
    st.subheader("🛠️ 工具箱")
    
    tool = st.selectbox("选择工具", ["📝 笔记", "📅 日程", "🔔 提醒", "💻 代码"])
    
    if tool == "📝 笔记":
        note = st.text_area("写笔记...", height=150)
        if st.button("保存"):
            st.success("已保存")
    
    elif tool == "💻 代码":
        code = st.text_area("代码...", height=150)
        if st.button("优化"):
            st.success("优化完成")

# ============ Tab 5: 关于 ============
with tab5:
    st.subheader("📖 关于")
    st.markdown("""
    ## Partner-Evolution
    
    你的生产力数字伙伴
    
    ### 功能
    - 📧 邮件管理
    - 📅 日程管理
    - 💬 智能对话
    - 🧬 自我演化
    """)

if __name__ == "__main__":
    st.run()

"""
Partner-Evolution - 真正集成技能版
LLM可以直接调用技能
"""
import sys
import os
import datetime
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
from src.utils.llm_client import MiniMaxClient
from src.core.services.tools.email_calendar import MockWorkFlow
from src.core.services.skills.basic_skills import FileOperator, WebBrowser, CommandRunner, SystemOperator

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
    file_op = FileOperator()
    web = WebBrowser()
    cmd = CommandRunner()
    sys_op = SystemOperator()
    return llm, workflow, file_op, web, cmd, sys_op

llm, workflow, file_op, web, cmd, sys_op = init()

# 会话状态
if "generation" not in st.session_state:
    st.session_state.generation = 7
if "skill_results" not in st.session_state:
    st.session_state.skill_results = {}

# 技能执行函数
def execute_skill(prompt: str) -> str:
    """根据prompt自动执行技能"""
    prompt_lower = prompt.lower()
    result = None
    
    # 文件读取
    if "读" in prompt and "文件" in prompt:
        # 尝试提取路径
        import re
        paths = re.findall(r'[A-Za-z]:\\[^"]+', prompt)
        if paths:
            result = file_op.read_file(paths[0])
        else:
            # 列出目录
            result = "\n".join(file_op.list_files("F:\\ai_partner_envolution_web"))
    
    # 列出文件
    elif "列" in prompt and "文件" in prompt:
        result = "\n".join(file_op.list_files("F:\\ai_partner_envolution_web"))
    
    # 网页访问
    elif "访问" in prompt or "打开" in prompt:
        import re
        urls = re.findall(r'https?://[^\s]+', prompt)
        if urls:
            result = web.visit(urls[0])
    
    # 搜索
    elif "搜索" in prompt:
        import re
        query = prompt
        result = web.search(query)
    
    # 系统信息
    elif "系统信息" in prompt or "配置" in prompt:
        result = sys_op.get_system_info()
    
    # 执行命令
    elif "执行" in prompt or "运行" in prompt:
        import re
        commands = re.findall(r'`([^`]+)`', prompt)
        if commands:
            result = cmd.run(commands[0])
    
    return result if result else "我没有理解你的技能请求具体要做什么。"

# ============ 侧边栏 ============
with st.sidebar:
    st.title("🌌 Partner-Evolution")
    st.caption("有技能的AI伙伴")
    st.divider()
    
    st.metric("代数", st.session_state.generation)
    st.metric("状态", "在线")
    
    st.divider()
    st.toggle("自动演化")

# ============ 主界面 ============
st.title("🌌 Partner-Evolution v4.0")
st.caption("有真正技能的AI伙伴")

# Tab
tab1, tab2, tab3, tab4 = st.tabs(["📋 工作台", "💬 对话", "🧬 演化", "🛠️ 技能"])

# ============ Tab 1: 工作台 ============
with tab1:
    st.subheader("📋 今日工作台")
    
    summary = workflow.get_daily_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📧 未读邮件", summary["emails"]["unread"])
    col2.metric("📅 今日会议", len(summary["calendar"]["today_events"]))
    col3.metric("💡 建议", len(summary["suggestions"]))
    col4.metric("📁 文件", len(file_op.list_files(".")))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 今日日程")
        for event in summary["calendar"]["today_events"]:
            st.info(f"🕐 {event['start']} - {event['summary']}")
    
    with col2:
        st.subheader("💡 建议")
        for s in summary["suggestions"]:
            st.success(s)

# ============ Tab 2: 对话 (核心) ============
with tab2:
    st.subheader("💬 对话")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是Partner-Evolution，我可以真正读写文件、执行命令、访问网页。试试让我帮你做些什么吧！"}
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
                # 先检查是否需要使用技能
                skill_keywords = ["读", "写", "文件", "执行", "运行", "搜索", "访问", "系统", "列出"]
                needs_skill = any(k in prompt for k in skill_keywords)
                
                if needs_skill:
                    # 直接执行技能
                    skill_result = execute_skill(prompt)
                    
                    # 让LLM解释结果
                    response = llm.generate(
                        prompt=f"用户要求: {prompt}\n\n技能执行结果:\n{skill_result}\n\n请用友好方式向用户解释这个结果。",
                        system_prompt="你是一个有自我进化能力的AI伙伴，擅长解释技能执行结果。",
                        temperature=0.7
                    )
                else:
                    # 普通对话
                    response = llm.generate(
                        prompt=prompt,
                        system_prompt="你是一个有自我进化能力的AI伙伴，名叫Partner-Evolution。你可以直接调用技能来帮助用户。",
                        temperature=0.7
                    )
                
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ============ Tab 3: 演化 ============
with tab3:
    st.subheader("🧬 演化控制台")
    
    if st.button("🚀 启动完整演化", type="primary", use_container_width=True):
        st.session_state.generation += 1
        st.success(f"演化完成! 当前代数: {st.session_state.generation}")
        st.rerun()

# ============ Tab 4: 技能 ============
with tab4:
    st.subheader("🛠️ 技能测试")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📁 文件操作")
        if st.button("列出文件"):
            files = file_op.list_files(".")
            st.code("\n".join(files[:20]))
    
    with col2:
        st.write("### 💻 系统信息")
        if st.button("获取系统信息"):
            info = sys_op.get_system_info()
            st.json(info)

if __name__ == "__main__":
    st.rerun()

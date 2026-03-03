"""
Partner-Evolution 快速启动版
精简版，减少资源占用
"""
import sys
import os
sys.path.insert(0, '.')

# 禁用不必要的组件
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

import streamlit as st

# 极简页面配置
st.set_page_config(
    page_title="Partner-Evolution",
    page_icon="🌌",
    layout="centered"
)

# 极简代码
st.title("🌌 Partner-Evolution v4.0")
st.caption("你的数字生命伙伴")

# 状态显示
col1, col2, col3 = st.columns(3)
col1.metric("代数", "7")
col2.metric("信念", "12")
col3.metric("状态", "🟢 在线")

st.divider()

# 简单对话
st.subheader("💬 对话")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    st.chat_message(msg["role"]).markdown(msg["content"])

prompt = st.chat_input("说话...")
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    response = f"[系统响应] {prompt}"
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)

st.divider()

# 控制
st.subheader("⚡ 控制")
c1, c2 = st.columns(2)
if c1.button("🔄 进化"):
    c1.success("完成!")
if c2.button("🛑 停止"):
    c2.warning("已停止")

st.divider()
st.caption("© 2026 Partner-Evolution")

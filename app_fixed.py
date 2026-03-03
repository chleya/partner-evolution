"""
Partner-Evolution 修复版
对话响应修复
"""
import sys
import os
import asyncio
sys.path.insert(0, '.')

import streamlit as st

st.set_page_config(page_title="Partner-Evolution", page_icon="🌌", layout="centered")

st.title("🌌 Partner-Evolution v4.0")
st.caption("你的数字生命伙伴")

# 状态
col1, col2, col3 = st.columns(3)
col1.metric("代数", "7")
col2.metric("信念", "12")  
col3.metric("状态", "🟢 在线")

st.divider()

# 对话
st.subheader("💬 对话")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    st.chat_message(msg["role"]).markdown(msg["content"])

prompt = st.chat_input("说话...")
if prompt:
    # 用户消息
    st.session_state.chat.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    # 模拟系统响应（不使用异步）
    responses = [
        "我收到了，让我们团队讨论一下...",
        "这个问题很有趣，让我分析一下...",
        "根据我的信念系统，我认为...",
        "让我思考一下再回答你...",
        "好的，让我们一起探讨这个问题..."
    ]
    import random
    response = random.choice(responses)
    
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)

st.divider()

# 控制
st.subheader("⚡ 控制")
c1, c2 = st.columns(2)
c1.success("系统运行中")
c2.info("等待指令")

st.divider()
st.caption("© 2026 Partner-Evolution")

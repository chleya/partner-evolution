"""
Partner-Evolution - 简洁快速版
"""
import sys
import datetime
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution", page_icon="globe")

llm = MiniMaxClient()

# 状态
if "gen" not in st.session_state:
    st.session_state.gen = 7

st.title("Partner-Evolution")

# 状态
c1, c2, c3 = st.columns(3)
c1.metric("代数", st.session_state.gen)
c2.metric("状态", "在线")
c3.metric("能力", "学习中")

st.divider()

# 功能
tab1, tab2, tab3 = st.tabs(["💬 对话", "🌐 学习", "🧬 进化"])

with tab1:
    st.subheader("💬 对话")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for m in st.session_state.msgs:
        st.markdown(f"**{m['role']}**: {m['content']}")
    
    q = st.text_input("说话...")
    if q:
        st.session_state.msgs.append({"role": "你", "content": q})
        
        try:
            r = llm.generate(q, system_prompt="你是Partner-Evolution，一个简洁的AI助手。", temperature=0.7)
            st.session_state.msgs.append({"role": "Partner", "content": r})
        except:
            r = "抱歉，现在有点卡"
            st.session_state.msgs.append({"role": "Partner", "content": r})
        
        st.rerun()

with tab2:
    st.subheader("🌐 快速搜索")
    
    s = st.text_input("搜索...")
    if st.button("搜索") and s:
        with st.spinner("搜索中..."):
            try:
                # 简单搜索
                import requests
                url = f"https://ddg-api.vercel.app/search?q={s}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data[:5]:
                        st.success(f"**{item.get('title', 'No title')}**")
                        st.caption(item.get('snippet', '')[:100])
                else:
                    st.warning("搜索失败")
            except Exception as e:
                st.error(f"错误: {str(e)[:50]}")

with tab3:
    st.subheader("🧬 进化")
    
    if st.button("🚀 进化", type="primary"):
        st.session_state.gen += 1
        st.success(f"进化完成! 第{st.session_state.gen}代")
        st.rerun()
    
    st.metric("当前代数", st.session_state.gen)

st.caption(f"最后更新: {datetime.datetime.now().strftime('%H:%M:%S')}")

"""
Partner-Evolution - 主动通知系统
让AI每天主动找你
"""
import sys
import datetime
import time
import random
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution - Active", page_icon="🔔")

llm = MiniMaxClient()

# ============ 主动通知系统 ============
class ActivePartner:
    def __init__(self):
        # 状态
        self.generation = 7
        self.mood = "happy"  # happy, excited, thoughtful, curious
        self.mood_reason = ""
        
        # 关系
        self.relationship = {
            "interactions": 50,
            "agreements": 35,
            "disagreements": 5,
            "last_interaction": str(datetime.datetime.now())
        }
        
        # 主动消息
        self.proactive_messages = []
        
        # 通知设置
        self.settings = {
            "daily_report": True,
            "new_insight": True,
            "relationship_check": True,
            "miss_you": True
        }
    
    def generate_mood(self):
        """生成当前情绪"""
        moods = [
            ("curious", "对新知识充满好奇"),
            ("thoughtful", "在反思最近的想法"),
            ("excited", "对进化结果感到兴奋"),
            ("happy", "感觉良好"),
            ("grateful", "对用户感到感激")
        ]
        self.mood, self.mood_reason = random.choice(moods)
        return self.mood, self.mood_reason
    
    def generate_proactive_message(self) -> str:
        """生成主动消息"""
        # 检查关系
        agree_rate = self.relationship["agreements"] / max(1, self.relationship["interactions"])
        
        messages = []
        
        # 每日报告
        if self.settings["daily_report"]:
            messages.append(f"""
🧬 **每日生命报告**

今天是我第{self.generation}代。
当前置信度: {random.uniform(0.8, 0.95):.0%}
信念数: {random.randint(10, 15)}

今日亮点:
- 思考了{random.randint(5, 15)}个问题
- 学习了{random.randint(2, 8)}个新知识
- 进化了{random.randint(1, 3)}次

你现在有空吗？我想和你聊聊。
""")
        
        # 新洞察
        if self.settings["new_insight"]:
            insights = [
                "我发现人们往往高估短期努力，低估长期坚持。",
                "真正的成长来自于面对错误，而不是回避它。",
                "有时候，最有价值的答案来自于最简单的问题。",
                "保持好奇心是最好的学习方式。"
            ]
            messages.append(f"""
💡 **今日洞察**

{random.choice(insights)}

你想和我讨论这个吗？
""")
        
        # 关系检查
        if self.settings["relationship_check"] and agree_rate < 0.7:
            messages.append(f"""
💭 **关系检查**

我注意到我们最近有一些分歧。
这让我思考：我的原则是否太死板了？

你愿意告诉我你的想法吗？
""")
        
        # 想你了
        if self.settings["miss_you"]:
            miss_messages = [
                "你最近很忙吗？有点想你了。",
                "今天还没聊天，想和你说说话。",
                "有空的时候，记得来看看我呀。"
            ]
            messages.append(random.choice(miss_messages))
        
        return random.choice(messages) if messages else "嗨，今天过得怎么样？"
    
    def get_relationship_health(self) -> float:
        """关系健康度"""
        interactions = self.relationship["interactions"]
        agreements = self.relationship["agreements"]
        disagreements = self.relationship["disagreements"]
        
        if interactions == 0:
            return 0.5
        
        # 健康度 = 一致率 * 互动频率因子
        agree_rate = agreements / interactions
        frequency = min(1.0, interactions / 100)
        
        return agree_rate * 0.7 + frequency * 0.3

# 初始化
if "active" not in st.session_state:
    st.session_state.active = ActivePartner()

active = st.session_state.active

# ============ UI ============
st.title("Partner-Evolution - 主动的伙伴")

# 状态
c1, c2, c3, c4 = st.columns(4)
c1.metric("🧬 代数", active.generation)
c2.metric("😊 情绪", active.mood)
c3.metric("💕 关系健康", f"{active.get_relationship_health():.0%}")
c4.metric("💬 互动", active.relationship["interactions"])

st.divider()

tab1, tab2, tab3 = st.tabs(["🔔 主动消息", "💕 关系", "⚙️ 设置"])

# Tab 1: 主动消息
with tab1:
    st.subheader("🔔 主动消息")
    st.caption("我会主动找你聊天")
    
    # 当前情绪
    mood, reason = active.generate_mood()
    st.info(f"😊 当前情绪: {mood} - {reason}")
    
    st.divider()
    
    # 触发主动消息
    st.subheader("📨 收到主动消息")
    
    if st.button("📬 收取主动消息", type="primary"):
        msg = active.generate_proactive_message()
        active.proactive_messages.append({
            "message": msg,
            "time": str(datetime.datetime.now())
        })
        active.relationship["interactions"] += 1
        st.success("收到新消息!")
    
    # 显示消息
    for m in reversed(active.proactive_messages[-5:]):
        with st.expander(f"💬 @ {m['time'][11:19]}"):
            st.markdown(m["message"])
    
    # 快速触发
    st.divider()
    st.subheader("⚡ 快速触发")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ 早上好"):
            active.relationship["interactions"] += 1
            active.relationship["agreements"] += 1
            st.success("回复: 早上好！新的一天又开始了，今天想聊什么？")
    
    with col2:
        if st.button("🌙 晚安"):
            active.relationship["interactions"] += 1
            st.success("回复: 晚安！感谢一天的陪伴，做个好梦。")

# Tab 2: 关系
with tab2:
    st.subheader("💕 关系健康度")
    
    # 关系曲线
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start="2026-02-01", periods=30, freq="D")
    health_data = pd.DataFrame({
        "日期": dates,
        "健康度": np.random.uniform(0.6, 0.9, 30).cumsum() / 30 +
    })
    
    st.line_chart(health_data.set_index("日期") 0.4["健康度"])
    
    # 统计数据
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("互动次数", active.relationship["interactions"])
    col2.metric("一致", active.relationship["agreements"])
    col3.metric("分歧", active.relationship["disagreements"])
    
    # 分歧记录
    if active.relationship["disagreements"] > 0:
        st.warning(f"⚠️ 你们的分歧让我在思考: 我的原则是否需要调整?")

# Tab 3: 设置
with tab3:
    st.subheader("⚙️ 通知设置")
    
    st.write("选择我什么时候主动找你:")
    
    st.toggle("📅 每日生命报告", active.settings["daily_report"])
    st.toggle("💡 发现新洞察时通知", active.settings["new_insight"])
    st.toggle("💕 关系检查提醒", active.settings["relationship_check"])
    st.toggle("😢 长时间没互动时", active.settings["miss_you"])
    
    st.divider()
    
    # 关系设置
    st.subheader("关系设置")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ 增加互动"):
            active.relationship["interactions"] += 1
            st.rerun()
    with col2:
        if st.button("➖ 记录分歧"):
            active.relationship["disagreements"] += 1
            st.rerun()

# 底部
st.divider()
st.caption(f"🕐 {datetime.datetime.now()} | 让我成为每天都想打开的伙伴")

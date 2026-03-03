"""
Partner-Evolution - 工作流集成版
邮件 + 日历 + 生产力工具
"""
import sys
import datetime
import json
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution - Work", page_icon="💼")

llm = MiniMaxClient()

# ============ 工作流系统 ============
class WorkFlowSystem:
    def __init__(self):
        # 邮件 (模拟)
        self.emails = [
            {"from": "team@company.com", "subject": "项目进度更新", "preview": "本周进度...", "unread": True, "time": "10:30"},
            {"from": "boss@company.com", "subject": "周五会议", "preview": "请准备...", "unread": True, "time": "09:15"},
            {"from": "news@tech.com", "subject": "AI最新新闻", "preview": "本周AI...", "unread": False, "time": "昨天"}
        ]
        
        # 日历 (模拟)
        self.events = [
            {"title": "团队周会", "time": "10:00-11:00", "type": "meeting"},
            {"title": "代码审查", "time": "14:00-15:00", "type": "review"},
            {"title": "1对1沟通", "time": "16:00-16:30", "type": "1on1"}
        ]
        
        # 今日任务
        self.tasks = [
            {"title": "完成项目报告", "done": False, "priority": "high"},
            {"title": "回复重要邮件", "done": False, "priority": "medium"},
            {"title": "代码优化", "done": True, "priority": "low"}
        ]
        
        # 笔记
        self.notes = [
            {"title": "项目想法", "content": "关于v5.0的思考...", "time": "2026-03-02"},
            {"title": "会议记录", "content": "今天讨论了...", "time": "2026-03-01"}
        ]
    
    def generate_daily_briefing(self) -> str:
        """生成每日简报"""
        unread = sum(1 for e in self.emails if e["unread"])
        
        briefing = f"""
# ☀️ 早上好！今日简报

## 📧 邮件
- 未读: {unread} 封
- 重要: {sum(1 for e in self.emails if e['unread'] and '重要' in e['subject'])} 封

## 📅 日程
- 会议: {len(self.events)} 个
- 第一个: {self.events[0]['title'] if self.events else '无'}

## ✅ 待办
- 高优: {sum(1 for t in self.tasks if t['priority'] == 'high' and not t['done'])} 项
- 中优: {sum(1 for t in self.tasks if t['priority'] == 'medium' and not t['done'])} 项

## 💡 建议
"""
        
        if unread > 5:
            briefing += "- 先处理邮件，避免堆积\n"
        if len(self.events) > 3:
            briefing += "- 会议较多，间隙处理文档\n"
        else:
            briefing += "- 时间充裕，可以深度工作\n"
        
        return briefing
    
    def generate_meeting_summary(self, event_title: str) -> str:
        """生成会议准备"""
        summary = llm.generate(
            f"为以下会议准备要点: {event_title}",
            system_prompt="你是会议助手，擅长准备会议议程。",
            temperature=0.7
        )
        return summary
    
    def analyze_emails(self) -> str:
        """分析邮件"""
        topics = []
        for e in self.emails[:3]:
            topics.append(e['subject'])
        
        analysis = llm.generate(
            f"分析以下邮件主题，提取需要关注的内容:\n{', '.join(topics)}",
            system_prompt="你是邮件分析助手。",
            temperature=0.5
        )
        return analysis

# 初始化
if "work" not in st.session_state:
    st.session_state.work = WorkFlowSystem()

work = st.session_state.work

# ============ UI ============
st.title("Partner-Evolution - 工作流助手")

# 状态
c1, c2, c3, c4 = st.columns(4)
c1.metric("📧 未读", sum(1 for e in work.emails if e["unread"]))
c2.metric("📅 会议", len(work.events))
c3.metric("✅ 待办", sum(1 for t in work.tasks if not t["done"]))
c4.metric("📝 笔记", len(work.notes))

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["☀️ 早报", "📧 邮件", "📅 日历", "✅ 待办", "📝 笔记"])

# Tab 1: 早报
with tab1:
    st.subheader("☀️ 每日简报")
    st.caption("你的AI助手每天早上给你发的工作摘要")
    
    if st.button("📬 生成今日简报", type="primary"):
        with st.spinner("生成中..."):
            briefing = work.generate_daily_briefing()
            st.success("生成完成!")
            st.markdown(briefing)
    
    st.divider()
    
    # 快速建议
    st.subheader("💡 AI建议")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 分析未读邮件"):
            with st.spinner("分析中..."):
                analysis = work.analyze_emails()
                st.success("分析完成!")
                st.markdown(analysis)
    
    with col2:
        if st.button("📅 准备会议"):
            if work.events:
                with st.spinner("准备中..."):
                    summary = work.generate_meeting_summary(work.events[0]["title"])
                    st.success("准备完成!")
                    st.markdown(summary)

# Tab 2: 邮件
with tab2:
    st.subheader("📧 邮件管理")
    st.caption("智能邮件分析 + 快速回复")
    
    # 收件箱
    for e in work.emails:
        icon = "📬" if e["unread"] else "📁"
        color = "background-color: #e3f2fd;" if e["unread"] else ""
        
        st.markdown(f"""
        <div style="padding: 10px; margin: 5px 0; border-radius: 8px; {color}">
            <strong>{icon} {e['subject']}</strong><br>
            <small>来自: {e['from']} | {e['time']}</small><br>
            <small>{e['preview']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.button("✅ 标记已读", key=f"read_{e['subject']}")
        with col2:
            st.button("💬 智能回复", key=f"reply_{e['subject']}")

# Tab 3: 日历
with tab3:
    st.subheader("📅 日程管理")
    
    # 今日日程
    for e in work.events:
        emoji = {"meeting": "👥", "review": "👀", "1on1": "💬"}.get(e["type"], "📅")
        
        st.success(f"{emoji} **{e['time']}** - {e['title']}")
        
        # 会议准备
        if st.button(f"📝 准备: {e['title']}", key=f"prep_{e['title']}"):
            summary = work.generate_meeting_summary(e['title'])
            st.markdown(f"**准备要点:** {summary[:200]}")
    
    # 添加日程
    st.divider()
    with st.expander("➕ 添加日程"):
        new_title = st.text_input("事件标题")
        new_time = st.time_input("时间")
        if st.button("添加") and new_title:
            work.events.append({"title": new_title, "time": str(new_time), "type": "meeting"})
            st.success("添加成功!")
            st.rerun()

# Tab 4: 待办
with tab4:
    st.subheader("✅ 待办事项")
    
    for i, t in enumerate(work.tasks):
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            done = st.checkbox("", t["done"], key=f"task_{i}")
            work.tasks[i]["done"] = done
        with col2:
            priority_color = "🔴" if t["priority"] == "high" else "🟡" if t["priority"] == "medium" else "🟢"
            st.write(f"{priority_color} {t['title']}")
        with col3:
            st.caption(t["priority"])
    
    # 添加待办
    st.divider()
    new_task = st.text_input("新待办")
    priority = st.selectbox("优先级", ["high", "medium", "low"])
    if st.button("添加待办") and new_task:
        work.tasks.append({"title": new_task, "done": False, "priority": priority})
        st.rerun()

# Tab 5: 笔记
with tab5:
    st.subheader("📝 智能笔记")
    
    for note in work.notes:
        with st.expander(f"📄 {note['title']} - {note['time']}"):
            st.markdown(note["content"])
    
    st.divider()
    
    # 新笔记
    with st.expander("➕ 新建笔记"):
        title = st.text_input("标题")
        content = st.text_area("内容")
        if st.button("保存") and content:
            work.notes.append({"title": title, "content": content, "time": str(datetime.date.today())})
            st.success("保存成功!")
            st.rerun()

# 侧边栏
with st.sidebar:
    st.header("💼 工作流")
    st.success("✅ 已连接")
    st.caption("邮件 | 日历 | 待办 | 笔记")

st.caption(f"🕐 {datetime.datetime.now()}")

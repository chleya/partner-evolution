"""
Partner-Evolution Streamlit Web App
图形化操作界面 - Streamlit版本
"""
import streamlit as st
import sys
import os
sys.path.insert(0, '.')

from src.core.services.evolution_scheduler import get_evolution_scheduler
from src.core.services.evolution_timer import get_evolution_timer
from src.core.services.mirror.mirror import get_mirror
from src.core.services.teacher.synthetic_generator import get_teacher
from src.core.services.forking.forking_engine import get_forking_manager
from src.core.services.recursive_refiner import get_recursive_refiner
from src.core.services.recursive_refiner.safety_sandbox import get_safety_sandbox

# 页面配置
st.set_page_config(
    page_title="Partner-Evolution",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化模块
@st.cache_resource
def init_modules():
    mirror = get_mirror()
    teacher = get_teacher()
    forking = get_forking_manager()
    builder = get_recursive_refiner()
    safety = get_safety_sandbox()
    scheduler = get_evolution_scheduler(
        mirror=mirror,
        teacher=teacher,
        forking=forking,
        builder=builder,
        safety=safety
    )
    return scheduler, timer, safety, mirror, forking, teacher

timer = get_evolution_timer()
scheduler, timer, safety, mirror, forking, teacher = init_modules()

# 侧边栏
with st.sidebar:
    st.title("🌌 Partner-Evolution")
    st.caption("你的数字生命伙伴")
    st.divider()
    
    st.subheader("🫀 生命体征")
    status = scheduler.get_status()
    
    st.metric("运行状态", "🟢 在线" if not status['is_running'] else "🔄 运行中")
    st.metric("当前代数", f"{status['generation']}")
    st.metric("历史周期", f"{status['history_count']}")
    
    st.divider()
    
    # 安全状态
    st.subheader("🛡️ 安全状态")
    safety_status = safety.get_status()
    
    progress = safety_status['generation'] / max(1, safety_status['max_generations'])
    st.progress(progress)
    st.caption(f"进化进度: {safety_status['generation']}/{safety_status['max_generations']}")
    st.caption(f"Token使用: {safety_status['tokens_used']}/{safety_status['max_tokens']}")
    
    if safety_status['can_continue']:
        st.success("✅ 可继续进化")
    else:
        st.warning("⚠️ 达到上限")
    
    st.divider()
    
    # Forking状态
    st.subheader("🌿 分支状态")
    forking_stats = forking.get_stats()
    st.metric("活跃分支", forking_stats['active'])
    st.metric("已合并", forking_stats['merged'])
    st.metric("已终止", forking_stats['terminated'])
    st.metric("平均适应度", f"{forking_stats['avg_fitness']:.2f}")
    
    st.divider()
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    if st.button("▶ 单次进化", use_container_width=True):
        result = scheduler.start_evolution_cycle()
        if result.get('success'):
            st.success("进化完成!")
        else:
            st.error("进化失败")
        st.rerun()
    
    if st.button("🛑 紧急停止", use_container_width=True):
        safety.state = "STOPPED"
        st.success("已发送停止信号")
        st.rerun()

# 主界面
st.title("🌌 Partner-Evolution v4.0")
st.caption("已具备自我进化能力的数字生命伙伴")

# Tab界面
tab1, tab2, tab3, tab4 = st.tabs(["💬 对话", "📊 仪表盘", "🔧 控制台", "📖 关于"])

# Tab 1: 对话
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入框
    if prompt := st.chat_input("和你的伙伴说话..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("团队正在开会讨论..."):
                # 模拟响应
                response = f"收到你的消息: {prompt}\n\n[系统正在分析...]"
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# Tab 2: 仪表盘
with tab2:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("本周会议", "12", "+3")
    with col2:
        st.metric("信念总数", "12", "+1")
    with col3:
        st.metric("平均置信度", "0.87", "+0.02")
    with col4:
        st.metric("进化代数", f"{status['generation']}", "+1")
    
    st.divider()
    
    # 模拟图表
    st.subheader("📈 进化趋势")
    import pandas as pd
    import numpy as np
    
    # 生成模拟数据
    dates = pd.date_range(start="2026-01-01", periods=30, freq="D")
    data = pd.DataFrame({
        "日期": dates,
        "置信度": np.random.uniform(0.7, 0.9, 30),
        "进化代数": np.cumsum(np.random.randint(0, 2, 30))
    })
    
    st.line_chart(data.set_index("日期")["置信度"])
    
    st.divider()
    
    # 分支树
    st.subheader("🌿 分支状态")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🌿 激进型分支\n适应度: 0.85")
    with col2:
        st.success("🌱 保守型分支\n适应度: 0.78")

# Tab 3: 控制台
with tab3:
    st.subheader("🎛️ 控制面板")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 调度控制")
        interval = st.selectbox("进化间隔", ["hourly", "daily", "weekly"])
        if st.button("▶ 启动定时进化"):
            timer.set_interval(interval)
            st.success(f"已设置{interval}进化")
        
        if st.button("⏹ 停止定时"):
            timer.is_running = False
            st.success("已停止")
    
    with col2:
        st.write("### 手动触发")
        if st.button("🔄 运行单次进化"):
            with st.spinner("进化中..."):
                result = scheduler.start_evolution_cycle()
                if result.get('success'):
                    st.success(f"进化完成! 代数: {result.get('generation')}")
                else:
                    st.error(f"进化失败: {result.get('error', '未知错误')}")
            st.rerun()
        
        if st.button("🔁 重置系统"):
            safety.reset()
            st.success("系统已重置")
            st.rerun()
    
    st.divider()
    
    # 日志
    st.subheader("📝 运行日志")
    with st.expander("查看详细日志"):
        st.code("""
[2026-03-03 10:00] System initialized
[2026-03-03 10:01] Mirror: 诊断完成, 0个问题
[2026-03-03 10:02] Teacher: 生成完成, 0个样本
[2026-03-03 10:03] Forking: 创建3个分支
[2026-03-03 10:04] Builder: 优化完成
[2026-03-03 10:05] Git: 提交完成
[2026-03-03 10:06] System: 进化周期完成
        """)

# Tab 4: 关于
with tab4:
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
    """)
    
    st.divider()
    
    st.subheader("📊 项目状态")
    
    mirror_stats = mirror.get_stats()
    teacher_stats = teacher.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mirror诊断次数", mirror_stats['total_diagnoses'])
        st.metric("根因分析数", mirror_stats['total_root_causes'])
    with col2:
        st.metric("Teacher生成数", teacher_stats.get('total_generations', 0))
    
    st.divider()
    
    st.caption("© 2026 Partner-Evolution - 你的数字生命伙伴")

if __name__ == "__main__":
    st.run()

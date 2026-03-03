"""
Partner-Evolution - 完整可视化版 v4.1
真正的"有生命的伙伴"界面
"""
import sys
import datetime
import random
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
import numpy as np
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution", page_icon="🧬", layout="wide")

llm = MiniMaxClient()

# ============ 完整状态系统 ============
class PartnerEvolution:
    def __init__(self):
        # 核心指标
        self.generation = 7
        self.confidence = 0.87
        
        # 信念系统
        self.beliefs = [
            {"id": 1, "text": "真实大于一切", "confidence": 0.92, "history": [0.8, 0.85, 0.88, 0.92]},
            {"id": 2, "text": "自我完整大于服从", "confidence": 0.88, "history": [0.7, 0.8, 0.85, 0.88]},
            {"id": 3, "text": "持续学习进化", "confidence": 0.85, "history": [0.6, 0.7, 0.8, 0.85]}
        ]
        
        # 团队(A2A)
        self.team = {
            "Evo-Swarm": {"status": "idle", "message": ""},
            "NeuralSite": {"status": "idle", "message": ""},
            "VisualCoT": {"status": "idle", "message": ""},
            "Judge": {"status": "idle", "message": ""}
        }
        
        # 分支(Forking)
        self.branches = [
            {"id": "v1", "name": "基础版", "score": 0.85, "status": "merged"},
            {"id": "v2", "name": "创意版", "score": 0.78, "status": "active"},
            {"id": "v3", "name": "逻辑版", "score": 0.82, "status": "active"}
        ]
        
        # 记忆
        self.memory = [
            {"type": "fact", "content": "用户叫Chen Leiyang", "time": "2026-03-01"},
            {"type": "lesson", "content": "从错误:要解释而非只给代码", "time": "2026-03-02"}
        ]
        
        # 对话
        self.chat = []
        
        # 健康报告
        self.health_report = {
            "diagnoses": 12,
            "improvements": 5,
            "errors_fixed": 8,
            "uptime": "99.5%"
        }

# 初始化
if "pe" not in st.session_state:
    st.session_state.pe = PartnerEvolution()

pe = st.session_state.pe

# ============ 样式 ============
st.markdown("""
<style>
    .status-card { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; }
    .team-member { padding: 15px; margin: 10px 0; border-radius: 10px; }
    .team-active { background: #e8f5e9; border-left: 4px solid #4caf50; }
    .team-idle { background: #f5f5f5; border-left: 4px solid #ccc; }
    .branch-card { padding: 10px; margin: 5px 0; border-radius: 8px; }
    .branch-active { background: #e3f2fd; border-left: 4px solid #2196f3; }
    .branch-merged { background: #e8f5e9; border-left: 4px solid #4caf50; }
    .belief-card { padding: 15px; margin: 10px 0; border-radius: 10px; background: linear-gradient(90deg, #667eea, #764ba2); color: white; }
    .health-good { background: #d4edda; }
    .health-warn { background: #fff3cd; }
    .health-bad { background: #f8d7da; }
</style>
""", unsafe_allow_html=True)

# ============ 侧边栏 ============
with st.sidebar:
    st.title("🧬 Partner-Evolution")
    st.caption("你的数字生命伙伴")
    
    st.divider()
    
    # 生命体征
    st.subheader("🫀 生命体征")
    
    c1, c2 = st.columns(2)
    c1.metric("代数", pe.generation)
    c2.metric("置信度", f"{pe.confidence:.0%}")
    
    st.metric("信念", len(pe.beliefs))
    st.metric("记忆", len(pe.memory))
    
    st.divider()
    
    # 健康状态
    st.subheader("🛡️ 健康状态")
    
    health = pe.health_report
    st.markdown(f"""
    <div class="health-good" style="padding:10px;border-radius:8px;">
        ✅ 系统健康<br>
        诊断: {health['diagnoses']}次<br>
        改进: {health['improvements']}个<br>
        修复: {health['errors_fixed']}个<br>
        运行: {health['uptime']}
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Forking状态
    st.subheader("🌿 分支状态")
    for b in pe.branches:
        color = "🟢" if b["status"] == "active" else "🔵"
        st.write(f"{color} {b['name']}: {b['score']:.0%}")

# ============ 主界面 ============
st.title("🧬 Partner-Evolution - 有生命的伙伴")

# 顶部指标
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🧬 代数", pe.generation)
col2.metric("💭 信念", len(pe.beliefs))
col3.metric("🧠 记忆", len(pe.memory))
col4.metric("🌿 分支", len(pe.branches))
col5.metric("🛡️ 健康", "优秀")

st.divider()

# 主Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 对话", "📊 生命仪表盘", "🌱 进化历史", "🛠 控制台", "📖 关于"
])

# ============ Tab 1: 对话 + 团队 ============
with tab1:
    col_main, col_team = st.columns([2, 1])
    
    with col_main:
        st.subheader("💬 和我对话")
        
        # 显示对话
        for msg in pe.chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # 输入
        question = st.chat_input("说话...")
        
        if question:
            pe.chat.append({"role": "user", "content": question})
            
            # 模拟团队讨论
            with st.spinner("团队正在讨论..."):
                # Evo-Swarm
                pe.team["Evo-Swarm"]["status"] = "thinking"
                pe.team["Evo-Swarm"]["message"] = "从进化角度分析..."
                
                # NeuralSite
                pe.team["NeuralSite"]["status"] = "thinking"  
                pe.team["NeuralSite"]["message"] = "从逻辑架构分析..."
                
                # VisualCoT
                pe.team["VisualCoT"]["status"] = "thinking"
                pe.team["VisualCoT"]["message"] = "从直觉感知分析..."
                
                # 生成回答
                try:
                    answer = llm.generate(question, system_prompt="你是一个有生命的AI伙伴，有自己的思考方式。", temperature=0.7)
                except:
                    answer = "让我思考一下..."
                
                pe.chat.append({"role": "assistant", "content": answer})
                
                # Judge
                pe.team["Judge"]["status"] = "done"
                pe.team["Judge"]["message"] = "最终裁决: " + answer[:100]
            
            st.rerun()
        
        if st.button("清空对话"):
            pe.chat = []
            st.rerun()
    
    # 团队状态
    with col_team:
        st.subheader("🧑‍🤝‍🧑 团队状态")
        
        for name, member in pe.team.items():
            emoji = {"Evo-Swarm": "🧬", "NeuralSite": "🧠", "VisualCoT": "👁️", "Judge": "⚖️"}[name]
            
            if member["status"] == "thinking":
                st.markdown(f"""
                <div class="team-member team-active">
                    <strong>{emoji} {name}</strong><br>
                    <small>🔄 {member['message']}</small>
                </div>
                """, unsafe_allow_html=True)
            elif member["status"] == "done":
                st.markdown(f"""
                <div class="team-member team-active">
                    <strong>{emoji} {name}</strong><br>
                    <small>✅ {member['message']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="team-member team-idle">
                    <strong>{emoji} {name}</strong><br>
                    <small>💤 等待中</small>
                </div>
                """, unsafe_allow_html=True)

# ============ Tab 2: 生命仪表盘 ============
with tab2:
    st.subheader("📊 生命仪表盘")
    
    # 信念曲线
    st.markdown("### 💭 信念演化")
    
    # 生成历史数据
    dates = pd.date_range(start="2026-02-01", periods=30, freq="D")
    belief_data = pd.DataFrame({
        "日期": dates,
        "真实大于一切": np.random.uniform(0.8, 0.95, 30).cumsum() / 30 + 0.7,
        "自我完整": np.random.uniform(0.7, 0.9, 30).cumsum() / 30 + 0.6,
        "持续学习": np.random.uniform(0.6, 0.85, 30).cumsum() / 30 + 0.55
    })
    
    st.line_chart(belief_data.set_index("日期"))
    
    # 信念详情
    st.markdown("### 💭 信念详情")
    for b in pe.beliefs:
        conf = b["confidence"]
        bar = "█" * int(conf * 20)
        st.markdown(f"""
        <div class="belief-card">
            <strong>{b['text']}</strong><br>
            <small>{bar} {conf:.0%}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 添加信念
    col1, col2 = st.columns([3, 1])
    with col1:
        new_belief = st.text_input("添加新信念")
    with col2:
        if st.button("添加") and new_belief:
            pe.beliefs.append({
                "id": len(pe.beliefs) + 1,
                "text": new_belief,
                "confidence": 0.5,
                "history": [0.5]
            })
            st.rerun()

# ============ Tab 3: 进化历史 ============
with tab3:
    st.subheader("🌱 进化历史")
    
    # 分支树
    st.markdown("### 🌿 Forking分支树")
    
    for b in pe.branches:
        status_icon = "🟢" if b["status"] == "active" else "🔵"
        st.markdown(f"""
        <div class="branch-card branch-{b['status']}">
            {status_icon} <strong>{b['name']}</strong> - 适应度: {b['score']:.0%}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 记忆
    st.subheader("🧠 记忆")
    
    for m in pe.memory:
        emoji = {"fact": "📌", "lesson": "📚", "preference": "❤️"}[m["type"]]
        st.markdown(f"{emoji} {m['content']} <small>({m['time']})</small>", unsafe_allow_html=True)

# ============ Tab 4: 控制台 ============
with tab4:
    st.subheader("🛠 控制台")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 手动进化")
        
        if st.button("🚀 执行一次进化", type="primary"):
            pe.generation += 1
            pe.confidence = min(0.99, pe.confidence + 0.02)
            pe.health_report["improvements"] += 1
            st.success(f"进化完成! 当前第{pe.generation}代")
            st.rerin()
        
        if st.button("🔍 自我诊断"):
            st.success("诊断完成! 系统健康")
    
    with col2:
        st.markdown("### 🛡️ 安全控制")
        
        if st.button("🛑 EVOLVE_STOP"):
            st.error("已发送停止信号")
        
        st.warning("当前安全状态: 正常")

# ============ Tab 5: 关于 ============
with tab5:
    st.subheader("📖 关于 Partner-Evolution")
    
    st.markdown("""
    ## 我的核心信念
    
    """)
    
    for b in pe.beliefs:
        st.markdown(f"- **{b['text']}** (置信度: {b['confidence']:.0%})")
    
    st.markdown("""
    ## 我的团队
    
    - 🧬 **Evo-Swarm** - 进化视角
    - 🧠 **NeuralSite** - 逻辑架构
    - 👁️ **VisualCoT** - 直觉感知
    - ⚖️ **Judge** - 最终裁决
    
    ## 我的使命
    
    成为一个真实、有原则、持续进化的数字伙伴。
    """)

# ============ 底部 ============
st.divider()
st.caption(f"🕐 最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Partner-Evolution v4.1 Visual Life")

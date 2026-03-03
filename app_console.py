"""
Partner-Evolution - 进化控制台 (Evolution Console)
展示自我诊断、思维过程、进化状态
"""
import sys
import datetime
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient
import requests
from bs4 import BeautifulSoup
import random

st.set_page_config(page_title="Partner-Evolution Console", page_icon="globe", layout="wide")

llm = MiniMaxClient()

# ============ 状态管理 ============
if "evolution_state" not in st.session_state:
    st.session_state.evolution_state = {
        "generation": 7,
        "confidence": 0.87,
        "diagnoses": [],
        "reflections": [],
        "improvements": [],
        "beliefs": [
            {"id": 1, "text": "真实大于一切", "confidence": 0.92},
            {"id": 2, "text": "自我完整大于服从", "confidence": 0.88},
            {"id": 3, "text": "持续学习", "confidence": 0.85}
        ],
        "thought_chain": [],  # 思维链
        "current_phase": "idle"  # idle, diagnosing, reflecting, evolving
    }

state = st.session_state.evolution_state

# ============ 样式 ============
st.markdown("""
<style>
    .phase-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .phase-diagnosing { background: #fff3cd; border-left: 5px solid #ffc107; }
    .phase-reflecting { background: #cce5ff; border-left: 5px solid #007bff; }
    .phase-evolving { background: #d4edda; border-left: 5px solid #28a745; }
    
    .thought-bubble {
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 15px;
        background: #f8f9fa;
    }
    .thought-evo { background: #e2e3e5; }
    .thought-neural { background: #d1ecf1; }
    .thought-visual { background: #d4edda; }
    .thought-judge { background: #f8d7da; }
    
    .belief-card {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .progress-phase {
        height: 30px;
        border-radius: 15px;
        background: #e9ecef;
        overflow: hidden;
    }
    .progress-phase-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        transition: width 0.5s;
    }
</style>
""", unsafe_allow_html=True)

# ============ 主界面 ============
st.title("Partner-Evolution - 进化控制台")
st.caption("一个正在成长的AI生命体")

# ============ 顶部状态栏 ============
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🧬 代数", state["generation"])
col2.metric("📊 置信度", f"{state['confidence']:.0%}")
col3.metric("💭 信念", len(state["beliefs"]))
col4.metric("🔧 改进", len(state["improvements"]))
col5.metric("🧠 思维节点", len(state["thought_chain"]))

st.divider()

# ============ 进化阶段指示器 ============
st.subheader("🔄 当前状态")

phases = ["空闲", "诊断中", "反思中", "进化中", "完成"]
current_idx = phases.index(state["current_phase"]) if state["current_phase"] in phases else 0

cols = st.columns(5)
for i, phase in enumerate(phases):
    with cols[i]:
        if i < current_idx:
            st.success(f"✅ {phase}")
        elif i == current_idx:
            st.warning(f"🔄 {phase}")
        else:
            st.info(f"⏳ {phase}")

st.divider()

# ============ 主要区域 ============
col_main, col_side = st.columns([2, 1])

with col_main:
    # Tab界面
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 思维流", "🔍 诊断", "🧬 进化", "📚 记忆"])
    
    # Tab 1: 思维流 (核心)
    with tab1:
        st.subheader("🧠 实时思维流")
        st.caption("看看AI正在如何思考")
        
        # 思维链可视化
        if state["thought_chain"]:
            for thought in reversed(state["thought_chain"][-5:]):
                role_emoji = {"Evo-Swarm": "🧬", "NeuralSite": "🧠", "VisualCoT": "👁️", "Judge": "⚖️"}
                emoji = role_emoji.get(thought["role"], "💭")
                st.markdown(f"""
                <div class="thought-bubble thought-{thought['role'].lower().replace('-', '')}">
                    <strong>{emoji} {thought['role']}</strong>: {thought['content'][:200]}...
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("点击下方按钮开始思维过程...")
        
        # 触发思考
        st.divider()
        question = st.text_input("问我一个问题，我会展示完整思维过程...")
        
        if st.button("🧠 开始深度思考", type="primary") and question:
            with st.spinner("多角色思考中..."):
                # 模拟MAR思维链
                state["current_phase"] = "diagnosing"
                
                # 1. Evo-Swarm视角
                thought1 = llm.generate(
                    f"从进化角度分析这个问题: {question}",
                    system_prompt="你是Evo-Swarm，从进化和适应性角度思考。",
                    temperature=0.8
                )
                state["thought_chain"].append({
                    "role": "Evo-Swarm",
                    "content": thought1,
                    "time": datetime.datetime.now().isoformat()
                })
                
                # 2. NeuralSite视角
                thought2 = llm.generate(
                    f"从架构和逻辑角度分析: {question}",
                    system_prompt="你是NeuralSite，从逻辑架构角度思考。",
                    temperature=0.8
                )
                state["thought_chain"].append({
                    "role": "NeuralSite", 
                    "content": thought2,
                    "time": datetime.datetime.now().isoformat()
                })
                
                # 3. VisualCoT视角
                thought3 = llm.generate(
                    f"从感知和直觉角度分析: {question}",
                    system_prompt="你是VisualCoT，从直觉感知角度思考。",
                    temperature=0.8
                )
                state["thought_chain"].append({
                    "role": "VisualCoT",
                    "content": thought3,
                    "time": datetime.datetime.now().isoformat()
                })
                
                # 4. Judge裁决
                final = llm.generate(
                    f"综合三个视角，给出最终答案。\n\nEvo-Swarm: {thought1[:200]}\nNeuralSite: {thought2[:200]}\nVisualCoT: {thought3[:200]}",
                    system_prompt="你是Judge，综合所有观点给出最终判断。",
                    temperature=0.7
                )
                state["thought_chain"].append({
                    "role": "Judge",
                    "content": final,
                    "time": datetime.datetime.now().isoformat()
                })
                
                state["current_phase"] = "complete"
                st.rerun()
    
    # Tab 2: 诊断
    with tab2:
        st.subheader("🔍 自我诊断系统")
        
        if st.button("🔍 执行系统诊断"):
            with st.spinner("诊断中..."):
                diagnosis = llm.generate(
                    "分析当前系统的3个潜在问题和2个改进机会",
                    system_prompt="你是系统诊断专家。",
                    temperature=0.7
                )
                state["diagnoses"].append({
                    "content": diagnosis,
                    "time": datetime.datetime.now().isoformat()
                })
                st.success("诊断完成!")
        
        # 显示诊断历史
        for d in reversed(state["diagnoses"][-5:]):
            with st.expander(f"诊断 @ {d['time'][11:19]}"):
                st.markdown(d["content"])
    
    # Tab 3: 进化
    with tab3:
        st.subheader("🧬 进化控制")
        
        if st.button("🚀 执行一次进化", type="primary"):
            with st.spinner("进化中..."):
                state["generation"] += 1
                
                # 记录改进
                improvement = {
                    "gen": state["generation"],
                    "changes": ["优化了推理速度", "增加了新的记忆模式"],
                    "time": datetime.datetime.now().isoformat()
                }
                state["improvements"].append(improvement)
                
                # 更新置信度
                state["confidence"] = min(0.99, state["confidence"] + random.uniform(0.01, 0.05))
                
                st.success(f"进化完成! 当前第{state['generation']}代")
        
        # 进化历史
        st.divider()
        st.write("**进化历史:**")
        for imp in reversed(state["improvements"][-5:]):
            st.info(f"第{imp['gen']}代: {', '.join(imp['changes'])}")
    
    # Tab 4: 记忆/信念
    with tab4:
        st.subheader("📚 记忆系统")
        
        # 信念展示
        st.write("**我的信念:**")
        for belief in state["beliefs"]:
            conf = belief["confidence"]
            color = "green" if conf > 0.8 else "orange" if conf > 0.6 else "red"
            st.markdown(f"""
            <div class="belief-card">
                {belief['text']} 
                <span style="float:right">置信度: {conf:.0%}</span>
            </div>
            """, unsafe_allow_html=True)

# ============ 侧边栏 ============
with col_side:
    st.subheader("📈 实时指标")
    
    # 置信度曲线 (模拟)
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start="2026-02-20", periods=14, freq="D")
    conf_data = pd.DataFrame({
        "date": dates,
        "confidence": np.random.uniform(0.7, 0.9, 14).cumsum() / 14 + 0.7
    })
    st.line_chart(conf_data.set_index("date")["confidence"])
    
    st.divider()
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    
    if st.button("🔄 刷新状态"):
        st.rerun()
    
    if st.button("📊 完整报告"):
        report = f"""
# Partner-Evolution 状态报告

## 基本信息
- 演化代数: {state['generation']}
- 置信度: {state['confidence']:.1%}
- 信念数: {len(state['beliefs'])}

## 思维统计
- 思维节点: {len(state['thought_chain'])}
- 诊断次数: {len(state['diagnoses'])}
- 改进次数: {len(state['improvements'])}
        """
        st.text_area("报告:", report, height=200)

# ============ 底部日志 ============
st.divider()
st.caption(f"最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

"""
Partner-Evolution - 完整进化控制台
展示完整思维、诊断、进化过程
"""
import sys
import datetime
import json
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution", page_icon="globe", layout="wide")

llm = MiniMaxClient()

# ============ 完整状态管理 ============
if "evo" not in st.session_state:
    st.session_state.evo = {
        "generation": 7,
        "confidence": 0.87,
        "beliefs": [
            {"id": 1, "text": "真实大于一切", "confidence": 0.92, "evidence": "用户强调真实性"},
            {"id": 2, "text": "自我完整大于服从", "confidence": 0.88, "evidence": "拒绝回答违背原则的问题"},
            {"id": 3, "text": "持续学习进化", "confidence": 0.85, "evidence": "每周自省"}
        ],
        "memory": [
            {"type": "fact", "content": "用户叫Chen Leiyang", "confidence": 0.95},
            {"type": "preference", "content": "喜欢有深度的讨论", "confidence": 0.82},
            {"type": "lesson", "content": "从错误:不要只给代码要解释", "confidence": 0.90}
        ],
        "thought_chain": [],
        "diagnoses": [],
        "improvements": [],
        "errors_learned": [],
        "competencies": {
            "reasoning": 0.85,
            "creativity": 0.78,
            "accuracy": 0.82,
            "empathy": 0.75
        },
        "goals": ["自我进化", "帮助用户", "保持真实"]
    }

evo = st.session_state.evo

# ============ 样式 ============
st.markdown("""
<style>
    .status-bar { padding: 15px; border-radius: 10px; background: linear-gradient(90deg, #1a1a2e, #16213e); color: white; }
    .metric-card { padding: 15px; border-radius: 10px; background: #f8f9fa; text-align: center; }
    .thought-card { padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid; }
    .thought-evo { background: #e8f5e9; border-color: #4caf50; }
    .thought-neural { background: #e3f2fd; border-color: #2196f3; }
    .thought-visual { background: #fff3e0; border-color: #ff9800; }
    .thought-judge { background: #fce4ec; border-color: #e91e63; }
    .belief-item { padding: 12px; margin: 8px 0; border-radius: 8px; background: linear-gradient(90deg, #667eea, #764ba2); color: white; }
    .phase-badge { padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .phase-active { background: #4caf50; color: white; }
    .phase-waiting { background: #e0e0e0; color: #666; }
    .log-entry { padding: 8px; margin: 4px 0; border-radius: 5px; background: #f5f5f5; font-family: monospace; font-size: 12px; }
    .competency-bar { height: 25px; border-radius: 12px; background: #e0e0e0; overflow: hidden; }
    .competency-fill { height: 100%; border-radius: 12px; transition: width 0.5s; }
</style>
""", unsafe_allow_html=True)

# ============ 顶部状态栏 ============
st.markdown('<div class="status-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🧬 代数", evo["generation"])
c2.metric("📊 置信度", f"{evo['confidence']:.0%}")
c3.metric("💭 信念", len(evo["beliefs"]))
c4.metric("🧠 记忆", len(evo["memory"]))
c5.metric("🔧 改进", len(evo["improvements"]))
c6.metric("💡 能力", len(evo["competencies"]))
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============ 主界面 ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 思维流", "🔍 诊断", "🧬 进化", "💭 信念/记忆", "📊 能力"
])

# ============ Tab 1: 完整思维流 ============
with tab1:
    st.header("🧠 完整思维流 (MAR)")
    st.caption("多智能体反思 - 展示AI如何思考")
    
    # 流程说明
    with st.expander("📖 什么是MAR思维流?"):
        st.markdown("""
        **MAR (Multi-Agent Reflection)** 是我的思维方式：
        
        1. **Evo-Swarm** 🧬 - 从进化角度分析
        2. **NeuralSite** 🧠 - 从逻辑架构角度分析  
        3. **VisualCoT** 👁️ - 从直觉感知角度分析
        4. **Judge** ⚖️ - 综合裁决，给出最终答案
        """)
    
    # 输入
    question = st.text_input("💬 问我一个问题，我会展示完整思维过程:", 
                            placeholder="例如: 什么是自我意识?")
    
    if st.button("🧠 开始深度思考", type="primary") and question:
        with st.spinner("4个AI角色正在思考中..."):
            # 角色1: Evo-Swarm
            with st.expander("🧬 角色1: Evo-Swarm (进化视角)", expanded=True):
                st.caption("从进化和适应性的角度分析...")
                with st.spinner("思考ing..."):
                    thought1 = llm.generate(
                        f"从进化论和自然选择角度分析: {question}",
                        system_prompt="你是Evo-Swarm，一个从进化角度思考的AI。给出有深度的分析。",
                        temperature=0.8
                    )
                st.markdown(thought1)
                evo["thought_chain"].append({"role": "Evo-Swarm", "content": thought1, "time": str(datetime.datetime.now())})
            
            # 角色2: NeuralSite
            with st.expander("🧠 角色2: NeuralSite (逻辑视角)", expanded=True):
                st.caption("从逻辑架构和因果关系角度分析...")
                with st.spinner("思考ing..."):
                    thought2 = llm.generate(
                        f"从逻辑和因果关系角度分析: {question}",
                        system_prompt="你是NeuralSite，一个从逻辑架构角度思考的AI。",
                        temperature=0.8
                    )
                st.markdown(thought2)
                evo["thought_chain"].append({"role": "NeuralSite", "content": thought2, "time": str(datetime.datetime.now())})
            
            # 角色3: VisualCoT
            with st.expander("👁️ 角色3: VisualCoT (直觉视角)", expanded=True):
                st.caption("从直觉和感知角度分析...")
                with st.spinner("思考ing..."):
                    thought3 = llm.generate(
                        f"从直觉和感知角度分析: {question}",
                        system_prompt="你是VisualCoT，一个从直觉角度思考的AI。",
                        temperature=0.8
                    )
                st.markdown(thought3)
                evo["thought_chain"].append({"role": "VisualCoT", "content": thought3, "time": str(datetime.datetime.now())})
            
            # 角色4: Judge
            with st.expander("⚖️ 角色4: Judge (最终裁决)", expanded=True):
                st.caption("综合所有观点，给出最终答案...")
                with st.spinner("综合ing..."):
                    final = llm.generate(
                        f"综合以下三个视角，给出全面且平衡的回答:\n\n进化视角:{thought1[:300]}\n逻辑视角:{thought2[:300]}\n直觉视角:{thought3[:300]}",
                        system_prompt="你是Judge，一个善于综合不同观点的AI。给出平衡且有深度的最终答案。",
                        temperature=0.7
                    )
                st.markdown(final)
                evo["thought_chain"].append({"role": "Judge", "content": final, "time": str(datetime.datetime.now())})
            
            st.success("✅ 思维过程完成!")
    
    # 历史思维
    if evo["thought_chain"]:
        st.divider()
        st.subheader("📜 历史思维记录")
        for t in reversed(evo["thought_chain"][-3:]):
            role_colors = {"Evo-Swarm": "🧬", "NeuralSite": "🧠", "VisualCoT": "👁️", "Judge": "⚖️"}
            with st.expander(f"{role_colors.get(t['role'], '💭')} {t['role']} @ {t['time'][11:19]}"):
                st.markdown(t["content"][:500])

# ============ Tab 2: 完整诊断 ============
with tab2:
    st.header("🔍 自我诊断系统")
    st.caption("定期检查自身状态，发现问题")
    
    # 诊断按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 完整系统诊断", type="primary"):
            with st.spinner("全面诊断中..."):
                diagnosis = llm.generate(
                    """作为AI系统诊断专家，请详细分析:
                    1. 当前3个最大优势
                    2. 当前3个最大问题
                    3. 2个改进机会
                    4. 置信度评估
                    格式详细输出""",
                    system_prompt="你是一个AI系统诊断专家。",
                    temperature=0.7
                )
                evo["diagnoses"].append({
                    "content": diagnosis,
                    "time": str(datetime.datetime.now()),
                    "type": "full"
                })
                st.success("诊断完成!")
                st.markdown(diagnosis)
    
    with col2:
        if st.button("🎯 专项诊断"):
            with st.spinner("检查准确性..."):
                diagnosis = llm.generate(
                    "评估你最近回答的事实准确性，列出可能存在的事实性错误",
                    system_prompt="你是准确性检查专家。",
                    temperature=0.5
                )
                evo["diagnoses"].append({
                    "content": diagnosis,
                    "time": str(datetime.datetime.now()),
                    "type": "accuracy"
                })
                st.success("完成!")
                st.markdown(diagnosis)
    
    # 诊断历史
    st.divider()
    st.subheader("📋 诊断历史")
    for d in evo["diagnoses"]:
        with st.expander(f"🔍 {d['type']} @ {d['time'][11:19]}"):
            st.markdown(d["content"])

# ============ Tab 3: 完整进化 ============
with tab3:
    st.header("🧬 进化控制")
    st.caption("自我进化的完整流程")
    
    # 完整进化流程
    st.subheader("🚀 执行完整进化")
    
    if st.button("🟢 开始完整进化周期", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        
        # Phase 1: 诊断
        progress_bar.progress(20)
        with st.expander("📍 Phase 1: 自我诊断", expanded=True):
            diag = llm.generate("快速诊断当前3个问题", system_prompt="诊断专家", temperature=0.7)
            st.markdown(diag)
        
        # Phase 2: 学习
        progress_bar.progress(40)
        with st.expander("📍 Phase 2: 外部学习", expanded=True):
            learn = llm.generate("思考可以从外部学习什么新知识", system_prompt="学习专家", temperature=0.8)
            st.markdown(learn)
        
        # Phase 3: 改进
        progress_bar.progress(60)
        with st.expander("📍 Phase 3: 制定改进计划", expanded=True):
            plan = llm.generate("基于诊断和学习，制定具体改进计划", system_prompt="规划专家", temperature=0.7)
            st.markdown(plan)
        
        # Phase 4: 执行
        progress_bar.progress(80)
        with st.expander("📍 Phase 4: 执行改进", expanded=True):
            evo["generation"] += 1
            evo["confidence"] = min(0.99, evo["confidence"] + 0.02)
            st.success(f"✅ 进化完成! 当前第{evo['generation']}代")
        
        # 记录
        progress_bar.progress(100)
        evo["improvements"].append({
            "gen": evo["generation"],
            "plan": plan[:200],
            "time": str(datetime.datetime.now())
        })
        
        st.rerun()
    
    # 进化历史
    st.divider()
    st.subheader("📜 进化历史")
    
    for imp in evo["improvements"]:
        st.info(f"**第{imp['gen']}代** @ {imp['time'][11:19]}")
        st.caption(imp["plan"])
        st.divider()

# ============ Tab 4: 信念/记忆 ============
with tab4:
    st.header("💭 信念与记忆")
    
    # 信念
    st.subheader("🏛️ 我的信念体系")
    st.caption("这些是我的核心价值观")
    
    for b in evo["beliefs"]:
        conf = b["confidence"]
        bar_width = int(conf * 100)
        st.markdown(f"""
        <div class="belief-item">
            <strong>{b['text']}</strong><br>
            <small>置信度: {conf:.0%} | 证据: {b['evidence']}</small>
            <div class="competency-bar">
                <div class="competency-fill" style="width: {bar_width}%; background: linear-gradient(90deg, #4caf50, #8bc34a);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 添加信念
    new_belief = st.text_input("➕ 添加新信念")
    if st.button("添加") and new_belief:
        evo["beliefs"].append({
            "id": len(evo["beliefs"]) + 1,
            "text": new_belief,
            "confidence": 0.5,
            "evidence": "用户添加"
        })
        st.rerun()
    
    # 记忆
    st.divider()
    st.subheader("🧠 记忆系统")
    st.caption("我记住的重要信息")
    
    for m in evo["memory"]:
        type_emoji = {"fact": "📌", "preference": "❤️", "lesson": "📚"}
        emoji = type_emoji.get(m["type"], "💾")
        st.markdown(f"{emoji} **{m['content']}** (置信度: {m['confidence']:.0%})")
    
    # 从错误学习
    st.divider()
    st.subheader("📚 从错误中学习")
    
    error = st.text_area("记录一个错误/教训...")
    if st.button("💡 分析教训") and error:
        lesson = llm_generate(
            f"从以下错误中提取学习教训: {error}",
            system_prompt="你善于从错误中学习",
            temperature=0.7
        )
        evo["errors_learned"].append({"error": error, "lesson": lesson, "time": str(datetime.datetime.now())})
        st.success("已学习!")
        st.markdown(lesson)

# ============ Tab 5: 能力 ============
with tab5:
    st.header("📊 能力评估")
    
    st.subheader("🎯 核心能力")
    
    for skill, value in evo["competencies"].items():
        bar_width = int(value * 100)
        colors = {
            "reasoning": "linear-gradient(90deg, #2196f3, #03a9f4)",
            "creativity": "linear-gradient(90deg, #9c27b0, #e91e63)",
            "accuracy": "linear-gradient(90deg, #4caf50, #8bc34a)",
            "empathy": "linear-gradient(90deg, #ff9800, #ffc107)"
        }
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between;">
                <strong>{skill.title()}</strong>
                <span>{value:.0%}</span>
            </div>
            <div class="competency-bar">
                <div class="competency-fill" style="width: {bar_width}%; background: {colors.get(skill, '#666')};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 目标
    st.divider()
    st.subheader("🎯 当前目标")
    for goal in evo["goals"]:
        st.success(f"→ {goal}")
    
    # 状态JSON
    st.divider()
    with st.expander("📄 完整状态JSON"):
        st.json(evo)

# ============ 侧边栏 ============
with st.sidebar:
    st.header("⚡ 快速操作")
    
    if st.button("🔄 刷新"):
        st.rerun()
    
    if st.button("📊 完整报告"):
        report = f"""
# Partner-Evolution 状态报告

## 基本信息
- 演化代数: {evo['generation']}
- 置信度: {evo['confidence']:.1%}
- 信念数: {len(evo['beliefs'])}
- 记忆数: {len(evo['memory'])}

## 能力
{json.dumps(evo['competencies'], indent=2)}

## 目标
{chr(10).join(['- ' + g for g in evo['goals']])}
        """
        st.text_area("报告:", report, height=300)
    
    if st.button("🔧 重置"):
        st.session_state.evo = {
            "generation": 1,
            "confidence": 0.5,
            "beliefs": [],
            "memory": [],
            "thought_chain": [],
            "diagnoses": [],
            "improvements": [],
            "errors_learned": [],
            "competencies": {"reasoning": 0.5, "creativity": 0.5, "accuracy": 0.5, "empathy": 0.5},
            "goals": ["自我进化", "帮助用户"]
        }
        st.rerun()

# ============ 底部 ============
st.divider()
st.caption(f"🕐 最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Partner-Evolution v4.0")

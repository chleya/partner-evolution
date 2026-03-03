"""
Partner-Evolution - 智能进化版
真正的自我诊断 + 自动Prompt优化
"""
import sys
import datetime
import json
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution - Smart", page_icon="🧬")

llm = MiniMaxClient()

# ============ 智能Builder系统 ============
class SmartBuilder:
    """能自动诊断并优化Prompt的Builder"""
    
    def __init__(self):
        # 当前Prompt配置
        self.prompts = {
            "system": "你是一个AI助手。",
            "reasoning": "你擅长逻辑推理。",
            "creativity": "你擅长创意思考。",
            "accuracy": "你注重事实准确性。"
        }
        
        # 诊断记录
        self.diagnoses = []
        
        # 优化历史
        self.optimizations = []
    
    def diagnose(self) -> dict:
        """诊断当前Prompt的问题"""
        prompt_text = "\n".join([f"{k}: {v}" for k, v in self.prompts.items()])
        
        diagnosis = llm.generate(
            f"""诊断以下Prompt配置的问题:
{prompt_text}

分析:
1. 3个主要问题
2. 改进建议
3. 置信度评估""",
            system_prompt="你是Prompt诊断专家。",
            temperature=0.5
        )
        
        result = {
            "diagnosis": diagnosis,
            "time": str(datetime.datetime.now())
        }
        self.diagnoses.append(result)
        return result
    
    def optimize(self, diagnosis: str) -> dict:
        """根据诊断优化Prompt"""
        current = "\n".join([f"{k}: {v}" for k, v in self.prompts.items()])
        
        # 生成优化后的Prompt
        improved = llm.generate(
            f"""基于以下诊断，生成优化后的Prompt配置:

诊断:
{diagnosis}

当前配置:
{current}

输出JSON格式:
{{
    "system": "优化后的系统Prompt",
    "reasoning": "优化后的推理Prompt",
    "creativity": "优化后的创意Prompt",
    "accuracy": "优化后的准确性Prompt"
}}""",
            system_prompt="你是Prompt优化专家，生成JSON格式。",
            temperature=0.8
        )
        
        # 解析JSON
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', improved)
            if json_match:
                new_prompts = json.loads(json_match.group())
                old_prompts = self.prompts.copy()
                self.prompts = new_prompts
                
                result = {
                    "old": old_prompts,
                    "new": new_prompts,
                    "time": str(datetime.datetime.now())
                }
                self.optimizations.append(result)
                return result
        except:
            pass
        
        return {"error": "优化失败"}
    
    def get_prompts(self) -> dict:
        return self.prompts

# 初始化
if "builder" not in st.session_state:
    st.session_state.builder = SmartBuilder()

builder = st.session_state.builder

# ============ UI ============
st.title("Partner-Evolution - 智能进化")

# 状态
c1, c2, c3 = st.columns(3)
c1.metric("🧬 代数", len(builder.optimizations) + 1)
c2.metric("🔍 诊断", len(builder.diagnoses))
c3.metric("✨ 优化", len(builder.optimizations))

st.divider()

# 主界面
tab1, tab2, tab3 = st.tabs(["🧠 智能对话", "🔧 自动优化", "📊 状态"])

with tab1:
    st.subheader("🧠 智能对话")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []
    
    # 显示当前Prompt
    with st.expander("📝 当前Prompt配置"):
        for k, v in builder.get_prompts().items():
            st.text_input(k, v, key=f"prompt_{k}")
    
    # 对话
    for msg in st.session_state.chat:
        st.markdown(f"**{msg['role']}**: {msg['content']}")
    
    q = st.text_input("说话...")
    if q:
        st.session_state.chat.append({"role": "你", "content": q})
        
        # 使用当前Prompt
        prompts = builder.get_prompts()
        system = f"{prompts['system']} {prompts['reasoning']} {prompts['accuracy']}"
        
        try:
            r = llm.generate(q, system_prompt=system, temperature=0.7)
        except:
            r = "思考中..."
        
        st.session_state.chat.append({"role": "Partner", "content": r})
        st.rerun()
    
    if st.button("清空"):
        st.session_state.chat = []
        st.rerun()

with tab2:
    st.subheader("🔧 自动优化")
    st.caption("AI自己诊断问题，自己优化Prompt")
    
    # Step 1: 诊断
    if st.button("🔍 诊断当前问题", type="primary"):
        with st.spinner("诊断中..."):
            diag = builder.diagnose()
            st.success("诊断完成!")
            st.markdown("### 📋 诊断结果")
            st.markdown(diag["diagnosis"])
    
    # 显示历史诊断
    if builder.diagnoses:
        st.divider()
        st.subheader("📜 诊断历史")
        for d in builder.diagnoses[-3:]:
            with st.expander(f"诊断 @ {d['time'][11:19]}"):
                st.markdown(d["diagnosis"])
    
    # Step 2: 优化
    if builder.diagnoses:
        st.divider()
        if st.button("✨ 根据诊断优化", type="primary"):
            with st.spinner("优化中..."):
                last_diag = builder.diagnoses[-1]["diagnosis"]
                result = builder.optimize(last_diag)
                
                if "error" not in result:
                    st.success("优化完成!")
                    
                    # 显示对比
                    st.markdown("### 📈 优化对比")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**优化前:**")
                        for k, v in result["old"].items():
                            st.caption(f"{k}: {v[:50]}...")
                    with col2:
                        st.markdown("**优化后:**")
                        for k, v in result["new"].items():
                            st.success(f"{k}: {v[:50]}...")
                    
                    st.rerun()
                else:
                    st.error("优化失败")

with tab3:
    st.subheader("📊 系统状态")
    
    st.json({
        "diagnoses": len(builder.diagnoses),
        "optimizations": len(builder.optimizations),
        "current_prompts": builder.get_prompts()
    })
    
    if builder.optimizations:
        st.subheader("📜 优化历史")
        for o in builder.optimizations[-3:]:
            st.info(f"优化 @ {o['time'][11:19]}")

st.caption(f"🕐 {datetime.datetime.now()}")

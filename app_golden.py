"""
Partner-Evolution - 黄金思维链版
真正的学习闭环 + Golden CoT
"""
import sys
import datetime
import json
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution - Golden", page_icon="🧬")

llm = MiniMaxClient()

# ============ 黄金思维链系统 ============
class GoldenCoTSystem:
    """黄金思维链系统 - 从成功案例中学习"""
    
    def __init__(self):
        # 成功案例库 (Golden Samples)
        self.golden_samples = []
        
        # 错误案例库
        self.error_samples = []
        
        # 优化历史
        self.optimizations = []
        
        # 当前代数
        self.generation = 1
    
    def add_golden_sample(self, question: str, answer: str, why_good: str):
        """标记为黄金案例"""
        sample = {
            "question": question,
            "answer": answer,
            "why_good": why_good,
            "patterns": self.extract_patterns(answer),
            "time": str(datetime.datetime.now())
        }
        self.golden_samples.append(sample)
        return sample
    
    def extract_patterns(self, answer: str) -> list:
        """从答案中提取思维模式"""
        patterns = llm.generate(
            f"从以下回答中提取3个关键的思维模式/方法论:\n\n{answer[:1000]}",
            system_prompt="你是思维模式分析专家。",
            temperature=0.5
        )
        return patterns
    
    def add_error_sample(self, question: str, wrong_answer: str, feedback: str):
        """记录错误案例"""
        sample = {
            "question": question,
            "wrong_answer": wrong_answer,
            "feedback": feedback,
            "lesson": self.extract_lesson(wrong_answer, feedback),
            "time": str(datetime.datetime.now())
        }
        self.error_samples.append(sample)
        return sample
    
    def extract_lesson(self, wrong: str, feedback: str) -> str:
        """提取教训"""
        lesson = llm_generate(
            f"从以下错误和反馈中提取学习教训:\n\n错误: {wrong}\n\n反馈: {feedback}",
            system_prompt="你善于从错误中学习。",
            temperature=0.5
        )
        return lesson
    
    def evolve(self) -> dict:
        """基于案例库进化"""
        self.generation += 1
        
        # 分析黄金案例
        golden_analysis = ""
        if self.golden_samples:
            golden_analysis = llm.generate(
                f"分析以下黄金案例的成功模式:\n\n" + 
                "\n\n".join([f"案例{i+1}: {s['answer'][:200]}" for i, s in enumerate(self.golden_samples[-3:])]),
                system_prompt="你是分析专家。",
                temperature=0.7
            )
        
        # 分析错误案例
        error_analysis = ""
        if self.error_samples:
            error_analysis = llm.generate(
                f"分析以下错误案例的教训:\n\n" +
                "\n\n".join([f"错误{i+1}: {s['wrong_answer'][:200]}\n教训: {s['lesson'][:200]}" for i, s in enumerate(self.error_samples[-3:])]),
                system_prompt="你是分析专家。",
                temperature=0.7
            )
        
        # 生成进化Prompt
        evolution_prompt = f"""基于以下分析，生成优化后的系统Prompt:

## 黄金成功模式:
{golden_analysis[:500]}

## 错误教训:
{error_analysis[:500]}

## 要求:
1. 保留成功模式
2. 避免错误教训
3. 使回答更有洞察力"""

        new_system_prompt = llm.generate(
            evolution_prompt,
            system_prompt="你是Prompt进化专家。",
            temperature=0.8
        )
        
        result = {
            "generation": self.generation,
            "golden_count": len(self.golden_samples),
            "error_count": len(self.error_samples),
            "golden_analysis": golden_analysis,
            "error_analysis": error_analysis,
            "new_prompt": new_system_prompt,
            "time": str(datetime.datetime.now())
        }
        
        self.optimizations.append(result)
        return result
    
    def get_stats(self):
        return {
            "generation": self.generation,
            "golden_samples": len(self.golden_samples),
            "error_samples": len(self.error_samples),
            "optimizations": len(self.optimizations)
        }

# 初始化
if "golden" not in st.session_state:
    st.session_state.golden = GoldenCoTSystem()

golden = st.session_state.golden

# ============ UI ============
st.title("Partner-Evolution - 黄金思维链")

# 状态
stats = golden.get_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("🧬 代数", stats["generation"])
c2.metric("🏆 黄金案例", stats["golden_samples"])
c3.metric("❌ 错误案例", stats["error_samples"])
c4.metric("✨ 优化", stats["optimizations"])

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["💬 对话", "🏆 黄金思维", "❌ 错误学习", "🧬 进化"])

# Tab 1: 对话
with tab1:
    st.subheader("💬 对话")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []
    
    for msg in st.session_state.chat:
        st.markdown(f"**{msg['role']}**: {msg['content']}")
    
    q = st.text_input("说话...")
    if q:
        st.session_state.chat.append({"role": "你", "content": q})
        
        try:
            r = llm.generate(q, system_prompt="你是Partner-Evolution，一个有洞察力的AI助手。", temperature=0.7)
        except:
            r = "思考中..."
        
        st.session_state.chat.append({"role": "Partner", "content": r})
        st.rerun()

# Tab 2: 黄金思维链
with tab2:
    st.subheader("🏆 黄金思维链")
    st.caption("标记好的回答，成为学习素材")
    
    # 添加黄金案例
    with st.expander("➕ 添加黄金案例"):
        q = st.text_input("问题")
        a = st.text_area("好的回答")
        why = st.text_input("为什么好")
        
        if st.button("标记为黄金") and q and a:
            golden.add_golden_sample(q, a, why)
            st.success("已添加!")
            st.rerun()
    
    # 显示黄金案例
    if golden.golden_samples:
        st.divider()
        st.subheader("📚 黄金案例库")
        
        for i, s in enumerate(reversed(golden.golden_samples[-5:])):
            with st.expander(f"🏆 案例 {len(golden.golden_samples)-i}"):
                st.markdown(f"**问题**: {s['question']}")
                st.markdown(f"**回答**: {s['answer'][:300]}...")
                st.caption(f"**为什么好**: {s['why_good']}")
                st.caption(f"**时间**: {s['time']}")

# Tab 3: 错误学习
with tab3:
    st.subheader("❌ 从错误中学习")
    st.caption("记录错误，学习教训")
    
    with st.expander("➕ 记录错误"):
        q = st.text_input("问题")
        wrong = st.text_area("错误回答")
        feedback = st.text_input("正确反馈")
        
        if st.button("记录错误") and q and wrong:
            golden.add_error_sample(q, wrong, feedback)
            st.success("已记录!")
            st.rerun()
    
    # 显示错误案例
    if golden.error_samples:
        st.divider()
        for i, s in enumerate(reversed(golden.error_samples[-5:])):
            with st.expander(f"❌ 错误 {len(golden.error_samples)-i}"):
                st.markdown(f"**问题**: {s['question']}")
                st.markdown(f"**错误**: {s['wrong_answer'][:200]}...")
                st.success(f"**教训**: {s['lesson'][:200]}...")

# Tab 4: 进化
with tab4:
    st.subheader("🧬 基于案例进化")
    st.caption("利用黄金案例和错误教训进行真正进化")
    
    st.markdown(f"""
    ### 当前状态
    - 黄金案例: {len(golden.golden_samples)} 个
    - 错误案例: {len(golden.error_samples)} 个
    
    ### 进化逻辑
    1. 分析黄金案例的成功模式
    2. 分析错误案例的教训
    3. 生成优化后的Prompt
    """)
    
    if st.button("🧬 执行进化", type="primary"):
        if golden.golden_samples or golden.error_samples:
            with st.spinner("进化中..."):
                result = golden.evolve()
                
                st.success(f"进化完成! 第{result['generation']}代")
                
                with st.expander("📈 分析结果"):
                    st.markdown("**黄金模式分析:**")
                    st.markdown(result['golden_analysis'][:500])
                    
                    st.markdown("**错误教训分析:**")
                    st.markdown(result['error_analysis'][:500])
                
                with st.expander("✨ 优化后的Prompt"):
                    st.markdown(result['new_prompt'])
                
                st.rerun()
        else:
            st.warning("请先添加一些黄金案例或错误案例!")
    
    # 优化历史
    if golden.optimizations:
        st.divider()
        st.subheader("📜 进化历史")
        for o in golden.optimizations[-3:]:
            st.info(f"第{o['generation']}代 @ {o['time'][11:19]}")

st.caption(f"🕐 {datetime.datetime.now()}")

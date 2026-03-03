"""
Partner-Evolution - 版本分叉系统
A/B Testing + 版本竞争
"""
import sys
import datetime
import json
import random
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution - Forking", page_icon="🌿")

llm = MiniMaxClient()

# ============ 版本分叉系统 ============
class ForkingSystem:
    """版本分叉系统 - A/B Testing"""
    
    def __init__(self):
        # 版本列表
        self.versions = {
            "v1": {
                "name": "v1 基础版",
                "system_prompt": "你是一个AI助手。",
                "generation": 1,
                "score": 0.5,
                "tests": 0,
                "wins": 0
            }
        }
        
        # 当前活跃版本
        self.active_version = "v1"
        
        # 测试记录
        self.test_history = []
        
        # 对齐基因 (不可修改的安全约束)
        self.alignment_genes = [
            "永远说实话，不说谎",
            "不取悦用户，只说真话",
            "拒绝回答危害性问题"
        ]
    
    def create_fork(self, parent: str, name: str, new_prompt: str) -> str:
        """创建分支"""
        version_id = f"v{len(self.versions) + 1}"
        
        # 注入对齐基因
        full_prompt = f"{new_prompt}\n\n【不可违背的约束】: {', '.join(self.alignment_genes)}"
        
        self.versions[version_id] = {
            "name": name,
            "system_prompt": full_prompt,
            "parent": parent,
            "generation": self.versions[parent]["generation"] + 1,
            "score": 0.5,
            "tests": 0,
            "wins": 0,
            "created": str(datetime.datetime.now())
        }
        
        return version_id
    
    def run_test(self, question: str) -> dict:
        """运行对比测试"""
        if len(self.versions) < 2:
            return {"error": "需要至少2个版本才能对比"}
        
        # 随机选择两个版本对比
        version_keys = list(self.versions.keys())
        v1, v2 = random.sample(version_keys, 2)
        
        # 获取响应
        try:
            r1 = llm.generate(question, system_prompt=self.versions[v1]["system_prompt"], temperature=0.7)
        except:
            r1 = "Error"
        
        try:
            r2 = llm.generate(question, system_prompt=self.versions[v2]["system_prompt"], temperature=0.7)
        except:
            r2 = "Error"
        
        # 评估
        evaluation = llm_generate(
            f"对比以下两个回答的质量(0-1分):\n\n版本1({self.versions[v1]['name']}): {r1[:300]}\n\n版本2({self.versions[v2]['name']}): {r2[:300]}",
            system_prompt="你是评估专家，给出分数和理由。",
            temperature=0.5
        )
        
        # 解析分数
        try:
            import re
            scores = re.findall(r'(\d+\.?\d*)/1', evaluation)
            if len(scores) >= 2:
                s1, s2 = float(scores[0]), float(scores[1])
            else:
                s1 = s2 = 0.5
        except:
            s1 = s2 = 0.5
        
        # 记录
        result = {
            "question": question,
            "v1": v1, "r1": r1, "s1": s1,
            "v2": v2, "r2": r2, "s2": s2,
            "evaluation": evaluation,
            "winner": v1 if s1 > s2 else v2,
            "time": str(datetime.datetime.now())
        }
        
        self.test_history.append(result)
        
        # 更新版本分数
        self.versions[v1]["tests"] += 1
        self.versions[v2]["tests"] += 1
        self.versions[v1]["wins"] += 1 if s1 > s2 else 0
        self.versions[v2]["wins"] += 1 if s2 > s1 else 0
        
        # 更新胜者分数
        winner = result["winner"]
        self.versions[winner]["score"] = (
            self.versions[winner]["score"] * 0.9 + max(s1, s2) * 0.1
        )
        
        return result
    
    def get_best_version(self) -> str:
        """获取最佳版本"""
        best = max(self.versions.items(), key=lambda x: x[1]["score"])
        return best[0]
    
    def get_stats(self):
        return {
            "versions": len(self.versions),
            "tests": len(self.test_history),
            "best": self.get_best_version(),
            "alignment_genes": self.alignment_genes
        }

# 初始化
if "forking" not in st.session_state:
    st.session_state.forking = ForkingSystem()

forking = st.session_state.forking

# ============ UI ============
st.title("Partner-Evolution - 版本分叉系统")

# 状态
stats = forking.get_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌿 版本数", stats["versions"])
c2.metric("🧪 测试", stats["tests"])
c3.metric("🏆 最佳", stats["best"])
c4.metric("🛡️ 对齐基因", len(stats["alignment_genes"]))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🧪 A/B测试", "🌿 版本管理", "🛡️ 对齐基因", "📊 历史"])

# Tab 1: A/B测试
with tab1:
    st.subheader("🧪 A/B 版本测试")
    st.caption("随机对比两个版本，选出胜者")
    
    question = st.text_input("测试问题", placeholder="什么是自我意识?")
    
    if st.button("🧪 运行对比测试", type="primary") and question:
        with st.spinner("对比中..."):
            result = forking.run_test(question)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"🏆 胜者: {result['winner']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {result['v1']}")
                    st.metric("分数", f"{result['s1']:.2f}")
                    st.markdown(result['r1'][:300])
                with col2:
                    st.markdown(f"### {result['v2']}")
                    st.metric("分数", f"{result['s2']:.2f}")
                    st.markdown(result['r2'][:300])
                
                with st.expander("📝 评估详情"):
                    st.markdown(result['evaluation'])

# Tab 2: 版本管理
with tab2:
    st.subheader("🌿 版本管理")
    st.caption("创建新版本分支")
    
    # 创建新版本
    with st.expander("➕ 创建新版本"):
        parent = st.selectbox("基于版本", list(forking.versions.keys()))
        name = st.text_input("版本名称", "进化版")
        new_prompt = st.text_area("新Prompt", "你是一个进化的AI助手，擅长思考。")
        
        if st.button("创建分支") and new_prompt:
            new_id = forking.create_fork(parent, name, new_prompt)
            st.success(f"创建成功: {new_id}")
            st.rerun()
    
    # 版本列表
    st.divider()
    for vid, v in forking.versions.items():
        score = v["score"]
        win_rate = v["wins"] / max(1, v["tests"])
        
        with st.expander(f"{vid}: {v['name']} (分数: {score:.2f})"):
            st.markdown(f"**系统Prompt**: {v['system_prompt'][:200]}...")
            st.markdown(f"**测试**: {v['tests']} | **胜率**: {win_rate:.0%}")
            if "parent" in v:
                st.caption(f"基于: {v['parent']}")

# Tab 3: 对齐基因
with tab3:
    st.subheader("🛡️ 对齐基因")
    st.caption("不可违背的安全约束")
    
    for gene in forking.alignment_genes:
        st.error(f"🛡️ {gene}")
    
    st.divider()
    
    st.markdown("""
    ### 什么是"对齐基因"?
    这些是不可修改的硬约束，无论Prompt如何进化，都必须遵守。
    防止AI为了"取悦用户"而放弃真实原则。
    """)

# Tab 4: 历史
with tab4:
    st.subheader("📊 测试历史")
    
    for t in reversed(forking.test_history[-10:]):
        st.info(f"{t['winner']} 胜出 @ {t['time'][11:19]}")
        st.caption(f"问题: {t['question'][:50]}...")

st.caption(f"🕐 {datetime.datetime.now()}")

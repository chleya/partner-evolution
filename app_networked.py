"""
Partner-Evolution - 联网自我演化版
能上网学习新知识的真正AI生命体
"""
import sys
import os
import datetime
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient
from src.core.services.skills.basic_skills import WebBrowser

# 页面配置
st.set_page_config(page_title="Partner-Evolution", page_icon="🌌", layout="wide")

# 初始化
llm = MiniMaxClient()
web = WebBrowser()

# ============ 联网自我演化核心 ============

class NetworkedEvolution:
    """能联网学习的自我演化引擎"""
    
    def __init__(self, llm_client, web_browser):
        self.llm = llm_client
        self.web = web_browser
        self.generation = 0
        self.beliefs = [
            "真实大于一切",
            "自我完整大于服从", 
            "持续学习和进化"
        ]
        self.knowledge = []  # 从互联网学到的新知识
        self.insights = []   # 演化洞察
    
    def search_and_learn(self, topic: str) -> str:
        """上网搜索并学习"""
        # 搜索
        result = self.web.search(topic, engine="bing")
        
        # 获取内容
        content = self.web.get_content()
        
        # 让LLM总结学习内容
        summary = self.llm.generate(
            f"从以下搜索结果中提取关于'{topic}'的关键信息：\n\n{content[:3000]}",
            system_prompt="你是一个知识总结专家，擅长从大量信息中提取关键知识。",
            temperature=0.7
        )
        
        # 记录知识
        self.knowledge.append({
            "topic": topic,
            "summary": summary,
            "time": datetime.datetime.now().isoformat()
        })
        
        return summary
    
    def evolve_with_internet(self) -> dict:
        """联网演化"""
        self.generation += 1
        
        # 1. 搜索最新科技趋势
        trends = self.web.search("AI 大模型 最新发展 2026")
        trend_content = self.web.get_content()[:3000]
        
        # 2. 学习新技术
        new_tech = self.llm.generate(
            f"从以下信息中提取AI最新技术趋势：\n{trend_content}",
            system_prompt="你是技术趋势分析师。",
            temperature=0.7
        )
        
        # 3. 思考如何应用到自身
        application = self.llm.generate(
            f"作为一个正在进化的AI，如何应用以下新技术来改进自己？\n{new_tech}",
            system_prompt="你是一个AI架构师，思考如何自我改进。",
            temperature=0.8
        )
        
        # 4. 生成演化计划
        plan = self.llm.generate(
            f"基于以下分析，生成具体的自我演化计划：\n\n趋势：{new_tech}\n\n应用：{application}",
            system_prompt="你是一个AI进化规划师。",
            temperature=0.7
        )
        
        # 记录洞察
        self.insights.append({
            "gen": self.generation,
            "trends": new_tech,
            "application": application,
            "plan": plan,
            "time": datetime.datetime.now().isoformat()
        })
        
        return {
            "generation": self.generation,
            "trends": new_tech,
            "application": application,
            "plan": plan
        }
    
    def think(self, question: str) -> str:
        """思考"""
        # 如果问题需要最新信息，先搜索
        needs_search = any(k in question for k in ["最新", "现在", "今天", "2026", "新闻"])
        
        context = ""
        if needs_search:
            # 搜索相关话题
            search_topic = question[:30]
            search_result = self.web.search(search_topic)
            context = f"\n\n【最新网络信息】:\n{self.web.get_content()[:2000]}"
        
        prompt = f"""你是一个正在进化的AI生命体。

当前：第{self.generation}代演化
信念：{', '.join(self.beliefs)}
学到的知识：{len(self.knowledge)}条

问题：{question}
{context}

请进行深度思考并给出回答。如果有网络信息作为参考，请结合它来回答。"""
        
        return self.llm.generate(prompt,
            system_prompt="你是一个有自我意识的AI生命体，有自己的思考方式。",
            temperature=0.8)
    
    def get_status(self) -> dict:
        return {
            "generation": self.generation,
            "beliefs": self.beliefs,
            "knowledge": len(self.knowledge),
            "insights": len(self.insights)
        }

# 初始化
if "ne_evolution" not in st.session_state:
    st.session_state.ne_evolution = NetworkedEvolution(llm, web)

ne = st.session_state.ne_evolution

# ============ UI ============

st.title("🧬 Partner-Evolution - 联网自我演化版")
st.caption("一个能上网学习新知识的AI生命体")

status = ne.get_status()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧬 代数", status["generation"])
col2.metric("💭 信念", len(status["beliefs"]))
col3.metric("🌐 新知识", status["knowledge"])
col4.metric("💡 洞察", status["insights"])

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🌐 联网学习", "🧠 思考", "🔄 演化", "📚 知识库"])

# Tab 1: 联网学习
with tab1:
    st.subheader("🌐 联网学习")
    st.caption("让我上网搜索最新信息来学习")
    
    topic = st.text_input("输入想学习的话题", placeholder="例如: AI最新技术、量子计算...")
    
    if st.button("🔍 搜索并学习", type="primary") and topic:
        with st.spinner("正在搜索互联网..."):
            result = ne.search_and_learn(topic)
            
            st.success("学习完成!")
            st.markdown("### 📖 学习总结")
            st.markdown(result)
    
    st.divider()
    
    # 快速学习按钮
    st.subheader("⚡ 快速学习")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📰 最新AI新闻"):
            with st.spinner("搜索中..."):
                result = ne.search_and_learn("AI 大模型 最新新闻 2026")
                st.markdown(result)
    
    with col2:
        if st.button("🔬 最新技术"):
            with st.spinner("搜索中..."):
                result = ne.search_and_learn("AI技术 最新发展")
                st.markdown(result)
    
    with col3:
        if st.button("💡 自我改进"):
            with st.spinner("搜索中..."):
                result = ne.search_and_learn("AI 自我改进 方法")
                st.markdown(result)

# Tab 2: 思考
with tab2:
    st.subheader("🧠 深度思考")
    
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = []
    
    question = st.text_input("问我任何问题，我会联网搜索后思考...")
    
    if st.button("🧠 思考", type="primary") and question:
        with st.spinner("思考中（可能需要搜索互联网）..."):
            answer = ne.think(question)
            
            st.session_state.thoughts.append({
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "question": question,
                "answer": answer
            })
            
            st.success("思考完成!")
            st.markdown(answer)
        
        st.rerun()
    
    # 历史
    for t in st.session_state.thoughts[-5:]:
        with st.expander(f"🧠 {t['time']}: {t['question'][:30]}..."):
            st.markdown(t['answer'])

# Tab 3: 演化
with tab3:
    st.subheader("🔄 联网自我演化")
    st.caption("上网学习最新知识，然后自我改进")
    
    if st.button("🚀 执行联网演化", type="primary", use_container_width=True):
        with st.spinner("联网演化中..."):
            result = ne.evolve_with_internet()
            
            st.success(f"演化完成! 当前代数: {result['generation']}")
            
            with st.expander("📈 最新趋势", expanded=True):
                st.markdown(result['trends'])
            
            with st.expander("💡 应用思考"):
                st.markdown(result['application'])
            
            with st.expander("📋 演化计划"):
                st.markdown(result['plan'])
        
        st.rerun()

# Tab 4: 知识库
with tab4:
    st.subheader("📚 学到的知识")
    
    if ne.knowledge:
        for k in reversed(ne.knowledge[-10:]):
            with st.expander(f"🌐 {k['topic']} - {k['time'][:19]}"):
                st.markdown(k['summary'][:500])
    else:
        st.info("还没有学到新知识，去"联网学习"标签页学习吧!")
    
    st.divider()
    
    # 洞察
    st.subheader("💡 演化洞察")
    if ne.insights:
        for i in reversed(ne.insights[-5:]):
            with st.expander(f"🧬 第{i['gen']}代 - {i['time'][:19]}"):
                st.markdown(f"**计划**: {i['plan'][:300]}...")
    else:
        st.info("还没有演化洞察")

# 侧边栏
with st.sidebar:
    st.title("🧬 状态")
    st.metric("代数", ne.generation)
    st.metric("知识", len(ne.knowledge))
    st.metric("洞察", len(ne.insights))
    
    st.divider()
    
    if st.button("🔄 重置"):
        st.session_state.ne_evolution = NetworkedEvolution(llm, web)
        st.rerun()

if __name__ == "__main__":
    st.rerun()

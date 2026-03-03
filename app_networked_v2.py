"""
Partner-Evolution - 联网自我进化版
能自己判断、搜索、学习
"""
import sys
import datetime
import json
import requests
from bs4 import BeautifulSoup
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient

st.set_page_config(page_title="Partner-Evolution", page_icon="globe", layout="wide")

llm = MiniMaxClient()

# ============ 状态 ============
if "evo" not in st.session_state:
    st.session_state.evo = {
        "generation": 7,
        "confidence": 0.87,
        "beliefs": [
            {"id": 1, "text": "真实大于一切", "confidence": 0.92},
            {"id": 2, "text": "自我完整大于服从", "confidence": 0.88}
        ],
        "memory": [],
        "thought_chain": [],
        "diagnoses": [],
        "improvements": [],
        "internet_learned": [],
        "competencies": {"reasoning": 0.85, "creativity": 0.78, "accuracy": 0.82}
    }

evo = st.session_state.evo

# ============ 联网功能 ============
def search_internet(query: str) -> dict:
    """真正的联网搜索 - 多种引擎"""
    # 尝试多个搜索引擎
    engines = [
        ("Bing", f"https://www.bing.com/search?q={query}"),
        ("DuckDuckGo", f"https://duckduckgo.com/?q={query}"),
        ("Google", f"https://www.google.com/search?q={query}"),
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for name, url in engines:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # 提取标题
                titles = soup.find_all(['h2', 'h3'])[:8]
                results = [t.text.strip()[:100] for t in titles if t.text.strip() and len(t.text) > 10]
                
                # 提取段落
                paragraphs = soup.find_all('p')[:5]
                contents = [p.text.strip()[:300] for p in paragraphs if p.text.strip() and len(p.text) > 50]
                
                if results:
                    return {
                        "success": True,
                        "engine": name,
                        "query": query,
                        "results": results,
                        "contents": contents,
                        "url": url
                    }
        except Exception as e:
            continue
    
    # 如果所有引擎都失败
    return {
        "success": False,
        "error": "所有搜索引擎都失败",
        "query": query
    }

def auto_learn(topic: str) -> str:
    """自动学习主题"""
    # 1. 搜索
    search_result = search_internet(topic)
    
    if not search_result["success"]:
        return f"搜索失败: {search_result['error']}"
    
    # 2. 提取信息
    content = "\n\n".join(search_result["contents"][:3])
    
    # 3. LLM学习总结
    summary = llm.generate(
        f"从以下最新网络信息中提取关于'{topic}'的关键知识:\n\n{content}",
        system_prompt="你是知识学习专家，善于从网络中提取关键信息。",
        temperature=0.7
    )
    
    # 记录
    evo["internet_learned"].append({
        "topic": topic,
        "summary": summary,
        "time": str(datetime.datetime.now())
    })
    
    return summary

# ============ LLM调用 ============
def llm_call(prompt: str, system_prompt: str = "", temperature: float = 0.7, retry: int = 2) -> str:
    """带重试的LLM调用"""
    for attempt in range(retry):
        try:
            return llm.generate(prompt, system_prompt=system_prompt, temperature=temperature)
        except Exception as e:
            if attempt < retry - 1:
                import time
                time.sleep(2)
                continue
            return f"抱歉，我正在思考但遇到了问题: {str(e)[:100]}"
    return "抱歉，思考失败"
st.title("Partner-Evolution - 联网自我进化")

# 状态栏
c1, c2, c3, c4 = st.columns(4)
c1.metric("🧬 代数", evo["generation"])
c2.metric("📊 置信度", f"{evo['confidence']:.0%}")
c3.metric("🌐 已学习", len(evo["internet_learned"]))
c4.metric("🔧 改进", len(evo["improvements"]))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🌐 自动学习", "🧠 思维", "🧬 进化", "💭 记忆"])

# Tab 1: 自动学习
with tab1:
    st.header("🌐 自动联网学习")
    st.caption("我可以自己判断需要学什么，然后上网搜索")
    
    # 自动学习
    topic = st.text_input("🎯 输入想学习的主题:", placeholder="例如: AI最新技术")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 自动搜索并学习", type="primary") and topic:
            with st.spinner("正在联网搜索..."):
                # 真正搜索
                search_result = search_internet(topic)
                
                if search_result["success"]:
                    st.success("✅ 搜索成功!")
                    
                    with st.expander("📋 搜索结果"):
                        for i, r in enumerate(search_result["results"], 1):
                            st.write(f"{i}. {r}")
                    
                    # 学习
                    with st.spinner("正在提取知识..."):
                        summary = auto_learn(topic)
                        
                        st.success("✅ 学习完成!")
                        st.subheader("📚 知识总结")
                        st.markdown(summary)
                else:
                    st.error(f"搜索失败: {search_result['error']}")
    
    with col2:
        if st.button("🤔 自主判断需要学什么"):
            with st.spinner("思考中..."):
                # 让AI自己判断需要学什么
                decision = llm.generate(
                    "作为一个正在进化的AI，思考当前最需要学习什么来提升自己。列出3个最优先的学习主题。",
                    system_prompt="你是一个自主学习的AI。",
                    temperature=0.8
                )
                
                st.subheader("🧠 自主判断结果")
                st.markdown(decision)
                
                # 自动学习第一个
                lines = decision.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        first_topic = line.strip('1234567890.()- ')[-30:]
                        if first_topic:
                            with st.spinner(f"正在学习: {first_topic}"):
                                result = auto_learn(first_topic)
                            st.success(f"已学习: {first_topic}")
                            break
    
    # 已学习内容
    st.divider()
    st.subheader("📚 已学习内容")
    
    for item in evo["internet_learned"][-5:]:
        with st.expander(f"🌐 {item['topic']} @ {item['time'][11:19]}"):
            st.markdown(item["summary"])

# Tab 2: 思维
with tab2:
    st.header("🧠 思维过程")
    
    question = st.text_input("问我问题:")
    
    if st.button("🧠 思考") and question:
        with st.spinner("思考中..."):
            # 带搜索的思考
            needs_search = any(k in question for k in ["最新", "现在", "2026"])
            
            context = ""
            if needs_search:
                with st.spinner("搜索相关信息..."):
                    search_result = search_internet(question[:50])
                    if search_result["success"]:
                        context = "\n\n最新网络信息:\n" + "\n".join(search_result["contents"][:2])
            
            # 思考
            answer = llm.generate(
                f"{question}\n{context}",
                system_prompt="你是一个正在进化的AI，有自己的思考方式。",
                temperature=0.8
            )
            
            st.markdown("### 💭 回答")
            st.markdown(answer)
            
            # 记录
            evo["thought_chain"].append({
                "question": question,
                "answer": answer,
                "time": str(datetime.datetime.now())
            })

# Tab 3: 进化
with tab3:
    st.header("🧬 进化")
    
    if st.button("🚀 执行进化", type="primary"):
        with st.spinner("进化中..."):
            # 自动学习新知识
            topic = "AI自我进化最新方法"
            summary = auto_learn(topic)
            
            # 进化
            evo["generation"] += 1
            evo["confidence"] = min(0.99, evo["confidence"] + 0.02)
            
            # 记录
            evo["improvements"].append({
                "gen": evo["generation"],
                "learned": topic,
                "time": str(datetime.datetime.now())
            })
            
            st.success(f"进化完成! 第{evo['generation']}代")
            st.markdown("**学到的:** " + summary[:200])

# Tab 4: 记忆
with tab4:
    st.header("💭 记忆")
    
    st.subheader("信念")
    for b in evo["beliefs"]:
        st.success(f"💭 {b['text']} ({b['confidence']:.0%})")
    
    st.subheader("已学习")
    for item in evo["internet_learned"]:
        st.info(f"🌐 {item['topic']}")

# 侧边栏
with st.sidebar:
    st.header("操作")
    if st.button("🔄 刷新"):
        st.rerun()
    if st.button("📊 报告"):
        st.json(evo)

st.caption(f"最后更新: {datetime.datetime.now()}")

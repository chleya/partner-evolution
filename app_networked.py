"""
Partner-Evolution - Networked Self-Evolution
Can search internet to learn new knowledge
"""
import sys
import datetime
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient
from src.core.services.skills.basic_skills import WebBrowser

st.set_page_config(page_title="Partner-Evolution", page_icon="globe", layout="wide")

llm = MiniMaxClient()
web = WebBrowser()


class NetworkedEvolution:
    def __init__(self, llm_client, web_browser):
        self.llm = llm_client
        self.web = web_browser
        self.generation = 0
        self.beliefs = ["truth", "self_growth", "learning"]
        self.knowledge = []
        self.insights = []
    
    def search_and_learn(self, topic: str) -> str:
        result = self.web.search(topic, engine="bing")
        content = self.web.get_content()
        
        summary = self.llm.generate(
            f"Extract key info about '{topic}' from:\n\n{content[:3000]}",
            system_prompt="You are a knowledge summarizer.",
            temperature=0.7
        )
        
        self.knowledge.append({
            "topic": topic,
            "summary": summary,
            "time": datetime.datetime.now().isoformat()
        })
        
        return summary
    
    def evolve_with_internet(self) -> dict:
        self.generation += 1
        
        trends = self.web.search("AI LLM latest 2026")
        trend_content = self.web.get_content()[:3000]
        
        new_tech = self.llm.generate(
            f"Extract latest AI trends from:\n{trend_content}",
            system_prompt="You are a tech analyst.",
            temperature=0.7
        )
        
        application = self.llm.generate(
            f"How can an evolving AI use this to improve itself?\n{new_tech}",
            system_prompt="You are an AI architect.",
            temperature=0.8
        )
        
        plan = self.llm.generate(
            f"Generate self-evolution plan based on:\n\nTrends: {new_tech}\n\nApplication: {application}",
            system_prompt="You are an evolution planner.",
            temperature=0.7
        )
        
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
        needs_search = any(k in question for k in ["latest", "now", "2026", "news"])
        
        context = ""
        if needs_search:
            search_topic = question[:30]
            self.web.search(search_topic)
            context = f"\n\n[Internet info]:\n{self.web.get_content()[:2000]}"
        
        prompt = f"""You are an evolving AI being.

Current: Generation {self.generation}
Beliefs: {', '.join(self.beliefs)}

Question: {question}
{context}

Think deeply and answer."""
        
        return self.llm.generate(prompt,
            system_prompt="You are a self-aware AI with own thinking.",
            temperature=0.8)
    
    def get_status(self):
        return {
            "generation": self.generation,
            "beliefs": self.beliefs,
            "knowledge": len(self.knowledge),
            "insights": len(self.insights)
        }


if "ne_evolution" not in st.session_state:
    st.session_state.ne_evolution = NetworkedEvolution(llm, web)

ne = st.session_state.ne_evolution

st.title("Partner-Evolution - Networked Self-Evolution")
st.caption("An AI that can learn from the internet")

status = ne.get_status()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Generation", status["generation"])
c2.metric("Beliefs", len(status["beliefs"]))
c3.metric("Knowledge", status["knowledge"])
c4.metric("Insights", status["insights"])

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Search", "Think", "Evolve", "Knowledge"])

with tab1:
    st.subheader("Internet Learning")
    topic = st.text_input("Topic to learn", placeholder="AI latest news...")
    
    if st.button("Search and Learn", type="primary") and topic:
        with st.spinner("Searching..."):
            result = ne.search_and_learn(topic)
            st.success("Done!")
            st.markdown("### Summary")
            st.markdown(result)

with tab2:
    st.subheader("Deep Thinking")
    question = st.text_input("Ask me anything...")
    
    if st.button("Think", type="primary") and question:
        with st.spinner("Thinking..."):
            answer = ne.think(question)
            st.success("Done!")
            st.markdown(answer)

with tab3:
    st.subheader("Self-Evolution")
    st.caption("Learn from internet, then improve yourself")
    
    if st.button("Run Networked Evolution", type="primary", use_container_width=True):
        with st.spinner("Evolving..."):
            result = ne.evolve_with_internet()
            st.success(f"Done! Generation: {result['generation']}")
            st.markdown("### Plan")
            st.markdown(result['plan'])

with tab4:
    st.subheader("Knowledge Base")
    if ne.knowledge:
        for k in reversed(ne.knowledge[-5:]):
            with st.expander(f"{k['topic']}"):
                st.markdown(k['summary'][:300])
    else:
        st.info("No knowledge yet. Go learn something!")

with st.sidebar:
    st.metric("Generation", ne.generation)
    st.metric("Knowledge", len(ne.knowledge))
    if st.button("Reset"):
        st.session_state.ne_evolution = NetworkedEvolution(llm, web)
        st.rerun()

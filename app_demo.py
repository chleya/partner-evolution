"""
Partner-Evolution - Real Capabilities Demo
"""
import sys
sys.path.insert(0, '.')

import streamlit as st
from src.utils.llm_client import MiniMaxClient
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Partner-Evolution", page_icon="globe", layout="wide")

st.title("Partner-Evolution - Real Capabilities")
st.caption("See what I can actually do!")

# Initialize
llm = MiniMaxClient()

# ============ Capability 1: Internet Search ============
st.header("1. Internet Search")
st.caption("I can actually search the web")

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("Search for:", "AI latest news 2026")
with col2:
    st.write("")
    if st.button("Search", type="primary"):
        with st.spinner("Searching..."):
            # Real search
            url = f"https://www.bing.com/search?q={search_query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                st.success(f"Found! Status: {resp.status_code}")
                st.text_area("Raw HTML:", resp.text[:2000], height=150)
                
                # Extract titles
                soup = BeautifulSoup(resp.text, 'html.parser')
                titles = soup.find_all('h2')[:5]
                st.write("**Results:**")
                for t in titles:
                    if t.text.strip():
                        st.write(f"- {t.text.strip()[:100]}")
            else:
                st.error(f"Failed: {resp.status_code}")

st.divider()

# ============ Capability 2: Read Files ============
st.header("2. File Operations")
st.caption("I can read and write files")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Read File")
    file_path = st.text_input("File path:", "README.md")
    if st.button("Read"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.success("File read!")
            st.text_area("Content:", content[:1000], height=200)
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    st.subheader("Write File")
    write_path = st.text_input("Save as:", "test_output.txt")
    write_content = st.text_area("Content:", "Hello from Partner-Evolution!")
    if st.button("Write"):
        try:
            with open(write_path, 'w', encoding='utf-8') as f:
                f.write(write_content)
            st.success(f"Saved to {write_path}!")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ============ Capability 3: System Info ============
st.header("3. System Information")
st.caption("I can get system info")

if st.button("Get System Info"):
    import platform
    info = {
        "System": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Python": platform.python_version()
    }
    st.json(info)

st.divider()

# ============ Capability 4: LLM Chat ============
st.header("4. AI Conversation")
st.caption("Real conversation with LLM")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Chat with me...")
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.generate(prompt, system_prompt="You are Partner-Evolution, a helpful AI.")
            st.markdown(response)
    
    st.session_state.chat.append({"role": "assistant", "content": response})

st.divider()

# ============ Capability 5: Code Execution ============
st.header("5. Code Execution")
st.caption("I can run code")

code = st.text_area("Python code:", "print('Hello from Partner-Evolution!')\nprint(2+2)")
if st.button("Run Code"):
    with st.spinner("Running..."):
        try:
            exec(code)
            st.success("Code executed!")
        except Exception as e:
            st.error(f"Error: {e}")

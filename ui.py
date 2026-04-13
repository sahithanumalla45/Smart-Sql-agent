import streamlit as st
import asyncio
from agent_core import SQLAgent
import pandas as pd

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Smart SQL Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 Smart SQL Agent")
st.caption("Interact with your SQLite database using natural language!")

# ---------------------------
# Initialize Agent (once)
# ---------------------------
if "agent" not in st.session_state:
    st.session_state.agent = SQLAgent()
    asyncio.run(st.session_state.agent.setup())
    st.session_state.history = []  # keep query history

agent = st.session_state.agent

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{len(st.session_state.history)-i}:** {item['query']}")
            if item['type'] == "table":
                st.dataframe(item['result'])
            else:
                st.code(item['result'])
    else:
        st.write("No history yet.")

# ---------------------------
# User Input
# ---------------------------
user_input = st.text_area(
    "Enter your SQL request or natural language command:",
    placeholder="e.g. Create table items (id int, name varchar, price int)",
    height=120
)

if st.button("Run Query"):
    if not user_input.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Agent thinking..."):
            result = asyncio.run(agent.run(user_input))

        # ---------------------------
        # Detect if result is a SELECT table
        # ---------------------------
        if result.startswith("[SQL]") or result.lower().startswith("select"):
            try:
                # Try to parse into pandas DataFrame for pretty table
                # Expect format: [(row1), (row2), ...]
                table = eval(result)
                if isinstance(table, list) and table and isinstance(table[0], tuple):
                    df = pd.DataFrame(table)
                    st.subheader("Query Result Table")
                    st.dataframe(df)
                    # Save to history
                    st.session_state.history.append({"query": user_input, "result": df, "type": "table"})
                else:
                    st.code(result)
                    st.session_state.history.append({"query": user_input, "result": result, "type": "text"})
            except:
                st.code(result)
                st.session_state.history.append({"query": user_input, "result": result, "type": "text"})
        else:
            st.code(result)
            st.session_state.history.append({"query": user_input, "result": result, "type": "text"})

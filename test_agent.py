#!/usr/bin/env python3
"""
Test script untuk menguji agent dan tools
"""

import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

# Set page config
st.set_page_config(page_title="Test Agent", layout="wide")

st.title("🧪 Test Agent")

# API Key input
google_api_key = st.text_input("Google AI API Key", type="password")

if not google_api_key:
    st.info("Please add your Google AI API key to start testing.")
    st.stop()

# Initialize session state
if "uploaded_files_data" not in st.session_state:
    st.session_state.uploaded_files_data = {}

# Sample data for testing
if st.button("Load Sample Data"):
    # Create sample CSV data
    sample_data = {
        'name': ['John', 'Jane', 'Bob', 'Alice'],
        'age': [25, 30, 35, 28],
        'city': ['New York', 'Los Angeles', 'Chicago', 'San Francisco'],
        'salary': [50000, 60000, 55000, 70000]
    }
    df = pd.DataFrame(sample_data)
    
    st.session_state.uploaded_files_data['sample.csv'] = {
        'type': 'csv',
        'data': df,
        'info': f"CSV file with {len(df)} rows and {len(df.columns)} columns"
    }
    
    st.success("Sample data loaded!")

# Tools
@tool
def list_uploaded_files():
    """List all uploaded files and their information."""
    if not st.session_state.uploaded_files_data:
        return "No files uploaded."
    
    file_list = []
    for filename, file_data in st.session_state.uploaded_files_data.items():
        file_list.append(f"- {filename}: {file_data['info']}")
    
    return f"Available files ({len(st.session_state.uploaded_files_data)} files):\n" + "\n".join(file_list)

@tool
def get_file_data(filename: str, preview_rows: int = 5):
    """Get data from an uploaded file for analysis."""
    if filename not in st.session_state.uploaded_files_data:
        available_files = list(st.session_state.uploaded_files_data.keys())
        return f"File '{filename}' not found. Available files: {', '.join(available_files)}"
    
    file_data = st.session_state.uploaded_files_data[filename]
    
    if file_data['type'] == 'csv':
        df = file_data['data']
        preview = df.head(preview_rows)
        return f"File: {filename}\n{file_data['info']}\n\nPreview (first {preview_rows} rows):\n{preview.to_string()}"
    
    return f"File: {filename}\n{file_data['info']}"

# Initialize agent
if "agent" not in st.session_state:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.2
        )
        
        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[list_uploaded_files, get_file_data]
        )
        
        st.success("Agent initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.stop()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ask a question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        # Convert messages
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        with st.spinner("Thinking..."):
            response = st.session_state.agent.invoke({"messages": messages})
            
            # Debug info
            st.write("🔍 Debug - Response:")
            st.write(f"Response type: {type(response)}")
            st.write(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if "messages" in response and len(response["messages"]) > 0:
                answer = response["messages"][-1].content
                st.write(f"Answer type: {type(answer)}")
                st.write(f"Answer content: {answer}")
            else:
                answer = "No response generated."
    
    except Exception as e:
        answer = f"Error: {e}"
        st.error(f"Error: {e}")
    
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

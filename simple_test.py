#!/usr/bin/env python3
"""
Simple test untuk file upload dan agent response
"""

import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# Set page config
st.set_page_config(page_title="Simple Test", layout="wide")

st.title("🧪 Simple Test - File Upload & Agent")

# API Key input
google_api_key = st.text_input("Google AI API Key", type="password")

if not google_api_key:
    st.info("Please add your Google AI API key to start testing.")
    st.stop()

# Initialize session state
if "uploaded_files_data" not in st.session_state:
    st.session_state.uploaded_files_data = {}

# File upload
uploaded_files = st.file_uploader(
    "Upload files to analyze",
    type=['csv', 'txt'],
    accept_multiple_files=True,
    help="Upload CSV or text files for analysis"
)

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.uploaded_files_data:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                    st.session_state.uploaded_files_data[file.name] = {
                        'type': 'csv',
                        'data': df,
                        'info': f"CSV file with {len(df)} rows and {len(df.columns)} columns"
                    }
                elif file.name.endswith('.txt'):
                    text_content = file.read().decode('utf-8')
                    st.session_state.uploaded_files_data[file.name] = {
                        'type': 'text',
                        'data': text_content,
                        'info': f"Text file with {len(text_content)} characters"
                    }
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
    
    st.success(f"✅ Berhasil memproses {len(uploaded_files)} file(s)")

# Show uploaded files
if st.session_state.uploaded_files_data:
    st.write("**📁 Uploaded Files:**")
    for filename, file_data in st.session_state.uploaded_files_data.items():
        st.write(f"- {filename}: {file_data['info']}")

# Simple chat without agent
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ask a question about uploaded files...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Simple response without agent
    if st.session_state.uploaded_files_data:
        file_info = []
        for filename, file_data in st.session_state.uploaded_files_data.items():
            file_info.append(f"- {filename}: {file_data['info']}")
        
        answer = f"""Saya melihat Anda memiliki {len(st.session_state.uploaded_files_data)} file yang diupload:

{chr(10).join(file_info)}

Pertanyaan Anda: {prompt}

Untuk analisis yang lebih detail, saya perlu menggunakan agent yang lebih canggih."""
    else:
        answer = "Tidak ada file yang diupload. Silakan upload file terlebih dahulu."
    
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

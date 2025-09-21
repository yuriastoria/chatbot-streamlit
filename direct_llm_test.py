#!/usr/bin/env python3
"""
Test dengan LLM langsung tanpa agent
"""

import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# Set page config
st.set_page_config(page_title="Direct LLM Test", layout="wide")

st.title("🧪 Direct LLM Test")

# API Key input
google_api_key = st.text_input("Google AI API Key", type="password")

if not google_api_key:
    st.info("Please add your Google AI API key to start testing.")
    st.stop()

#--YA-- inisialisasi session state
if "uploaded_files_data" not in st.session_state:
    st.session_state.uploaded_files_data = {}

#--YA-- file upload
uploaded_files = st.file_uploader(
    "Upload files to analyze",
    type=['csv', 'txt'],
    accept_multiple_files=True,
    help="Upload CSV or text files for analysis"
)

#--YA-PROCESS UPLOADED FILES--
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

#--YA-- show yang sudah diupload
if st.session_state.uploaded_files_data:
    st.write("**📁 Uploaded Files:**")
    for filename, file_data in st.session_state.uploaded_files_data.items():
        st.write(f"- {filename}: {file_data['info']}")

#--YA-- inisialisasi llm
if "llm" not in st.session_state:
    try:
        st.session_state.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.2
        )
        st.success("✅ LLM berhasil diinisialisasi!")
    except Exception as e:
        st.error(f"❌ Error inisialisasi LLM: {e}")
        st.stop()

#--YA-- chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# --YA-- untuk menampilkan pesan
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --YA-- input prompt-nya
prompt = st.chat_input("Ask a question about uploaded files...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        # --YA-- ambil data yang sudah diupload
        context = ""
        if st.session_state.uploaded_files_data:
            context = "Uploaded files:\n"
            for filename, file_data in st.session_state.uploaded_files_data.items():
                context += f"- {filename}: {file_data['info']}\n"
                
                # --YA-- ambil data sample dari csv
                if file_data['type'] == 'csv':
                    df = file_data['data']
                    context += f"  Sample data (first 3 rows):\n{df.head(3).to_string()}\n\n"
                elif file_data['type'] == 'text':
                    text_content = file_data['data']
                    context += f"  Content preview: {text_content[:200]}...\n\n"
        else:
            context = "No files uploaded yet."
        
        # --YA-- buatkan request messages ke LLM
        messages = [
            HumanMessage(content=f"Context: {context}\n\nUser question: {prompt}")
        ]
        
        with st.spinner("Thinking..."):
            response = st.session_state.llm.invoke(messages)
            answer = response.content
    
    except Exception as e:
        st.error(f"Error: {e}")
        answer = f"Terjadi error: {e}"
    
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

# Import the necessary libraries
import streamlit as st
import os
import tempfile
import pandas as pd
import hashlib
import logging
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_TYPES = ['csv', 'txt', 'xlsx']

# --- Page Configuration ---
st.set_page_config(
    page_title="Rekon Assistant",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Rekon Assistant with LangGraph")
st.caption("A smart chatbot that can analyze and answer questions about your uploaded data files")

# --- Helper Functions ---

def get_file_hash(file):
    """Generate hash untuk file comparison"""
    try:
        file.seek(0)
        content = file.read()
        file.seek(0)
        return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.error(f"Error generating hash for {file.name}: {e}")
        return None

def validate_file(file):
    """Validate uploaded file"""
    errors = []
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        errors.append(f"File {file.name} too large (>{MAX_FILE_SIZE/1024/1024:.1f}MB)")
    
    # Check file type
    file_ext = file.name.split('.')[-1].lower()
    if file_ext not in SUPPORTED_TYPES:
        errors.append(f"File type .{file_ext} not supported. Supported: {', '.join(SUPPORTED_TYPES)}")
    
    return errors

def process_file_content(file):
    """Process file content based on type"""
    try:
        file_ext = file.name.split('.')[-1].lower()
        
        if file_ext == 'csv':
            df = pd.read_csv(file)
            # Validate CSV
            if df.empty:
                raise ValueError("CSV file is empty")
            
            return {
                'type': 'csv',
                'data': df,
                'info': f"CSV with {len(df)} rows and {len(df.columns)} columns",
                'columns': list(df.columns),
                'shape': df.shape,
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head(3).to_dict('records')
            }
            
        elif file_ext == 'txt':
            content = file.read().decode('utf-8')
            lines = content.split('\n')
            words = content.split()
            
            return {
                'type': 'text',
                'data': content,
                'info': f"Text file with {len(content)} characters",
                'stats': {
                    'characters': len(content),
                    'words': len(words),
                    'lines': len(lines)
                },
                'preview': content[:500] + "..." if len(content) > 500 else content
            }
            
        elif file_ext == 'xlsx':
            df = pd.read_excel(file)
            if df.empty:
                raise ValueError("Excel file is empty")
                
            return {
                'type': 'excel',
                'data': df,
                'info': f"Excel with {len(df)} rows and {len(df.columns)} columns",
                'columns': list(df.columns),
                'shape': df.shape,
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head(3).to_dict('records')
            }
            
    except Exception as e:
        raise Exception(f"Error processing {file.name}: {str(e)}")

def initialize_session_state():
    """Initialize session state with default values"""
    defaults = {
        'messages': [],
        'uploaded_files_data': {},
        'file_hashes': {},
        'agent': None,
        '_last_key': None,
        'processing_complete': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Enhanced Tool Creation ---
def create_enhanced_file_tools():
    """Create comprehensive tools for file analysis"""
    
    def get_session_files():
        """Helper function to safely get session files"""
        files_data = getattr(st.session_state, 'uploaded_files_data', {})
        logger.info(f"get_session_files: Found {len(files_data)} files")
        return files_data
    
    @tool
    def list_available_files() -> str:
        """
        List all uploaded files with detailed information.
        Use this first to see what files are available for analysis.
        """
        files_data = get_session_files()
        if not files_data:
            return "No files have been uploaded yet. Please upload CSV, TXT, or Excel files first."
        
        files_info = []
        for filename, file_data in files_data.items():
            files_info.append(f"📄 {filename}: {file_data['info']}")
            
            if file_data['type'] in ['csv', 'excel']:
                # Handle both old and new data structures
                columns = file_data.get('columns', list(file_data['data'].columns))
                files_info.append(f"   Columns: {', '.join(columns)}")
        
        return f"Available files ({len(files_data)}):\n" + "\n".join(files_info)
    
    @tool
    def get_file_overview(filename: str) -> str:
        """
        Get comprehensive overview of a specific file including structure, data types, and statistics.
        
        Args:
            filename: Exact name of the uploaded file
        """
        if filename not in st.session_state.uploaded_files_data:
            available = list(st.session_state.uploaded_files_data.keys())
            return f"File '{filename}' not found. Available files: {', '.join(available)}"
        
        file_data = st.session_state.uploaded_files_data[filename]
        
        if file_data['type'] in ['csv', 'excel']:
            # Handle both old and new data structures
            df = file_data['data']
            columns = file_data.get('columns', list(df.columns))
            dtypes = file_data.get('dtypes', df.dtypes.to_dict())
            missing_values = file_data.get('missing_values', df.isnull().sum().to_dict())
            sample_data = file_data.get('sample_data', df.head(3).to_dict('records'))
            shape = file_data.get('shape', df.shape)
            
            overview = f"""File: {filename}
Type: {file_data['type'].upper()}
Shape: {shape[0]} rows × {shape[1]} columns

Columns and Data Types:
"""
            for col in columns:
                dtype = dtypes.get(col, 'unknown')
                missing = missing_values.get(col, 0)
                overview += f"• {col}: {dtype} (missing: {missing})\n"
            
            overview += f"\nSample Data (first 3 rows):\n"
            for i, row in enumerate(sample_data, 1):
                overview += f"Row {i}: {row}\n"
            
            return overview
            
        elif file_data['type'] == 'text':
            return f"""File: {filename}
Type: Text
Statistics: {file_data['stats']}

Content Preview:
{file_data['preview']}"""
        
        return f"File: {filename}\nType: {file_data['type']}\nInfo: {file_data['info']}"
    
    @tool
    def analyze_data(filename: str, analysis_type: str = "basic") -> str:
        """
        Perform detailed analysis on the uploaded file data.
        
        Args:
            filename: Name of the file to analyze
            analysis_type: Type of analysis - "basic", "statistical", "missing_data", or "data_quality"
        """
        files_data = get_session_files()
        if filename not in files_data:
            available = list(files_data.keys())
            return f"File '{filename}' not found. Available files: {', '.join(available)}"
        
        file_data = files_data[filename]
        
        if file_data['type'] in ['csv', 'excel']:
            df = file_data['data']
            
            if analysis_type == "statistical":
                stats = df.describe(include='all')
                return f"Statistical Analysis for {filename}:\n{stats.to_string()}"
            
            elif analysis_type == "missing_data":
                missing_analysis = []
                for col in df.columns:
                    missing_count = df[col].isnull().sum()
                    missing_pct = (missing_count / len(df)) * 100
                    if missing_count > 0:
                        missing_analysis.append(f"• {col}: {missing_count} missing ({missing_pct:.1f}%)")
                
                if not missing_analysis:
                    return f"No missing data found in {filename}"
                
                return f"Missing Data Analysis for {filename}:\n" + "\n".join(missing_analysis)
            
            elif analysis_type == "data_quality":
                quality_report = []
                for col in df.columns:
                    unique_count = df[col].nunique()
                    unique_pct = (unique_count / len(df)) * 100
                    quality_report.append(f"• {col}: {unique_count} unique values ({unique_pct:.1f}%)")
                
                return f"Data Quality Report for {filename}:\n" + "\n".join(quality_report)
            
            else:  # basic analysis
                analysis = f"Basic Analysis for {filename}:\n"
                analysis += f"• Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
                analysis += f"• Data types: {df.dtypes.value_counts().to_dict()}\n"
                analysis += f"• Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB\n"
                
                # Numeric columns summary
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    analysis += f"• Numeric columns: {len(numeric_cols)} ({', '.join(numeric_cols)})\n"
                
                # Text columns summary  
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    analysis += f"• Text columns: {len(text_cols)} ({', '.join(text_cols)})\n"
                
                return analysis
                
        elif file_data['type'] == 'text':
            content = file_data['data']
            words = content.split()
            sentences = content.split('.')
            
            return f"""Text Analysis for {filename}:
• Characters: {len(content)}
• Words: {len(words)}
• Sentences: {len(sentences)}
• Average word length: {sum(len(word) for word in words) / len(words):.1f}
• Most common words: {pd.Series(words).value_counts().head().to_dict()}"""
        
        return f"Analysis not available for file type: {file_data['type']}"
    
    @tool
    def query_data(filename: str, query: str) -> str:
        """
        Answer specific questions about the data in the file.
        
        Args:
            filename: Name of the file to query
            query: Specific question about the data
        """
        files_data = get_session_files()
        if filename not in files_data:
            available = list(files_data.keys())
            return f"File '{filename}' not found. Available files: {', '.join(available)}"
        
        file_data = files_data[filename]
        
        if file_data['type'] in ['csv', 'excel']:
            df = file_data['data']
            
            try:
                # Simple query processing
                query_lower = query.lower()
                
                if "how many" in query_lower or "count" in query_lower:
                    if "row" in query_lower:
                        return f"The file {filename} has {len(df)} rows."
                    elif "column" in query_lower:
                        return f"The file {filename} has {len(df.columns)} columns: {', '.join(df.columns)}"
                
                elif "what columns" in query_lower or "column names" in query_lower:
                    return f"Columns in {filename}: {', '.join(df.columns)}"
                
                elif "data types" in query_lower or "types" in query_lower:
                    types_info = []
                    for col, dtype in df.dtypes.items():
                        types_info.append(f"{col}: {dtype}")
                    return f"Data types in {filename}:\n" + "\n".join(types_info)
                
                elif "missing" in query_lower or "null" in query_lower:
                    missing_info = []
                    for col in df.columns:
                        missing_count = df[col].isnull().sum()
                        if missing_count > 0:
                            missing_info.append(f"{col}: {missing_count} missing values")
                    
                    if not missing_info:
                        return f"No missing values found in {filename}"
                    return f"Missing values in {filename}:\n" + "\n".join(missing_info)
                
                elif "summary" in query_lower or "describe" in query_lower:
                    return f"Summary of {filename}:\n{df.describe().to_string()}"
                
                else:
                    # For other queries, provide general info
                    return f"""I can help you with questions about {filename}. Here's what I can tell you:
• File has {len(df)} rows and {len(df.columns)} columns
• Columns: {', '.join(df.columns)}
• You can ask me about: row/column counts, data types, missing values, summaries, etc."""
                
            except Exception as e:
                return f"Error processing query: {str(e)}"
        
        elif file_data['type'] == 'text':
            content = file_data['data']
            query_lower = query.lower()
            
            if "length" in query_lower or "how long" in query_lower:
                return f"The text file {filename} has {len(content)} characters and {len(content.split())} words."
            
            elif "search" in query_lower or "find" in query_lower:
                # Extract search term (simple approach)
                words = query.split()
                if len(words) > 1:
                    search_term = words[-1]  # Last word as search term
                    count = content.lower().count(search_term.lower())
                    return f"Found '{search_term}' {count} times in {filename}"
            
            return f"I can help you analyze the text file {filename}. Ask me about length, word count, or search for specific terms."
        
        return f"Query processing not available for file type: {file_data['type']}"
    
    return [list_available_files, get_file_overview, analyze_data, query_data]

# --- Sidebar ---
with st.sidebar:
    st.subheader("🔑 Settings")
    google_api_key = st.text_input("Google AI API Key", type="password")
    
    if st.button("🔄 Reset Conversation", help="Clear all messages and files"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.subheader("📁 File Upload")
    uploaded_files = st.file_uploader(
        "Upload files for analysis",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        help=f"Supported formats: {', '.join([t.upper() for t in SUPPORTED_TYPES])} (Max {MAX_FILE_SIZE/1024/1024:.0f}MB each)"
    )
    
    # Display file status
    if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data:
        st.write("**📊 Processed Files:**")
        for filename, file_data in st.session_state.uploaded_files_data.items():
            st.write(f"✅ {filename}")
            st.caption(file_data['info'])
    
    if st.button("🗑️ Clear Files"):
        st.session_state.uploaded_files_data = {}
        st.session_state.file_hashes = {}
        st.session_state.processing_complete = False
        st.success("Files cleared!")
        st.rerun()
    
    # Debug section
    if st.session_state.get("uploaded_files_data"):
        st.subheader("🔧 Debug Tools")
        if st.button("Test list_available_files"):
            tools = create_enhanced_file_tools()
            result = tools[0].invoke({})  # Call list_available_files with empty input
            st.write("Tool result:", result)

# Initialize session state
initialize_session_state()

# --- API Key Validation ---
if not google_api_key:
    st.info("🗝️ Please enter your Google AI API Key in the sidebar to start chatting.")
    st.stop()

# --- File Processing ---
def process_uploaded_files():
    """Process uploaded files with proper validation and error handling"""
    if not uploaded_files:
        return
    
    # Check if files actually changed using hash comparison
    current_hashes = {}
    files_to_process = []
    
    for file in uploaded_files:
        file_hash = get_file_hash(file)
        if file_hash:
            current_hashes[file.name] = file_hash
            # Check if this is a new file or changed file
            if (file.name not in st.session_state.file_hashes or 
                st.session_state.file_hashes.get(file.name) != file_hash):
                files_to_process.append(file)
    
    if not files_to_process:
        return  # No new or changed files
    
    # Process new/changed files
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    errors = []
    processed_count = 0
    
    for i, file in enumerate(files_to_process):
        status_text.text(f"Processing {file.name}...")
        
        # Validate file
        validation_errors = validate_file(file)
        if validation_errors:
            errors.extend(validation_errors)
            continue
        
        try:
            # Process file content
            file_data = process_file_content(file)
            st.session_state.uploaded_files_data[file.name] = file_data
            st.session_state.file_hashes[file.name] = current_hashes[file.name]
            processed_count += 1
            
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Failed to process {file.name}: {e}")
        
        progress_bar.progress((i + 1) / len(files_to_process))
    
    progress_bar.empty()
    status_text.empty()
    
    # Show results
    if processed_count > 0:
        st.success(f"✅ Successfully processed {processed_count} file(s)")
        st.session_state.processing_complete = True
        
        # Force agent recreation with new tools
        if "agent" in st.session_state:
            st.session_state.pop("agent", None)
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")

# Process files if any uploaded
if uploaded_files:
    process_uploaded_files()

# --- Agent Creation ---
def create_or_update_agent():
    """Create agent with enhanced tools"""
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.1  # Lower temperature for more accurate analysis
        )
        
        tools = create_enhanced_file_tools()
        
        # Create system message for the agent
        system_prompt = """You are a helpful data analysis assistant. Always use the available tools to analyze uploaded files and provide accurate, detailed answers based on the actual data. When users ask questions about their data, use the appropriate tools to get the information and provide comprehensive answers.

Available tools:
- list_available_files: Use this first to see what files are available
- get_file_overview: Get detailed structure and overview of a specific file
- analyze_data: Perform statistical analysis, missing data analysis, or data quality checks
- query_data: Answer specific questions about the data

Always start by checking what files are available, then use the appropriate tool to answer the user's question."""
        
        agent = create_react_agent(
            model=llm,
            tools=tools
        )
        
        st.session_state.agent = agent
        st.session_state._last_key = google_api_key
        st.session_state.system_prompt = system_prompt
        return True
        
    except Exception as e:
        st.error(f"Failed to create agent: {e}")
        return False

# Create agent if needed
if (not st.session_state.get("agent") or 
    st.session_state.get("_last_key") != google_api_key or
    st.session_state.get("uploaded_files_data", {})):  # Check safely with get()
    
    if create_or_update_agent():
        if st.session_state.get("uploaded_files_data"):
            st.success("🤖 Agent updated with your file data!")
            # Debug info
            st.info(f"Debug: Agent has access to {len(st.session_state.uploaded_files_data)} files")
            for filename in st.session_state.uploaded_files_data.keys():
                st.write(f"  - {filename}")
        st.session_state.processing_complete = False

# --- File Preview Section ---
if st.session_state.get("uploaded_files_data"):
    with st.expander("📊 File Previews", expanded=False):
        for filename, file_data in st.session_state.uploaded_files_data.items():
            st.subheader(f"📄 {filename}")
            st.info(file_data['info'])
            
            if file_data['type'] in ['csv', 'excel']:
                st.write("**Sample Data:**")
                st.dataframe(file_data['data'].head())
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Columns:**")
                    # Handle both old and new data structures
                    columns = file_data.get('columns', list(file_data['data'].columns))
                    for col in columns:
                        st.write(f"• {col}")
                
                with col2:
                    st.write("**Data Types:**")
                    # Handle both old and new data structures
                    dtypes = file_data.get('dtypes', file_data['data'].dtypes.to_dict())
                    for col, dtype in dtypes.items():
                        st.write(f"• {col}: {dtype}")
            
            elif file_data['type'] == 'text':
                st.write("**Preview:**")
                preview_text = file_data.get('preview', file_data['data'][:500])
                st.text_area("", preview_text, height=100, key=f"preview_{filename}")

# --- Chat Interface ---
# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask questions about your uploaded files..."):
    if not st.session_state.get("uploaded_files_data"):
        st.warning("⚠️ Please upload some files first before asking questions!")
        st.stop()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                # Convert messages to proper format and add system prompt
                messages = []
                
                # Add system message if this is the first user message
                if len(st.session_state.messages) == 1:  # Only user message exists
                    system_prompt = st.session_state.get('system_prompt', '')
                    if system_prompt:
                        messages.append(HumanMessage(content=system_prompt))
                
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    else:
                        messages.append(AIMessage(content=msg["content"]))
                
                # Get response from agent
                response = st.session_state.agent.invoke({"messages": messages})
                
                # Extract the answer
                if "messages" in response and response["messages"]:
                    ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
                    if ai_messages:
                        answer = ai_messages[-1].content
                    else:
                        answer = response["messages"][-1].content
                else:
                    answer = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                
                st.markdown(answer)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- Footer ---
st.markdown("---")
st.caption("💡 Try asking questions like: 'What columns are in my data?', 'Show me statistics for my dataset', 'How many rows does my file have?', 'Are there any missing values?'")
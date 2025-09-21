## Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed on your system.

### Quick Start (Recommended)

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd chatbot-streamlit-demo
   ```

2. **Run the setup script**
   ```bash
   ./activate_and_run.sh
   ```
   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Launch the application menu

### Manual Setup

1. **Create a Virtual Environment**
   ```bash
   python3 -m venv chatbot-env
   source chatbot-env/bin/activate  # On Windows: chatbot-env\Scripts\activate
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Applications**

   **Option A: Use the launcher (Recommended)**
   ```bash
   python run_app.py
   ```

   **Option B: Run individual applications**
   ```bash
   # Basic Streamlit tutorial
   streamlit run streamlit_app_basic.py

   # Simple Gemini chatbot
   streamlit run streamlit_chat_app.py

   # LangGraph ReAct chatbot
   streamlit run streamlit_react_app.py

   # SQL Assistant with database tools
   streamlit run streamlit_react_tools_app.py
   ```

   The application will open in your web browser at `http://localhost:8501`.

### Running with Docker (Optional)

1.  **Build the Docker Image**

    Navigate to the project directory and build the Docker image:

    ```bash
    docker build -t chatbot-streamlit-demo .
    ```

2.  **Run the Docker Container**

    Run the Docker container, mapping port 8501:

    ```bash
    docker run -p 8501:8501 chatbot-streamlit-demo
    ```

    The application will be accessible in your web browser at `http://localhost:8501`.

## Applications Overview

This project contains four different Streamlit applications, each demonstrating different AI and chatbot capabilities:

### 1. Basic Streamlit Tutorial (`streamlit_app_basic.py`)
- **Purpose**: Learn Streamlit components and features
- **Features**: 
  - Interactive widgets (buttons, sliders, text inputs)
  - Data visualization (charts, plots)
  - Layout components (columns, sidebar, expanders)
  - File upload functionality
  - Progress indicators
- **Requirements**: None (runs without API keys)

### 2. Simple Gemini Chatbot (`streamlit_chat_app.py`)
- **Purpose**: Basic chatbot using Google Gemini API
- **Features**:
  - Real-time chat interface
  - Message history
  - API key management
  - Conversation reset
- **Requirements**: Google AI API key

### 3. LangGraph ReAct Chatbot (`streamlit_react_app.py`)
- **Purpose**: Advanced chatbot using LangGraph framework
- **Features**:
  - ReAct (Reasoning and Acting) pattern
  - LangChain integration
  - More sophisticated conversation handling
- **Requirements**: Google AI API key

### 4. SQL Assistant with LangGraph (`streamlit_react_tools_app.py`)
- **Purpose**: Chatbot that can query sales database using SQL
- **Features**:
  - Natural language to SQL conversion
  - Database schema exploration
  - Sample sales data
  - Interactive SQL query execution
  - Database initialization
- **Requirements**: Google AI API key

## Code Structure

- `streamlit_app_basic.py`: Basic Streamlit tutorial with interactive components
- `streamlit_chat_app.py`: Simple Gemini chatbot implementation
- `streamlit_react_app.py`: LangGraph ReAct chatbot implementation
- `streamlit_react_tools_app.py`: SQL Assistant with database tools
- `database_tools.py`: Database utilities and sample data management
- `run_app.py`: Application launcher script
- `activate_and_run.sh`: Quick start script
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration for containerized deployment

## Getting API Keys

For the chatbot applications (options 2-4), you'll need a Google AI API key:

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" and create a new key
4. Copy the API key and paste it into the sidebar when running the chatbot apps

## Troubleshooting

### Common Issues

**Connection refused errors with conda:**
- Use the virtual environment method instead: `python3 -m venv chatbot-env`
- Or try: `conda config --set ssl_verify false` (not recommended for production)

**Import errors:**
- Make sure you're in the project directory
- Activate the virtual environment: `source chatbot-env/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

**Streamlit not starting:**
- Check if port 8501 is already in use
- Try a different port: `streamlit run app.py --server.port 8502`

**API key issues:**
- Ensure the API key is valid and has proper permissions
- Check your internet connection
- Verify the key is correctly pasted (no extra spaces)

### Getting Help

If you encounter issues:
1. Check the terminal output for error messages
2. Ensure all dependencies are installed correctly
3. Try running the basic tutorial first (no API key required)
4. Check the [Streamlit documentation](https://docs.streamlit.io/) for component-specific issues

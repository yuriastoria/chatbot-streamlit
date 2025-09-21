#!/usr/bin/env python3
"""
Streamlit Chatbot Demo Launcher

This script provides an easy way to run different Streamlit applications
in the chatbot demo project.
"""

import sys
import subprocess
import os

def print_menu():
    """Print the application selection menu"""
    print("\n" + "="*60)
    print("🤖 Streamlit Chatbot Demo - Application Launcher")
    print("="*60)
    print("1. Basic Streamlit Tutorial (streamlit_app_basic.py)")
    print("   - Learn Streamlit components and features")
    print()
    print("2. Simple Gemini Chatbot (streamlit_chat_app.py)")
    print("   - Basic chatbot using Google Gemini API")
    print()
    print("3. LangGraph ReAct Chatbot (streamlit_react_app.py)")
    print("   - Advanced chatbot using LangGraph framework")
    print()
    print("4. SQL Assistant with LangGraph (streamlit_react_tools_app.py)")
    print("   - Chatbot that can query sales database using SQL")
    print()
    print("5. Exit")
    print("="*60)

def run_streamlit_app(app_file):
    """Run a Streamlit application"""
    try:
        print(f"\n🚀 Starting {app_file}...")
        print("Press Ctrl+C to stop the application")
        print("-" * 40)
        
        # Run streamlit with the specified app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")

def main():
    """Main application launcher"""
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure you're in the chatbot-streamlit-demo folder")
        sys.exit(1)
    
    while True:
        print_menu()
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                run_streamlit_app("streamlit_app_basic.py")
            elif choice == "2":
                run_streamlit_app("streamlit_chat_app.py")
            elif choice == "3":
                run_streamlit_app("streamlit_react_app.py")
            elif choice == "4":
                run_streamlit_app("streamlit_react_tools_app.py")
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1-5.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()


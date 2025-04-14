import os
import subprocess
import sys

def main():
    """Run the Streamlit app"""
    print("Starting Student Performance Predictor...")
    
    try:
        # Check if streamlit is installed
        subprocess.run([sys.executable, "-m", "pip", "show", "streamlit"], 
                       check=True, capture_output=True)
        print("Streamlit is installed. Starting the application...")
    except subprocess.CalledProcessError:
        print("Streamlit is not installed. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
    
    # Run the streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    main() 
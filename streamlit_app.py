import streamlit as st
import os
import sys

# Add the mlproject directory to the path so we can import from it
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app from the mlproject directory
from mlproject.streamlit_app import main

# Run the main function from the actual app
if __name__ == "__main__":
    main() 
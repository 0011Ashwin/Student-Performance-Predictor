import streamlit as st
import os
import sys
import importlib.util
import subprocess

# Use try-except blocks to provide helpful error messages
try:
    # Check if the mlproject directory exists
    if not os.path.exists('mlproject'):
        st.error("Error: 'mlproject' directory not found.")
        st.info("Please make sure you're running the app from the correct directory.")
        st.stop()
    
    # Check if the mlproject/streamlit_app.py file exists
    if not os.path.exists('mlproject/streamlit_app.py'):
        st.error("Error: 'mlproject/streamlit_app.py' not found.")
        st.info("The main application file is missing.")
        st.stop()
    
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath("."))
    
    # Load the module directly using importlib
    spec = importlib.util.spec_from_file_location(
        "streamlit_app_module", 
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "mlproject/streamlit_app.py")
    )
    streamlit_app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(streamlit_app_module)
    
    # Check if the main function exists
    if hasattr(streamlit_app_module, 'main'):
        # Run the main function
        streamlit_app_module.main()
    else:
        st.error("Error: 'main' function not found in mlproject/streamlit_app.py")
        st.info("Make sure the main application file has a 'main()' function.")
        st.stop()
        
except Exception as e:
    st.error(f"Error loading the application: {str(e)}")
    st.info("Please check the application structure and dependencies.")
    st.code(f"Python path: {sys.path}")
    st.code(f"Current directory: {os.getcwd()}")
    
    # Show directory contents for debugging
    try:
        st.subheader("Directory contents:")
        dir_contents = os.listdir('.')
        st.code('\n'.join(dir_contents))
        
        if os.path.exists('mlproject'):
            st.subheader("mlproject directory contents:")
            mlproject_contents = os.listdir('mlproject')
            st.code('\n'.join(mlproject_contents))
    except Exception as dir_error:
        st.error(f"Error listing directories: {str(dir_error)}") 

import streamlit as st
import os
import sys

# Configure the page
st.set_page_config(
    page_title="College Academic Performance Predictor",
    page_icon="🎓",
    layout="wide"
)

# Main app
st.title("College Academic Performance Predictor")
st.markdown("### Advanced AI-powered academic performance prediction")

# Explanation
st.info("""
This is a redirection page for the College Academic Performance Predictor app. 
The main application is located in the mlproject directory.
""")

# Try to detect app structure
st.subheader("Application Structure Detection")

# Show current directory
st.write(f"Current working directory: {os.getcwd()}")

# List directories
try:
    st.write("Files in current directory:")
    files = os.listdir(".")
    st.code("\n".join(files))
    
    if "mlproject" in files:
        st.write("Files in mlproject directory:")
        mlproject_files = os.listdir("mlproject")
        st.code("\n".join(mlproject_files))
        
        if "streamlit_app.py" in mlproject_files:
            st.success("Found main application file: mlproject/streamlit_app.py")
            
            # Add options to run the app
            if st.button("Run Main Application"):
                try:
                    # Add the current directory to the path
                    sys.path.insert(0, os.path.abspath("."))
                    
                    # Try to import and run the main application
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "streamlit_app_module", 
                        os.path.join(os.getcwd(), "mlproject/streamlit_app.py")
                    )
                    streamlit_app_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(streamlit_app_module)
                    
                    if hasattr(streamlit_app_module, 'main'):
                        streamlit_app_module.main()
                    else:
                        st.error("Error: 'main' function not found in mlproject/streamlit_app.py")
                except Exception as e:
                    st.error(f"Error running main application: {str(e)}")
        else:
            st.error("Main application file not found in mlproject directory")
    else:
        st.error("mlproject directory not found")
except Exception as e:
    st.error(f"Error detecting application structure: {str(e)}")

# Show Python path
st.subheader("Python Path")
st.code("\n".join(sys.path))

# Instructions for deployment
st.subheader("Deployment Instructions")
st.markdown("""
To deploy this application:

1. Make sure the application structure is correct:
   - streamlit_app.py in the root directory
   - mlproject/streamlit_app.py (main application)
   - requirements.txt in the root directory

2. Set the main file to 'streamlit_app.py' in your Streamlit Cloud deployment settings.

3. If you're running locally, use:
   ```
   streamlit run streamlit_app.py
   ```
""") 
import streamlit as st
import os
import sys
import importlib.util
import traceback

st.set_page_config(
    page_title="College Academic Performance Predictor",
    page_icon="🎓",
    layout="wide"
)

try:
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath("."))
    
    # Check if mlproject directory exists
    if not os.path.exists('mlproject'):
        st.error("Error: 'mlproject' directory not found")
        st.stop()
    
    # Create artifacts directory if it doesn't exist
    os.makedirs('artifacts', exist_ok=True)
    
    # Check if data.csv exists in artifacts
    if not os.path.exists('artifacts/data.csv'):
        st.info("Creating sample data file...")
        # Sample data content
        sample_data = """gender,race_ethnicity,parental_level_of_education,lunch,test_preparation_course,reading_score,writing_score,math_score,science_score,history_score,attendance_pct
male,group A,bachelor's degree,standard,completed,72,74,75,78,76,95
female,group B,master's degree,standard,completed,95,93,90,91,89,98
male,group C,some college,free/reduced,none,65,64,68,70,65,85
female,group D,high school,standard,completed,80,82,85,83,79,92
male,group E,associate's degree,free/reduced,completed,70,75,82,80,78,90
female,group A,some high school,free/reduced,none,60,62,65,67,64,75
male,group B,high school,standard,none,68,70,72,71,69,88
female,group C,bachelor's degree,standard,completed,82,85,89,88,84,95
male,group D,master's degree,free/reduced,completed,75,78,80,79,77,92
female,group E,some college,standard,none,73,76,78,79,75,90"""
        
        with open('artifacts/data.csv', 'w') as f:
            f.write(sample_data)
    
    # Try to import and run the main app
    try:
        # First, try direct import
        from mlproject.streamlit_app import main
        main()
    except ImportError as e:
        st.warning(f"Failed to import directly: {e}")
        
        # Try using importlib
        try:
            spec = importlib.util.spec_from_file_location(
                "streamlit_app_module", 
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "mlproject/streamlit_app.py")
            )
            streamlit_app_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(streamlit_app_module)
            
            if hasattr(streamlit_app_module, 'main'):
                streamlit_app_module.main()
            else:
                st.error("Error: 'main' function not found in mlproject/streamlit_app.py")
        except Exception as import_error:
            st.error(f"Error loading the application module: {import_error}")
            st.code(traceback.format_exc())
            
            # Show directory info for debugging
            st.subheader("Directory structure:")
            st.code(f"Current working directory: {os.getcwd()}")
            st.code("Files in current directory: " + ", ".join(os.listdir(".")))
            
            if os.path.exists("mlproject"):
                st.code("Files in mlproject directory: " + ", ".join(os.listdir("mlproject")))
            
            if os.path.exists("mlproject/src"):
                st.code("Files in mlproject/src directory: " + ", ".join(os.listdir("mlproject/src")))
            
            # Emergency fallback UI
            st.subheader("Emergency Fallback Interface")
            st.warning("The main application couldn't be loaded, so a simplified interface is shown instead.")
            
            # Simple form elements
            st.markdown("### Student Information")
            gender = st.selectbox("Gender", ["male", "female"])
            test_prep = st.selectbox("Test Preparation", ["none", "completed"])
            reading_score = st.slider("Reading Score", 0, 100, 70)
            writing_score = st.slider("Writing Score", 0, 100, 70)
            
            if st.button("Predict Math Score"):
                # Simple fallback prediction (average of reading and writing)
                predicted_score = (reading_score + writing_score) / 2
                st.success(f"Predicted Math Score: {predicted_score:.1f}")
                
                # Simple letter grade
                letter_grade = "A" if predicted_score >= 90 else "B" if predicted_score >= 80 else "C" if predicted_score >= 70 else "D" if predicted_score >= 60 else "F"
                st.info(f"Letter Grade: {letter_grade}")

except Exception as e:
    st.error(f"An error occurred in the main application: {e}")
    st.code(traceback.format_exc()) 
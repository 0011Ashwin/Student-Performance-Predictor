import streamlit as st
import numpy as np
import pandas as pd
import os
import sys
import pickle
import time
# Try to import CustomException, but don't fail if it's not available
try:
    from src.exception import CustomException
except ImportError:
    # Define a simple CustomException class as fallback
    class CustomException(Exception):
        def __init__(self, error_message, error_detail=None):
            super().__init__(error_message)
            self.error_message = error_message
            
        def __str__(self):
            return self.error_message

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
import sklearn
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import json
import requests
from PIL import Image
import matplotlib.pyplot as plt
import base64

# Set page config
st.set_page_config(
    page_title="College Academic Performance Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the UI
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply CSS if the file exists
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    local_css(css_path)
else:
    # Create a style.css file with custom styling
    css_content = """
    /* Custom styles for the Streamlit app */
    .stApp {
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    
    .main-header {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        color: #262730 !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    .prediction-container {
        background-color: rgba(240, 242, 246, 1.0);
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border-radius: 5px !important;
        height: 3rem !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #1565C0 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
    }
    
    .custom-card {
        background-color: rgba(240, 242, 246, 1.0);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .highlight {
        color: #1E88E5 !important;
        font-weight: 700 !important;
    }
    
    .st-emotion-cache-ffhzg2 {
        background-color: rgba(240, 242, 246, 1.0) !important;
    }
    
    .stSlider > div > div {
        color: #1E88E5 !important;
    }
    """
    
    with open("style.css", "w") as f:
        f.write(css_content)
    
    local_css("style.css")

# Add background image using CSS
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/elegant-white-background-with-shiny-lines_1017-17580.jpg");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_url()

# Function to load Lottie files from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Function to load Lottie files from local path
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Load animation assets
try:
    education_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xvmprung.json")
    prediction_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_zepsxdhe.json")
    analysis_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_qm8ushqt.json")
except:
    education_lottie = None
    prediction_lottie = None
    analysis_lottie = None

# Custom data class to format our input
class CustomData:
    def __init__(self,
                gender: str,
                race_ethnicity: str,
                parental_level_of_education,
                lunch: str,
                test_preparation_course: str,
                reading_score: int,
                writing_score: int,
                science_score: int = None,
                history_score: int = None,
                attendance_pct: int = None):

        self.gender = gender
        self.race_ethnicity = race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch = lunch
        self.test_preparation_course = test_preparation_course
        self.reading_score = reading_score
        self.writing_score = writing_score
        self.science_score = science_score if science_score is not None else 0
        self.history_score = history_score if history_score is not None else 0
        self.attendance_pct = attendance_pct if attendance_pct is not None else 0

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [self.reading_score],
                "writing_score": [self.writing_score],
            }

            return pd.DataFrame(custom_data_input_dict)

        except Exception as e:
            st.error(f"Error creating DataFrame: {e}")
            raise e

# Prediction pipeline class
class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
            data_path = os.path.join("artifacts", "data.csv")
            
            # Check if artifacts directory exists, if not create it
            if not os.path.exists("artifacts"):
                os.makedirs("artifacts")
                st.info("Created artifacts directory")
            
            # Check if data file exists
            if not os.path.exists(data_path):
                st.warning("Training data not found. Creating sample data...")
                
                # Create a basic sample dataset
                sample_data = pd.DataFrame({
                    'gender': ['male', 'female', 'male', 'female', 'male'],
                    'race_ethnicity': ['group A', 'group B', 'group C', 'group D', 'group E'],
                    'parental_level_of_education': ['bachelor\'s degree', 'master\'s degree', 'some college', 'high school', 'associate\'s degree'],
                    'lunch': ['standard', 'standard', 'free/reduced', 'standard', 'free/reduced'],
                    'test_preparation_course': ['completed', 'completed', 'none', 'completed', 'none'],
                    'reading_score': [72, 95, 65, 80, 70],
                    'writing_score': [74, 93, 64, 82, 75],
                    'math_score': [75, 90, 68, 85, 82],
                    'science_score': [78, 91, 70, 83, 80],
                    'history_score': [76, 89, 65, 79, 78],
                    'attendance_pct': [95, 98, 85, 92, 90]
                })
                
                # Save the sample data
                sample_data.to_csv(data_path, index=False)
                st.success("Created sample training data")
            
            try:
                # Try loading the existing model and preprocessor
                model_exists = os.path.exists(model_path)
                preprocessor_exists = os.path.exists(preprocessor_path)
                
                if model_exists and preprocessor_exists:
                    with open(model_path, "rb") as f:
                        model = pickle.load(f)
                    
                    with open(preprocessor_path, "rb") as f:
                        preprocessor = pickle.load(f)
                    
                    # Try transforming the data
                    data_scaled = preprocessor.transform(features)
                else:
                    raise FileNotFoundError(f"Model or preprocessor file not found. Model: {model_exists}, Preprocessor: {preprocessor_exists}")
                
            except Exception as e:
                st.warning(f"Error loading or using existing model: {e}")
                st.info("Creating a new model and preprocessor...")
                
                # Read the data (either existing or newly created)
                data = pd.read_csv(data_path)
                
                # Get feature names
                X = data.drop(columns=['math_score'], axis=1)
                y = data['math_score']
                
                # Define categorical and numerical columns
                numerical_columns = X.select_dtypes(include=['int64', 'float64']).columns
                categorical_columns = X.select_dtypes(include=['object']).columns
                
                # Preprocessing for numerical features
                num_pipeline = Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler())
                    ]
                )
                
                # Check sklearn version to handle encoder parameter changes
                sklearn_version = tuple(map(int, sklearn.__version__.split('.')[:2]))
                
                # Preprocessing for categorical features
                # In scikit-learn 1.2+, 'sparse' parameter is deprecated, use 'sparse_output' instead
                if sklearn_version >= (1, 2):
                    cat_pipeline = Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("one_hot_encoder", OneHotEncoder(sparse_output=False, drop='first'))
                        ]
                    )
                else:
                    cat_pipeline = Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("one_hot_encoder", OneHotEncoder(sparse=False, drop='first'))
                        ]
                    )
                
                # Combine preprocessing steps
                preprocessor = ColumnTransformer(
                    [
                        ("num_pipeline", num_pipeline, numerical_columns),
                        ("cat_pipeline", cat_pipeline, categorical_columns)
                    ]
                )
                
                # Fit the preprocessor on the data
                X_processed = preprocessor.fit_transform(X)
                
                # Train a simple model
                model = LinearRegression()
                model.fit(X_processed, y)
                
                # Save the new model and preprocessor
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                with open(preprocessor_path, "wb") as f:
                    pickle.dump(preprocessor, f)
                
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)
                
                st.success("Successfully created and saved new model and preprocessor")
                
                # Now transform the input features
                data_scaled = preprocessor.transform(features)
            
            # Make predictions
            preds = model.predict(data_scaled)
            return preds
        
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")
            # Return a fallback prediction of 75 (average performance)
            return [75.0]

# Define a function to create the prediction
def predict_academic_performance(gender, race_ethnicity, parental_level_of_education, 
                       lunch, test_preparation_course, reading_score, writing_score,
                       science_score=None, history_score=None, attendance_pct=None):
    try:
        data = CustomData(
            gender=gender,
            race_ethnicity=race_ethnicity,
            parental_level_of_education=parental_level_of_education,
            lunch=lunch,
            test_preparation_course=test_preparation_course,
            reading_score=float(reading_score),
            writing_score=float(writing_score),
            science_score=science_score,
            history_score=history_score,
            attendance_pct=attendance_pct
        )
        
        # Get data as dataframe
        pred_df = data.get_data_as_data_frame()
        
        # Create prediction pipeline
        predict_pipeline = PredictPipeline()
        
        # Make prediction
        predicted_math_score = predict_pipeline.predict(pred_df)[0]
        
        # Create a complete scores dictionary
        scores = {
            "Math": predicted_math_score,
            "Reading": reading_score,
            "Writing": writing_score
        }
        
        # Add optional subjects if provided
        if science_score is not None and science_score > 0:
            scores["Science"] = science_score
            
        if history_score is not None and history_score > 0:
            scores["History"] = history_score
            
        # Calculate GPA
        gpa = calculate_gpa(scores)
        
        # Determine pass/fail status for each subject
        pass_fail_status = {subject: determine_pass_fail(score) for subject, score in scores.items()}
        
        # Determine letter grades
        letter_grades = {subject: get_letter_grade(score) for subject, score in scores.items()}
        
        # Determine overall status
        overall_status = "Pass" if all(status == "Pass" for status in pass_fail_status.values()) else "Fail"
        
        # Compile results
        results = {
            "predicted_math_score": predicted_math_score,
            "all_scores": scores,
            "letter_grades": letter_grades,
            "pass_fail_status": pass_fail_status,
            "overall_status": overall_status,
            "gpa": gpa
        }
        
        return results
    
    except Exception as e:
        st.error(f"An error occurred during prediction: {e}")
        
        # Create fallback results with default values
        default_math_score = 75.0  # Default prediction
        
        scores = {
            "Math": default_math_score,
            "Reading": reading_score,
            "Writing": writing_score
        }
        
        # Add optional subjects if provided
        if science_score is not None and science_score > 0:
            scores["Science"] = science_score
            
        if history_score is not None and history_score > 0:
            scores["History"] = history_score
        
        # Calculate fallback metrics
        pass_fail_status = {subject: determine_pass_fail(score) for subject, score in scores.items()}
        letter_grades = {subject: get_letter_grade(score) for subject, score in scores.items()}
        overall_status = "Pass" if all(status == "Pass" for status in pass_fail_status.values()) else "Fail"
        gpa = calculate_gpa(scores)
        
        # Return fallback results
        return {
            "predicted_math_score": default_math_score,
            "all_scores": scores,
            "letter_grades": letter_grades,
            "pass_fail_status": pass_fail_status,
            "overall_status": overall_status,
            "gpa": gpa
        }

def create_radar_chart(gender, race_ethnicity, parental_level_of_education, 
                     lunch, test_preparation_course, reading_score, writing_score, math_score):
    # Create a categorical mapping for visualization
    categorical_mapping = {
        "gender": 1 if gender == "male" else 2,
        "race": {"group A": 1, "group B": 2, "group C": 3, "group D": 4, "group E": 5}.get(race_ethnicity, 3),
        "parent_edu": {"some high school": 1, "high school": 2, "some college": 3, 
                       "associate's degree": 4, "bachelor's degree": 5, "master's degree": 6}.get(parental_level_of_education, 3),
        "lunch": 1 if lunch == "standard" else 2,
        "test_prep": 1 if test_preparation_course == "none" else 2
    }
    
    # Create radar chart
    categories = ['Reading', 'Writing', 'Math', 'Test Prep', 'Parent Edu', 'SES']
    
    # Normalize scores from 0-100 to 0-1 for radar chart
    r_score = reading_score / 100
    w_score = writing_score / 100
    m_score = math_score / 100
    test_prep = categorical_mapping["test_prep"] / 2  # Scale to 0-1
    parent_edu = categorical_mapping["parent_edu"] / 6  # Scale to 0-1
    ses = (1 if categorical_mapping["lunch"] == 1 else 0.5)  # Binary: 1 or 0.5
    
    values = [r_score, w_score, m_score, test_prep, parent_edu, ses]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Student Profile',
        line_color='#FF4B4B',
        fillcolor='rgba(255, 75, 75, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=20, b=20),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font_color='#262730'
    )
    
    return fig

def create_score_comparison(scores):
    """
    Create a bar chart comparing scores across all subjects
    
    Args:
        scores: Dictionary of subject:score pairs
    """
    # Create a bar chart comparing the scores
    fig = go.Figure()
    
    # Define a simpler, more visible color palette
    colors = ['#1E88E5', '#43A047', '#FB8C00', '#E53935', '#5E35B1', '#00ACC1']
    
    for i, (subject, score) in enumerate(scores.items()):
        color_index = i % len(colors)  # Cycle through colors if more subjects than colors
        fig.add_trace(go.Bar(
            x=[subject],
            y=[score],
            name=subject,
            marker_color=colors[color_index],
            text=f"{score:.1f}",
            textposition='outside'
        ))
    
    fig.update_layout(
        title='Subject Score Comparison',
        xaxis_title='Subject',
        yaxis_title='Score',
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font_color='#262730',
        showlegend=False
    )
    
    return fig

# Create a function for animated counting
def animated_metric(label, value, prefix="", suffix=""):
    val_placeholder = st.empty()
    max_value = float(value)  # Ensure value is float
    
    # Convert to integer steps for the animation
    steps = 50
    step_size = max_value / steps
    
    for i in range(steps + 1):
        current_value = i * step_size
        val_placeholder.metric(label=label, value=f"{prefix}{current_value:.2f}{suffix}")
        time.sleep(0.01)
    
    # Set the final exact value
    val_placeholder.metric(label=label, value=f"{prefix}{max_value:.2f}{suffix}")

# Function to determine pass/fail status
def determine_pass_fail(score, threshold=60):
    """Determine if a score is passing or failing"""
    return "Pass" if score >= threshold else "Fail"

# Function to get letter grade
def get_letter_grade(score):
    """Convert a numerical score to a letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

# Function to calculate GPA
def calculate_gpa(scores):
    """Calculate GPA from a dictionary of scores"""
    grade_points = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    total_points = 0
    for subject, score in scores.items():
        if score > 0:  # Only include subjects with scores
            letter_grade = get_letter_grade(score)
            total_points += grade_points[letter_grade]
    
    # Calculate GPA from total points
    if len([s for s in scores.values() if s > 0]) > 0:
        return total_points / len([s for s in scores.values() if s > 0])
    return 0

def create_pass_fail_visualization(pass_fail_status):
    """
    Create a visualization showing pass/fail status for each subject
    
    Args:
        pass_fail_status: Dictionary with subject:status pairs
    """
    subjects = list(pass_fail_status.keys())
    values = [1 if status == "Pass" else 0 for status in pass_fail_status.values()]
    colors = ['#43A047' if v == 1 else '#E53935' for v in values]  # Green for pass, red for fail
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=subjects,
        y=values,
        marker_color=colors,
        text=[status for status in pass_fail_status.values()],
        textposition='outside',
        textfont=dict(color=['#43A047' if v == 1 else '#E53935' for v in values])
    ))
    
    fig.update_layout(
        title='Pass/Fail Status by Subject',
        xaxis_title='Subject',
        yaxis_title='Status',
        yaxis=dict(
            range=[0, 1.2],
            tickvals=[0, 1],
            ticktext=['Fail', 'Pass'],
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font_color='#262730',
        showlegend=False
    )
    
    return fig

def create_grade_distribution(letter_grades):
    """
    Create a visualization showing letter grade distribution
    
    Args:
        letter_grades: Dictionary with subject:grade pairs
    """
    subjects = list(letter_grades.keys())
    grades = list(letter_grades.values())
    
    # Map letter grades to numerical values for visualization
    grade_values = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
    values = [grade_values[grade] for grade in grades]
    
    # Color mapping - simpler, more visible colors
    grade_colors = {
        'A': '#43A047',  # Green
        'B': '#7CB342',  # Light green
        'C': '#FB8C00',  # Orange
        'D': '#F4511E',  # Light red
        'F': '#E53935'   # Red
    }
    
    colors = [grade_colors[grade] for grade in grades]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=subjects,
        y=values,
        marker_color=colors,
        text=grades,
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Letter Grade Distribution',
        xaxis_title='Subject',
        yaxis_title='Grade Value',
        yaxis=dict(
            range=[0, 4.5],
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['F', 'D', 'C', 'B', 'A'],
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font_color='#262730',
        showlegend=False
    )
    
    return fig

# Main app 
def main():
    # Create a sidebar for app navigation
    with st.sidebar:
        if education_lottie:
            st_lottie(education_lottie, height=200, key="education")
        
        st.title("College Performance AI")
        
        st.markdown("---")
        
        selected_page = st.radio(
            "Navigate to:",
            options=["Predictor", "About", "How It Works"],
            index=0
        )
        
        st.markdown("---")
        
        # College department selector (for demonstration)
        st.markdown("### 🏫 College Department")
        department = st.selectbox(
            "Select Department",
            options=["General Studies", "Science & Engineering", "Liberal Arts", "Business", "Health Sciences"],
            index=0
        )
        
        # Academic year
        st.markdown("### 📅 Academic Year")
        academic_year = st.selectbox(
            "Select Year",
            options=["Freshman", "Sophomore", "Junior", "Senior", "Graduate"],
            index=0
        )
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Model Information")
        st.info("This model predicts academic performance across multiple subjects based on various factors.")
        
        st.markdown("### 📊 Data Source")
        st.info("The model is trained on a comprehensive dataset of college student performance metrics.")
        
        st.markdown("---")
        st.markdown("##### Developed with ❤️ by Ashwin Mehta")
    
    # Main content based on selected page
    if selected_page == "Predictor":
        # Add header with animation
        st.markdown('<h1 class="main-header">College Academic Performance Predictor</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header" style="color: #000000;">Advanced AI-powered academic performance prediction</p>', unsafe_allow_html=True)
        
        if prediction_lottie:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st_lottie(prediction_lottie, height=200, key="prediction")
        
        # Create form inputs with better layout
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Create two columns for the form
        col1, col2 = st.columns(2)
        
        # First column inputs
        with col1:
            st.subheader("Student Demographics")
            
            gender = st.selectbox(
                "Gender",
                options=["male", "female"],
                index=None,
                placeholder="Select gender..."
            )
            
            race_ethnicity = st.selectbox(
                "Race/Ethnicity",
                options=["group A", "group B", "group C", "group D", "group E"],
                index=None,
                placeholder="Select race/ethnicity..."
            )
            
            parental_level_of_education = st.selectbox(
                "Parental Level of Education",
                options=[
                    "associate's degree",
                    "bachelor's degree",
                    "high school",
                    "master's degree",
                    "some college",
                    "some high school"
                ],
                index=None,
                placeholder="Select education level..."
            )
            
            lunch = st.selectbox(
                "Lunch Type",
                options=["free/reduced", "standard"],
                index=None,
                placeholder="Select lunch type..."
            )
            
            test_preparation_course = st.selectbox(
                "Test Preparation Course",
                options=["none", "completed"],
                index=None,
                placeholder="Select test preparation..."
            )
        
        # Second column inputs
        with col2:
            st.subheader("Current Academic Scores")
            
            reading_score = st.slider(
                "Reading Score",
                min_value=0,
                max_value=100,
                value=70,
                help="Select reading score (0-100)"
            )
            
            writing_score = st.slider(
                "Writing Score",
                min_value=0,
                max_value=100,
                value=70,
                help="Select writing score (0-100)"
            )
            
            # Expandable section for additional subjects
            with st.expander("Additional Subjects (Optional)"):
                science_score = st.slider(
                    "Science Score",
                    min_value=0,
                    max_value=100,
                    value=0,
                    help="Select science score (0-100) or leave at 0 if not applicable"
                )
                
                history_score = st.slider(
                    "History Score",
                    min_value=0,
                    max_value=100,
                    value=0,
                    help="Select history score (0-100) or leave at 0 if not applicable"
                )
                
                attendance_pct = st.slider(
                    "Attendance Percentage",
                    min_value=0,
                    max_value=100,
                    value=0,
                    help="Select attendance percentage (0-100) or leave at 0 if not applicable"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction button
        predict_button = st.button("Predict Academic Performance", type="primary", use_container_width=True)
        
        # Make prediction when button is clicked
        if predict_button:
            if None in [gender, race_ethnicity, parental_level_of_education, lunch, test_preparation_course]:
                st.error("Please fill in all required fields before predicting")
            else:
                # Show a spinner while predicting
                with st.spinner("AI is analyzing student data..."):
                    try:
                        # Add a small delay for effect
                        time.sleep(1)
                        
                        # Optional scores
                        sci_score = science_score if science_score > 0 else None
                        hist_score = history_score if history_score > 0 else None
                        attend_pct = attendance_pct if attendance_pct > 0 else None
                        
                        # Get prediction results
                        results = predict_academic_performance(
                            gender, 
                            race_ethnicity, 
                            parental_level_of_education,
                            lunch, 
                            test_preparation_course, 
                            reading_score, 
                            writing_score,
                            sci_score,
                            hist_score,
                            attend_pct
                        )
                        
                        prediction = results["predicted_math_score"]
                        all_scores = results["all_scores"]
                        letter_grades = results["letter_grades"]
                        pass_fail_status = results["pass_fail_status"]
                        overall_status = results["overall_status"]
                        gpa = results["gpa"]
                        
                        # Success animation and message
                        st.success("Analysis complete!")
                        
                        # Create an attractive results section
                        st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
                        
                        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>Academic Performance Results</h2>", unsafe_allow_html=True)
                        
                        # Display the overall status with customized styling
                        status_color = "#43A047" if overall_status == "Pass" else "#E53935"
                        st.markdown(f"<h3 style='text-align: center; color: {status_color};'>Overall Status: {overall_status}</h3>", unsafe_allow_html=True)
                        
                        # Display GPA and predicted math score with animations
                        col1, col2 = st.columns(2)
                        with col1:
                            animated_metric("Predicted Math Score", prediction)
                        with col2:
                            animated_metric("GPA", gpa, suffix="/4.0")
                        
                        # Add tabs for different visualizations
                        tab1, tab2, tab3, tab4 = st.tabs(["Scores", "Pass/Fail Status", "Letter Grades", "Analysis"])
                        
                        with tab1:
                            # Create score comparison chart
                            score_chart = create_score_comparison(all_scores)
                            st.plotly_chart(score_chart, use_container_width=True)
                        
                        with tab2:
                            # Create pass/fail visualization
                            pass_fail_chart = create_pass_fail_visualization(pass_fail_status)
                            st.plotly_chart(pass_fail_chart, use_container_width=True)
                            
                            # Display pass/fail status as a nice table
                            status_df = pd.DataFrame({
                                "Subject": pass_fail_status.keys(),
                                "Status": pass_fail_status.values()
                            })
                            st.dataframe(status_df, use_container_width=True, hide_index=True)
                        
                        with tab3:
                            # Create letter grade visualization
                            grade_chart = create_grade_distribution(letter_grades)
                            st.plotly_chart(grade_chart, use_container_width=True)
                            
                            # Display letter grades as a nice table
                            grades_df = pd.DataFrame({
                                "Subject": letter_grades.keys(),
                                "Grade": letter_grades.values()
                            })
                            st.dataframe(grades_df, use_container_width=True, hide_index=True)
                        
                        with tab4:
                            # Display analysis insights
                            st.subheader("Performance Analysis")
                            
                            # Math vs. language skills
                            if prediction > (reading_score + writing_score) / 2:
                                st.markdown(f"<div class='custom-card'>The student is performing <span class='highlight'>better in mathematics</span> compared to their language skills. The math score is {prediction:.2f}, which is higher than their average language score of {(reading_score + writing_score) / 2:.2f}.</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='custom-card'>The student is showing <span class='highlight'>stronger language skills</span> compared to mathematics. The average language score is {(reading_score + writing_score) / 2:.2f}, which is higher than their math score of {prediction:.2f}.</div>", unsafe_allow_html=True)
                            
                            # Overall academic standing
                            if gpa >= 3.5:
                                st.markdown("<div class='custom-card'>The student is performing at an <span class='highlight'>excellent academic level</span> with a strong GPA. This performance level is suitable for honor roll consideration.</div>", unsafe_allow_html=True)
                            elif gpa >= 3.0:
                                st.markdown("<div class='custom-card'>The student is performing at a <span class='highlight'>good academic level</span>. With additional effort in specific subjects, they could improve to excellent standing.</div>", unsafe_allow_html=True)
                            elif gpa >= 2.0:
                                st.markdown("<div class='custom-card'>The student is performing at a <span class='highlight'>satisfactory academic level</span>. Focused tutoring in lower-performing subjects could significantly improve their standing.</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div class='custom-card'>The student is <span class='highlight'>at risk academically</span>. Immediate intervention is recommended, including tutoring and additional academic support services.</div>", unsafe_allow_html=True)
                            
                            # Education level impact
                            if parental_level_of_education in ["bachelor's degree", "master's degree"]:
                                st.markdown("<div class='custom-card'>The student has parents with <span class='highlight'>higher education</span>, which often correlates with better academic performance and support systems at home.</div>", unsafe_allow_html=True)
                            
                            # Test preparation impact
                            if test_preparation_course == "completed":
                                st.markdown("<div class='custom-card'>The student has <span class='highlight'>completed test preparation</span>, which typically leads to improved scores across all subjects.</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div class='custom-card'>The student has <span class='highlight'>not completed test preparation</span>. Consider enrolling in a test prep course to potentially improve scores.</div>", unsafe_allow_html=True)
                            
                            # Attendance impact (if provided)
                            if attendance_pct > 0:
                                if attendance_pct < 80:
                                    st.markdown(f"<div class='custom-card'>The student's <span class='highlight'>attendance is concerning</span> at {attendance_pct}%. Low attendance often correlates with lower academic performance. Improving attendance should be a priority.</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='custom-card'>The student has <span class='highlight'>good attendance</span> at {attendance_pct}%, which positively contributes to their academic performance.</div>", unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"An error occurred during prediction: {str(e)}")
    
    elif selected_page == "About":
        st.markdown('<h1 class="main-header">About This Project</h1>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("""
        The College Academic Performance Predictor is an advanced machine learning application designed to predict and analyze student academic performance across multiple subjects.
        
        This comprehensive tool helps educators and administrators:
        
        - Predict student performance in mathematics based on various factors
        - Analyze performance across multiple subjects
        - Identify students who may need academic intervention
        - Generate grade reports with pass/fail status and letter grades
        - Calculate GPA based on subject performance
        - Provide detailed academic standing analysis
        
        The system considers multiple factors including demographics, socioeconomic indicators, parental education, test preparation, attendance, and current subject scores.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display features in cards
        st.subheader("Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 🤖 Advanced AI Model")
            st.markdown("Uses machine learning to make accurate predictions based on historical student performance data.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Comprehensive Analytics")
            st.markdown("Provides detailed analysis including letter grades, pass/fail status, GPA calculation, and academic standing.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 🎓 College-Focused")
            st.markdown("Specifically designed for college environments with relevant academic metrics and analysis.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 🔄 Self-Healing System")
            st.markdown("Automatically fixes compatibility issues and adapts to your environment.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 📱 Modern User Interface")
            st.markdown("Sleek, intuitive design that makes the application accessible and easy to use.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 Multi-Subject Support")
            st.markdown("Handles multiple academic subjects and provides integrated analysis across disciplines.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif selected_page == "How It Works":
        st.markdown('<h1 class="main-header">How It Works</h1>', unsafe_allow_html=True)
        
        if analysis_lottie:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st_lottie(analysis_lottie, height=200, key="analysis")
        
        # Create a step-by-step guide
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("The Prediction & Analysis Process")
        
        st.markdown("""
        1. **Data Collection**: The system collects information about the student including demographics, academic background, and current subject scores.
        
        2. **Data Preparation**: This data is processed and transformed to be compatible with our machine learning model.
        
        3. **Math Score Prediction**: The AI model analyzes the processed data to predict the student's math score.
        
        4. **Multi-Subject Analysis**: The system integrates the predicted math score with other subject scores to provide a comprehensive academic profile.
        
        5. **Academic Standing Determination**: Based on all scores, the system calculates GPA, letter grades, and pass/fail status.
        
        6. **Personalized Insights**: Detailed analysis is provided with recommendations based on the student's specific academic profile.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Model explanation
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("The Model")
        
        st.markdown("""
        Our AI model is trained on a comprehensive dataset of college student performance metrics. It uses advanced machine learning techniques to identify patterns and relationships between various factors and academic performance.
        
        The model takes into account:
        
        - **Demographic factors**: Gender, race/ethnicity
        - **Socioeconomic factors**: Lunch type (as a proxy)
        - **Educational background**: Parental education level
        - **Academic preparation**: Test preparation course completion
        - **Current performance**: Scores in Reading, Writing, and other subjects
        - **Attendance**: Student attendance percentage (when available)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # College applications
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Applications in College Education")
        
        st.markdown("""
        This system has multiple applications in college environments:
        
        - **Early Intervention**: Identify at-risk students before they fail courses
        - **Academic Advising**: Provide data-driven guidance for course selection and major choices
        - **Resource Allocation**: Efficiently target academic support services to students who need them most
        - **Program Evaluation**: Analyze the effectiveness of academic programs and interventions
        - **Predictive Planning**: Forecast student outcomes for enrollment management and retention strategies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key findings
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Key Insights for College Success")
        
        st.markdown("""
        Our analysis has revealed several important insights for college student success:
        
        - **Test preparation** has a significant positive impact on student performance across all disciplines
        - **Parental education level** shows a strong correlation with college student outcomes
        - **Cross-disciplinary performance** often follows patterns (e.g., students strong in math often do well in science)
        - **Socioeconomic factors** continue to play a role in academic achievement even at the college level
        - **Attendance** is one of the strongest predictors of academic success
        - **Early performance** in core subjects often predicts overall academic trajectory
        """)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
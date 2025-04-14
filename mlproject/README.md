# Student Performance Predictor

A machine learning application for predicting student math scores based on various factors including gender, ethnicity, parental education level, lunch type, test preparation course, and reading/writing scores.

## Features

- Machine learning model trained on student performance data
- Streamlit interactive dashboard with visualization
- Self-healing model compatibility feature
- Auto-regenerating model if compatibility issues arise

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd mlproject
```

2. Create and activate a virtual environment:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

You can run the application in two ways:

### Option 1: Direct Streamlit Run

```
streamlit run streamlit_app.py
```

### Option 2: Using Helper Script (recommended)

```
python run_app.py
```

This script will automatically check for and install dependencies if needed.

The application will open automatically in your default web browser.

## Project Structure

- `src/`: Source code for utility functions and exception handling
- `artifacts/`: Contains the trained model, preprocessor, and data
- `streamlit_app.py`: Main Streamlit application that handles everything
- `run_app.py`: Helper script to run the application

## Model Information

The model predicts student math scores based on the following features:
- Gender
- Race/Ethnicity
- Parental Level of Education
- Lunch Type
- Test Preparation Course
- Reading Score
- Writing Score

## Troubleshooting

If you encounter any issues with the model, the application includes a self-healing feature that will automatically retrain the model with compatible settings for your environment.

## License

This project is licensed under the MIT License.
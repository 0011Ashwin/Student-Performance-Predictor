# College Academic Performance Predictor

An AI-powered application that predicts academic performance based on various student attributes.

## Deployment Instructions

### Local Deployment

1. Install the required dependencies:
   ```
   pip install -r mlproject/requirements.txt
   ```

2. Run the application:
   ```
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud Deployment

1. Connect your GitHub repository to Streamlit Cloud.
2. Select the main branch and the root directory.
3. The app entry point is `streamlit_app.py` in the root directory.
4. The requirements file is at `mlproject/requirements.txt`.

## Project Structure

- `streamlit_app.py`: Main entry point that imports and runs the app
- `mlproject/`: Contains the core application code
  - `streamlit_app.py`: The main Streamlit application
  - `requirements.txt`: Required dependencies
  - `src/`: Source code for prediction pipeline

## Features

- Predicts math scores based on student demographics and other academic scores
- Visualizes grade distribution and pass/fail status
- Provides overall GPA calculation 
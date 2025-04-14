import os
import sys
from src.exception import CustomException
from src.logger import logging
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

def train_model():
    try:
        # Initialize data ingestion
        logging.info("Starting data ingestion")
        data_ingestion = DataIngestion()
        train_data_path, test_data_path = data_ingestion.initiate_data_ingestion()
        
        # Initialize data transformation
        logging.info("Starting data transformation")
        data_transformation = DataTransformation()
        train_arr, test_arr, _ = data_transformation.initiate_data_transformation(train_data_path, test_data_path)
        
        # Initialize model trainer
        logging.info("Starting model training")
        model_trainer = ModelTrainer()
        model_trainer.initiate_model_trainer(train_arr, test_arr)
        
        logging.info("Model training completed successfully")
        print("Model training completed successfully!")

     # Handl exception of customer   
    except Exception as e:
        raise CustomException(e, sys)

if __name__ == "__main__":
    train_model() 
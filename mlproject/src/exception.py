import sys
from src.logger import logging

def error_message_detail(error,error_detail:sys):
    _,_,exc_tb=error_detail.exc_info()
    file_name=exc_tb.tb_frame.f_code.co_filename
    error_message="Error occured in python script name [{0}] line number [{1}] error message[{2}]".format(
     file_name,exc_tb.tb_lineno,str(error))

    return error_message

    

class CustomException(Exception):
    """Custom exception class for handling errors in the application"""
    
    def __init__(self, error_message, error_detail=None):
        """
        Initialize the custom exception with error message and details
        
        Args:
            error_message: The error message to display
            error_detail: Details of the error (typically from sys.exc_info())
        """
        super().__init__(error_message)
        self.error_message = error_message
        self.error_detail = error_detail if error_detail else sys.exc_info()
        
    def __str__(self):
        """
        String representation of the exception
        
        Returns:
            Formatted error message with file and line information
        """
        _, _, exc_tb = self.error_detail
        error_location = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        
        return f"Error in {error_location} at line {line_number}: {self.error_message}"
    


        
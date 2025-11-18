"""
Utility functions for the CML Lab Builder
"""

import sys
import traceback
from typing import Dict, Any, Union
from .client import get_client


def check_auth() -> Union[None, Dict[str, str]]:
    """
    Check if the client is authenticated
    
    Returns:
        None if authenticated, error dictionary if not
    """
    if not get_client():
        return {"error": "You must initialize the client first with initialize_client()"}
    return None


def handle_api_error(operation: str, error: Exception) -> Dict[str, Any]:
    """
    Handle API errors consistently
    
    Args:
        operation: Description of the operation that failed
        error: Exception that was raised
    
    Returns:
        Error dictionary with consistent format
    """
    print(f"Error during {operation}: {str(error)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return {"error": f"Error during {operation}: {str(e)}"}

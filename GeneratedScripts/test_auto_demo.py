"""
test_auto_demo.py

This module provides a simple function to return a greeting message.
"""

def get_greeting():
    """
    Returns a greeting message.

    Returns:
        str: A greeting message 'Hello World'.

    Raises:
        Exception: If an unexpected error occurs.
    """
    try:
        return "Hello World"
    except Exception as e:
        raise Exception("An error occurred while getting the greeting message.") from e

if __name__ == "__main__":
    try:
        print(get_greeting())
    except Exception as error:
        print(f"Error: {error}")
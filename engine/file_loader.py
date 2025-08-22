"""
Loads the template file from disk.
"""
import os

def load_template_file(filename: str) -> str:
    """
    Loads the template file and returns its content as a string.
    Args:
        filename (str): The name of the template file (e.g., 'template.txt').
    Returns:
        str: The content of the template file.
    """
    base_path: str = os.path.dirname(os.path.dirname(__file__))
    file_path: str = os.path.join(base_path, filename)
    with open(file_path, "r") as f:
        template_content: str = f.read()
    return template_content

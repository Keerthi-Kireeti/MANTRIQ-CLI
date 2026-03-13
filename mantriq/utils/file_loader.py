import os

def load_file(file_path: str) -> str:
    """Loads code from a file and returns its content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

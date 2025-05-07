from uuid import uuid4
from datetime import datetime
import os
import subprocess, shutil
import re

def generate_uuid():
    return str(uuid4())

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dir(path: str):
    """
    Create directory at `path` (including any missing parents),
    but do nothing if it already exists.
    """
    os.makedirs(path, exist_ok=True)
    
def run_r_script(path_to_r: str) -> str:
    # find Rscript on your PATH
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError(
            "Rscript.exe not found on PATH. "
            "Install R and add its bin/ folder to your PATH."
        )

    result = subprocess.run(
        [rscript, path_to_r],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout

def fetch_sample_lines(filename, lines):
    """
    Reads the first n lines from a CSV file.
    
    Args:
        filename (str): Path to the CSV file
        lines (int): Number of lines to read
        
    Returns:
        str: The first n lines of the file as a string
    """
    with open(filename, 'r') as f:
        return ''.join(f.readline() for _ in range(lines))


def strip_code_block(text: str) -> str:
    # Strips fencing (``` or """ with optional language tag) and
    # any extraneous leading/trailing quotes from a code block.
    lines = text.splitlines()
    all_lines = []

    # 1) Drop the opening fence if present
    if lines and re.match(r'^\s*(?:```|""")[^\n]*', lines[0]):
        lines = lines[1:]

    # 2) Drop the closing fence if present
    if lines and re.match(r'^\s*(?:```|""")\s*$', lines[-1]):
        lines = lines[:-1]

    # 3) Strip leading quotes from first line
    if lines:
        lines[0] = re.sub(r'^"+\s*', '', lines[0])

    # 4) Strip trailing quotes from last line
    if len(lines) > 1:
        lines[-1] = re.sub(r'\s*"+$', '', lines[-1])

    return "\n".join(lines).strip()
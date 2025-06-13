from pathlib import Path
from typing import List
import os

def get_file_info(path: Path) -> dict:
    """Get detailed information about a file"""
    stat = path.stat()
    return {
        "name": path.name,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
    }

def list_directory(path: Path) -> List[dict]:
    """List all files in directory with their information"""
    files = []
    for item in path.iterdir():
        if item.is_file():
            files.append(get_file_info(item))
    return files
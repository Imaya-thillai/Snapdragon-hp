"""
FileCore Windows File Explorer Integration
Opens real Windows File Explorer at specific file/folder locations.
"""
import os
import subprocess
import sys


def open_in_explorer(path: str) -> dict:
    """Open Windows File Explorer at the given path, selecting the file if it exists."""
    if not os.path.exists(path):
        return {"status": "error", "message": f"Path does not exist: {path}"}

    try:
        if sys.platform == "win32":
            if os.path.isfile(path):
                # Select the specific file in Explorer
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                subprocess.Popen(f'explorer "{path}"')
        else:
            # Fallback for development on non-Windows
            subprocess.Popen(["xdg-open", os.path.dirname(path)])
        
        return {"status": "success", "message": f"Opened Explorer at: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def open_file(path: str) -> dict:
    """Open a file with its default Windows application."""
    if not os.path.exists(path):
        return {"status": "error", "message": f"File not found: {path}"}
    try:
        os.startfile(path)
        return {"status": "success", "message": f"Opened: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

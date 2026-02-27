import json
from pathlib import Path
from config import UPLOAD_DIR

def get_annotation_path(pdf_name: str) -> Path:
    """Get the path to the annotation JSON file for a PDF."""
    return Path(UPLOAD_DIR) / f"{pdf_name}.annotations.json"

def load_annotations(pdf_name: str) -> dict:
    """Load annotations for a PDF file."""
    path = get_annotation_path(pdf_name)
    if path.exists():
        return json.loads(path.read_text())
    return {"highlights": [], "notes": []}

def save_annotations(pdf_name: str, data: dict):
    """Save annotations for a PDF file."""
    path = get_annotation_path(pdf_name)
    path.write_text(json.dumps(data, indent=2))

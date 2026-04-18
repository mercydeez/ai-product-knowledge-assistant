"""Helpers for reading product knowledge data."""

import json
from pathlib import Path


def load_json(file_path: str) -> list[dict]:
    """Load JSON data from the given file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise Exception(f"File not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON format") from exc

    if not isinstance(data, list):
        raise Exception("Product dataset must be a JSON array")

    return data


def save_json(data: list[dict], file_path: str) -> None:
    """Save JSON data to the given file path."""
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

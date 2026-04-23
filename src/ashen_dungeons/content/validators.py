from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .errors import ContentValidationError


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_against_schema(data, schema, source_name: str) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if errors:
        messages = []
        for error in errors:
            path = ".".join(str(p) for p in error.path) or "<root>"
            messages.append(f"{source_name}: {path}: {error.message}")
        raise ContentValidationError("\n".join(messages))
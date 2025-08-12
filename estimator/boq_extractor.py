from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from .parsing import BoQItem, extract_boq_from_paths


def gather_input_files(inputs: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file():
                    files.append(child)
        elif p.is_file():
            files.append(p)
    # Keep only supported types
    supported = [p for p in files if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}]
    return supported


def extract_boq(inputs: Iterable[str]) -> List[BoQItem]:
    files = gather_input_files(inputs)
    return extract_boq_from_paths(files)


def boq_items_to_dicts(items: List[BoQItem]) -> List[dict]:
    return [asdict(it) for it in items]
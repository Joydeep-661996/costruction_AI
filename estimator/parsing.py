from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None  # type: ignore

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None  # type: ignore

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore


@dataclass
class BoQItem:
    item_id: Optional[str]
    description: str
    unit: Optional[str]
    quantity: Optional[float]
    activity: Optional[str] = None


def is_pdf(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def is_image(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


_number_re = re.compile(r"(?<![\w.])([0-9]+(?:\.[0-9]+)*)")
_quantity_re = re.compile(r"(?<![\w.])([0-9]+(?:\.[0-9]+)?)\s*(m2|m3|m|kg|t|ton|tons|no\.?|nos\.?|lot|sqm|cum|sq\.m|cu\.m|pc|pcs|piece|pieces|set|sets|l|liter|litre|ltr|hr|hour|day|month|year|mm|cm|km)\b", re.IGNORECASE)
_unit_only_re = re.compile(r"\b(m2|m3|m|kg|t|ton|tons|no\.?|nos\.?|lot|sqm|cum|sq\.m|cu\.m|pc|pcs|piece|pieces|set|sets|l|liter|litre|ltr|hr|hour|day|month|year|mm|cm|km)\b", re.IGNORECASE)


def _normalize_cell(cell: Optional[str]) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", cell).strip()


def extract_tables_from_pdf(pdf_path: Path) -> List[List[List[str]]]:
    if pdfplumber is None:
        return []
    tables: List[List[List[str]]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            try:
                page_tables = page.extract_tables() or []
                normalized_tables: List[List[List[str]]] = []
                for tbl in page_tables:
                    normalized_tables.append([[ _normalize_cell(c) for c in row] for row in tbl])
                if normalized_tables:
                    tables.extend(normalized_tables)
            except Exception:
                continue
    return tables


def extract_text_lines_from_pdf(pdf_path: Path) -> List[str]:
    if pdfplumber is None:
        return []
    lines: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            try:
                text = page.extract_text() or ""
                page_lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
                lines.extend(page_lines)
            except Exception:
                continue
    return lines


def extract_text_from_image(image_path: Path) -> List[str]:
    if Image is None or pytesseract is None:
        return []
    try:
        img = Image.open(str(image_path))
        text = pytesseract.image_to_string(img)
        return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
    except Exception:
        return []


_line_patterns: List[re.Pattern[str]] = [
    # Pattern 1: item, description, quantity, unit
    re.compile(
        r"^(?:(?P<item>[0-9]+(?:\.[0-9]+)*)\s+)?(?P<desc>.+?)\s+(?P<qty>[0-9]+(?:\.[0-9]+)?)\s*(?P<unit>[A-Za-z/.]+)$",
        re.IGNORECASE,
    ),
    # Pattern 2: item, description, unit, quantity
    re.compile(
        r"^(?:(?P<item>[0-9]+(?:\.[0-9]+)*)\s+)?(?P<desc>.+?)\s+(?P<unit>[A-Za-z/.]+)\s*(?P<qty>[0-9]+(?:\.[0-9]+)?)$",
        re.IGNORECASE,
    ),
]


def parse_boq_line(line: str) -> Optional[BoQItem]:
    for pat in _line_patterns:
        m = pat.match(line)
        if m:
            item_id = (m.group("item") or "").strip() or None
            desc = (m.group("desc") or "").strip()
            qty_str = (m.group("qty") or "").strip()
            unit = (m.group("unit") or "").strip() or None
            try:
                qty = float(qty_str)
            except Exception:
                qty = None
            if desc:
                return BoQItem(item_id=item_id, description=desc, unit=unit, quantity=qty)
    # Fallback: try to find quantity+unit anywhere in the line
    m2 = _quantity_re.search(line)
    if m2:
        qty_str, unit = m2.group(1), m2.group(2)
        desc = line[: m2.start()].strip(" -:")
        try:
            qty = float(qty_str)
        except Exception:
            qty = None
        if desc:
            return BoQItem(item_id=None, description=desc, unit=unit, quantity=qty)
    return None


def extract_boq_from_pdf(pdf_path: Path) -> List[BoQItem]:
    items: List[BoQItem] = []
    # Try tables first
    for table in extract_tables_from_pdf(pdf_path):
        header_detected = False
        for row in table:
            cols = [c for c in row if c is not None]
            if not cols or all(not c.strip() for c in cols):
                continue
            joined = " ".join(cols)
            if not header_detected and re.search(r"description|item|qty|quantity|unit", joined, re.IGNORECASE):
                header_detected = True
                continue
            candidate = parse_boq_line(joined)
            if candidate:
                items.append(candidate)
    # Fallback to text lines
    if not items:
        for ln in extract_text_lines_from_pdf(pdf_path):
            candidate = parse_boq_line(ln)
            if candidate:
                items.append(candidate)
    return items


def extract_boq_from_image(image_path: Path) -> List[BoQItem]:
    items: List[BoQItem] = []
    for ln in extract_text_from_image(image_path):
        candidate = parse_boq_line(ln)
        if candidate:
            items.append(candidate)
    return items


def extract_boq_from_paths(paths: Iterable[Path]) -> List[BoQItem]:
    all_items: List[BoQItem] = []
    for p in paths:
        if is_pdf(p):
            all_items.extend(extract_boq_from_pdf(p))
        elif is_image(p):
            all_items.extend(extract_boq_from_image(p))
    # Deduplicate by (description, unit, quantity) to avoid duplicates across multiple sources
    unique: List[BoQItem] = []
    seen = set()
    for it in all_items:
        key = (it.description.lower(), (it.unit or "").lower(), it.quantity)
        if key not in seen:
            seen.add(key)
            unique.append(it)
    return unique
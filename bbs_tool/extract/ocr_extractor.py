from __future__ import annotations
from typing import List
import io
import numpy as np
import cv2
from PIL import Image
import pytesseract

from ..models.schemas import BBSItem


def preprocess_image_for_ocr(data: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(data)).convert("L")
    img = np.array(image)
    img = cv2.resize(img, None, fx=1.0, fy=1.0, interpolation=cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 25, 15)
    return img


def extract_from_image(data: bytes) -> List[BBSItem]:
    try:
        img = preprocess_image_for_ocr(data)
    except Exception as ex:
        raise RuntimeError(f"Image preprocessing failed: {ex}")

    try:
        # Use pytesseract to extract TSV data
        tsv = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
    except Exception as ex:
        raise RuntimeError("Tesseract not available or OCR failed. Install tesseract-ocr or provide CSV input.") from ex

    # Very minimal heuristic: expect a header row with known columns
    # Filter rows with reasonable confidence
    tsv = tsv.dropna(subset=['text'])
    tsv = tsv[tsv['conf'].astype(float) > 30]

    # Group by line and reconstruct rows
    rows: List[str] = []
    for _, grp in tsv.groupby(['page_num', 'block_num', 'par_num', 'line_num']):
        line = " ".join(str(t).strip() for t in grp['text'] if isinstance(t, str))
        if line:
            rows.append(line)

    # Extremely naive parsing: look for tokens and build items
    # Users are encouraged to upload CSV for reliable extraction in this initial version.
    items: List[BBSItem] = []
    for line in rows:
        tokens = [tok.strip() for tok in line.replace(',', ' ').split() if tok.strip()]
        if len(tokens) < 4:
            continue
        # Heuristic: BAR MARK, DIA, SHAPE, QTY, dims A,B,... present as A=xxx B=yyy
        bar_mark = tokens[0]
        try:
            dia_candidates = [float(tok) for tok in tokens if tok.replace('.', '', 1).isdigit()]
        except Exception:
            dia_candidates = []
        diameter = dia_candidates[0] if dia_candidates else 0.0
        shape = "STRAIGHT"
        for tok in tokens:
            up = tok.upper()
            if up in {"STRAIGHT", "L_90", "L90", "L_135", "L135", "U_135_OPEN", "STIRRUP_RECT"}:
                shape = up.replace("L90", "L_90").replace("L135", "L_135")
        dims = {}
        quantity = 1
        for tok in tokens:
            if '=' in tok:
                k, v = tok.split('=', 1)
                k = k.upper()
                try:
                    dims[k] = float(v)
                except ValueError:
                    pass
            if tok.upper().startswith('QTY'):
                try:
                    quantity = int(tok.split('=')[-1])
                except Exception:
                    pass
        if diameter > 0 and bar_mark:
            items.append(BBSItem(bar_mark=bar_mark, diameter_mm=diameter, shape=shape, dims_mm=dims, quantity=quantity))

    return items
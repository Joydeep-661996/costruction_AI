# BBS Tool (Automated Bar Bending Schedule)

An API and minimal UI to extract, recognize, calculate, validate, and generate Bar Bending Schedules (BBS).

## Quickstart

- Python 3.10+
- Optional: Tesseract OCR binary for image OCR (`pytesseract` will try to use it). If not present, the OCR extractor will gracefully skip.

```bash
python -m pip install -r requirements.txt
uvicorn bbs_tool.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/` for the minimal UI.

## Design

- Backend: FastAPI
- OCR: OpenCV preprocessing + optional `pytesseract`
- Shape recognition: Heuristics + mappable shape descriptors
- Calculations: Configurable IS 2502-like defaults (bend allowances, hooks, unit weight `d^2/162`)
- Validation: Sanity checks for dimensions per diameter, minimum bend radius, required dims per shape
- UI: Simple static HTML that calls the API

## Assumptions and Notes

- Dimensions in calculations are interpreted as centreline lengths unless explicitly provided as edge-to-edge with an accompanying offset. Centreline-based inputs are recommended for consistency.
- Bend allowances and hook extensions are configurable via `bbs_tool/calc/is2502.py`. Defaults are reasonable but must be reviewed by your QA with reference to the relevant IS code and project specifications.
- PDF table extraction is stubbed; image OCR and CSV upload are supported in this initial version.

## API

- POST `/api/extract` — Upload an image or CSV; returns structured items. For now, PDF support is limited.
- POST `/api/calculate` — Provide items + config override; returns cutting lengths, weights, and warnings.
- POST `/api/generate` — Upload and get calculated BBS plus CSV download payload.

## Tests

Basic sanity tests are included in `tests/`. You can run:

```bash
pytest -q
```

## Disclaimer

This tool provides a configurable implementation aligned with common interpretations of IS 2502 practices, but you must validate all outputs against your internal QA processes and the latest codes/specifications. Adjust configuration as required.
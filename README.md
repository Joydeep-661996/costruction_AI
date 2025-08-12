# Construction Project Estimator

Extracts Bill of Quantities (BOQ) from tender documents and construction drawings (PDF/images), matches items to a unit rate database, and produces total estimates and reports.

## Features
- Parse PDFs (text and simple tables) and images (OCR optional) to extract BOQ-like lines
- Match items to unit rates using keyword and unit rules
- Compute totals, per-activity breakdown, and export CSV/Excel + HTML summary
- Simple Streamlit UI for ad-hoc use

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note: OCR for images uses `pytesseract` which requires the Tesseract binary installed on your system (optional).

## Rates CSV Format
Create a CSV with headers: `keyword,unit,unit_rate,activity` (activity optional). Examples:
```csv
keyword,unit,unit_rate,activity
excavation,m3,12.5,Earthworks
concrete,m3,95,Concrete Works
rebar,kg,1.2,Reinforcement
* ,m,5,General per meter
* ,m2,8,General per sqm
```
Rules:
- `keyword`: substring matched against the description (case-insensitive). Use `*` for unit-only default.
- `unit`: leave blank to ignore units; otherwise must match the BOQ unit.
- `unit_rate`: numeric.
- `activity`: optional label used for per-activity totals.

## CLI Usage
```bash
python -m estimator.cli \
  --inputs /path/to/docs /path/to/another/dir \
  --rates /path/to/rates.csv \
  --output-dir /path/to/output \
  --contingency-pct 10 \
  --tax-pct 5
```
Outputs:
- `estimate.csv` and (if supported) `estimate.xlsx`
- `summary.html` with grand total and per-activity breakdown

## Optional Web App
A Streamlit web UI is scaffolded in `webapp/app.py` but may be disabled on restricted environments. Focus on the CLI usage above.

## Notes & Limitations
- Parsing of complex BOQ tables and CAD drawings is heuristic and may require manual review.
- For best results, provide reasonably clean PDFs with structured tables.
- Extend `estimator/parsing.py` and your rates CSV to improve matching.
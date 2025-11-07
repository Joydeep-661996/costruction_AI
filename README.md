# Construction AI - Intelligent Tools for Infrastructure Development

This repository contains AI-powered tools for the construction and infrastructure sector, including automated bar bending schedule generation and water management solutions.

## 🚀 Projects

### 1. BBS Tool (Automated Bar Bending Schedule)

An API and minimal UI to extract, recognize, calculate, validate, and generate Bar Bending Schedules (BBS).

### 2. Water Management Application (Analysis Phase)

Market analysis and strategic planning for a Water Management Application targeting India's Jal Jeevan Mission (JJM) and AMRUT schemes.

📊 **[View Market Analysis →](MARKET_COMPETITOR_ANALYSIS.md)**  
📋 **[Quick Reference Guide →](MARKET_ANALYSIS_SUMMARY.md)**

---

## BBS Tool

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

---

## 📚 Documentation

- **[Market Competitor Analysis](MARKET_COMPETITOR_ANALYSIS.md)** - Comprehensive analysis for Water Management Application (905 lines)
- **[Market Analysis Summary](MARKET_ANALYSIS_SUMMARY.md)** - Quick reference guide with visual data (342 lines)
- **[Setup Guide](SETUP_DESKTOP.md)** - Desktop installation instructions

## 📂 Repository Structure

```
├── bbs_tool/              # Bar Bending Schedule API and tools
├── construction_scheduler/ # Construction scheduling utilities
├── tests/                 # Test suite
├── MARKET_COMPETITOR_ANALYSIS.md  # Water management market analysis
├── MARKET_ANALYSIS_SUMMARY.md     # Quick reference guide
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please ensure all code changes are tested and documented.

## 📄 License

See individual project directories for license information.
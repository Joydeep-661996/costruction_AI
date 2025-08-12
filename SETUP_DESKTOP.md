### Run on Desktop

Option A) Docker (recommended)

1) Build image
```bash
docker build -t bbs-tool:latest .
```
2) Run container
```bash
docker run --rm -p 8000:8000 bbs-tool:latest
```
3) Open UI: http://localhost:8000/

Option B) Native (Linux/macOS)

1) Ensure Python 3.10+ installed; install Tesseract (optional for OCR):
- Ubuntu/Debian: `sudo apt-get install -y tesseract-ocr`
- macOS: `brew install tesseract`

2) Run start script
```bash
chmod +x start.sh
./start.sh
```

3) Open UI: http://localhost:8000/

Windows (PowerShell)

```powershell
py -3 -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn bbs_tool.main:app --host 0.0.0.0 --port 8000
```

Notes
- For OCR, Tesseract must be installed on the host.
- Default port is 8000; change with `--port`.
- Tests: `pytest -q`.
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import io
import csv

from .models.schemas import BBSItem, BBSCalculationConfig, BBSCalculationRequest, BBSCalculationResponse
from .extract.ocr_extractor import extract_from_image
from .calc.is2502 import calculate_cutting_length_for_item, unit_weight_kg_per_m
from .validation.validators import validate_item

app = FastAPI(title="BBS Tool API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (
        ("""
        <!doctype html>
        <html>
        <head>
            <meta charset='utf-8'/>
            <meta name='viewport' content='width=device-width, initial-scale=1'/>
            <title>BBS Tool</title>
            <style>
              body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
              .card { border: 1px solid #ddd; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
              input, select, button { padding: 8px; margin: 6px 0; }
              pre { background: #f6f8fa; padding: 12px; overflow: auto; }
              .row { display: flex; gap: 24px; flex-wrap: wrap; }
              .col { flex: 1; min-width: 320px; }
            </style>
        </head>
        <body>
          <h2>Automated Bar Bending Schedule (BBS)</h2>
          <div class='row'>
            <div class='col'>
              <div class='card'>
                <h3>1) Extract</h3>
                <form id='extractForm'>
                  <label>Source type:</label>
                  <select name='source_type'>
                    <option value='csv'>CSV</option>
                    <option value='image'>Image</option>
                  </select>
                  <br/>
                  <input type='file' name='file' accept='.csv,image/*' required />
                  <br/>
                  <button type='submit'>Extract</button>
                </form>
                <pre id='extractOutput'></pre>
              </div>
            </div>
            <div class='col'>
              <div class='card'>
                <h3>2) Calculate</h3>
                <form id='calcForm'>
                  <textarea id='itemsJson' placeholder='Paste items JSON array here' style='width:100%; height:160px;'></textarea>
                  <button type='submit'>Calculate</button>
                </form>
                <pre id='calcOutput'></pre>
              </div>
            </div>
          </div>
          <script>
            const extractForm = document.getElementById('extractForm');
            const extractOutput = document.getElementById('extractOutput');
            extractForm.addEventListener('submit', async (e) => {
              e.preventDefault();
              const formData = new FormData(extractForm);
              const res = await fetch('/api/extract', { method: 'POST', body: formData });
              const json = await res.json();
              extractOutput.textContent = JSON.stringify(json, null, 2);
              const itemsField = document.getElementById('itemsJson');
              itemsField.value = JSON.stringify(json.items || [], null, 2);
            });

            const calcForm = document.getElementById('calcForm');
            const calcOutput = document.getElementById('calcOutput');
            calcForm.addEventListener('submit', async (e) => {
              e.preventDefault();
              const itemsText = document.getElementById('itemsJson').value;
              try {
                const payload = { items: JSON.parse(itemsText) };
                const res = await fetch('/api/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const json = await res.json();
                calcOutput.textContent = JSON.stringify(json, null, 2);
              } catch(err) {
                calcOutput.textContent = 'Invalid JSON: ' + err?.message;
              }
            });
          </script>
        </body>
        </html>
        """)
    )


class ExtractResponse(BaseModel):
    items: List[BBSItem]
    warnings: List[str] = []


@app.post("/api/extract", response_model=ExtractResponse)
async def extract(source_type: str = Form(...), file: UploadFile = File(...)) -> Any:
    warnings: List[str] = []
    content = await file.read()

    items: List[BBSItem] = []
    if source_type == "csv":
        try:
            text = content.decode("utf-8")
        except Exception:
            text = content.decode("latin-1")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            item = BBSItem.from_csv_row(row)
            items.append(item)
    elif source_type == "image":
        try:
            items = extract_from_image(content)
        except Exception as ex:
            warnings.append(f"OCR extraction failed: {ex}")
            items = []
    else:
        warnings.append("Unsupported source_type. Use 'csv' or 'image'.")

    return ExtractResponse(items=items, warnings=warnings)


@app.post("/api/calculate", response_model=BBSCalculationResponse)
def calculate(req: BBSCalculationRequest) -> BBSCalculationResponse:
    results: List[Dict[str, Any]] = []
    warnings: List[str] = []
    config = req.config or BBSCalculationConfig()

    for item in req.items:
        item_warnings = validate_item(item, config)
        warnings.extend(item_warnings)
        try:
            cutting_length_mm = calculate_cutting_length_for_item(item, config)
            unit_wt = unit_weight_kg_per_m(item.diameter_mm, config)
            total_length_m = (cutting_length_mm / 1000.0) * item.quantity
            total_weight_kg = unit_wt * total_length_m
            results.append({
                "bar_mark": item.bar_mark,
                "shape": item.shape,
                "diameter_mm": item.diameter_mm,
                "cutting_length_mm": round(cutting_length_mm, 1),
                "unit_weight_kg_per_m": round(unit_wt, 4),
                "quantity": item.quantity,
                "total_length_m": round(total_length_m, 3),
                "total_weight_kg": round(total_weight_kg, 3),
            })
        except Exception as ex:
            warnings.append(f"Calculation failed for {item.bar_mark}: {ex}")

    return BBSCalculationResponse(results=results, warnings=warnings)


@app.post("/api/generate")
def generate():
    return JSONResponse({"message": "Not implemented in this initial version. Use /api/extract then /api/calculate."})
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Automated Bar Bending Schedule (BBS) Tool", version="0.1.0")

# CORS for local UI testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/upload-drawing")
async def upload_drawing(file: UploadFile = File(...)):
    """Upload a drawing file (image/PDF) and trigger BBS generation (placeholder)."""
    # TODO: Save file temporarily, call OCR + shape detection + calculations
    return {"filename": file.filename, "detail": "Processing not yet implemented"}
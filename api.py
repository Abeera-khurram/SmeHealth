"""
API Layer
-----------
Thin FastAPI wrapper around the existing agentic_layer and
sonography_reporting modules, so the dashboard in frontend/ has something to
call. No business logic lives here - it only translates HTTP requests into
calls against the existing Python modules and serializes the results.

Run: uvicorn api:app --reload
Docs: http://127.0.0.1:8000/docs
"""
import os
import shutil
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agentic_layer.orchestrator import run_preop_workflow

app = FastAPI(title="SmeHealth API", version="1.0.0")

# Wide-open CORS for local dev - the dashboard is a static file opened
# straight from disk or served by a different local port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/preop")
def preop(patient_id: str = Form(...), drug_name: str = Form(...)):
    """Runs the full pre-op agentic workflow (dosage + readiness + resource
    conflicts) and returns the physician review packet."""
    try:
        result = run_preop_workflow(patient_id=patient_id, drug_name=drug_name)
    except RuntimeError as e:
        # Most likely a missing GROQ_API_KEY - surface it clearly instead of
        # a raw 500.
        raise HTTPException(status_code=503, detail=str(e))
    return result["physician_packet"]


@app.post("/api/sonography")
def sonography(screenshot: UploadFile = File(...), audio: UploadFile = File(...)):
    """Accepts a sonography machine screenshot + a voice annotation and
    returns a merged structured report."""
    # Imported lazily so the whisper model (and its download) only loads
    # when this endpoint is actually used.
    from sonography_reporting.report_generator import generate_report

    with tempfile.TemporaryDirectory() as tmp:
        screenshot_path = os.path.join(tmp, screenshot.filename or "screenshot.png")
        audio_path = os.path.join(tmp, audio.filename or "annotation.wav")

        with open(screenshot_path, "wb") as f:
            shutil.copyfileobj(screenshot.file, f)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        try:
            report = generate_report(screenshot_path, audio_path)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    return report


# Serve the dashboard itself at "/" so the whole thing can be opened from
# one URL: http://127.0.0.1:8000/
_frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

"""
FileCore FastAPI Server — Web Dashboard Backend
Runs locally on http://127.0.0.1:8001 (different port from Project Turtle's 8000)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json

from filecore.db.database import init_db, get_all_files, get_audit_log
from filecore.core.indexer import index_directory, find_duplicates
from filecore.core.search import search, find_sensitive_files, find_recent_files
from filecore.core.security import scan_file
from filecore.core.document_intel import summarize_document
from filecore.core.policy import request_action
from filecore.hsal.hsal import hsal
from filecore.ai.ai_runtime import ai_runtime

init_db()

app = FastAPI(title="FileCore Local Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static ui directory if it exists
ui_dir = os.path.join(os.path.dirname(__file__), "ui")
if os.path.exists(ui_dir):
    app.mount("/static", StaticFiles(directory=ui_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join(ui_dir, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>FileCore UI missing</h1><p>Expected index.html in filecore/ui</p>"

@app.get("/api/status")
def status():
    files = get_all_files()
    sensitive = find_sensitive_files()
    dupes = find_duplicates()
    hsal_s = hsal.get_status()
    ai_s = ai_runtime.get_status()
    return {
        "files_indexed": len(files),
        "sensitive_files": len(sensitive),
        "duplicate_groups": len(dupes),
        "ai_status": ai_s,
        "hsal_status": hsal_s,
        "network_mode": "OFFLINE / LOCAL MODE",
    }

@app.get("/api/search")
def api_search(q: str = Query(...), limit: int = 20):
    results = search(q, limit=limit)
    return {"query": q, "count": len(results), "results": results}

@app.post("/api/index")
def api_index(path: str = Form(...)):
    if not os.path.isdir(path):
        return {"status": "error", "message": f"Not a directory: {path}"}
    result = index_directory(path)
    return {"status": "success", **result}

@app.get("/api/duplicates")
def api_duplicates():
    return {"duplicates": find_duplicates()}

@app.get("/api/sensitive")
def api_sensitive():
    return {"sensitive_files": find_sensitive_files()}

@app.get("/api/recent")
def api_recent(limit: int = 20):
    return {"recent_files": find_recent_files(limit)}

@app.post("/api/analyze")
async def api_analyze(file: UploadFile = File(...)):
    # Save temp file for scanning
    import tempfile, shutil
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    result = scan_file(tmp_path)
    os.unlink(tmp_path)
    result["original_filename"] = file.filename
    return result

@app.post("/api/summarize")
async def api_summarize(file: UploadFile = File(...)):
    import tempfile, shutil
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    result = summarize_document(tmp_path)
    os.unlink(tmp_path)
    return result

@app.post("/api/action")
def api_action(action: str = Form(...), target: str = Form(...),
               confirmed: bool = Form(False), cmd: str = Form("")):
    return request_action(action, target, confirmed, extra={"cmd": cmd})

@app.get("/api/audit")
def api_audit(limit: int = 50):
    return {"events": get_audit_log(limit)}

@app.get("/api/hsal")
def api_hsal():
    return hsal.get_status()

if __name__ == "__main__":
    uvicorn.run("filecore_api:app", host="127.0.0.1", port=8001, reload=True)

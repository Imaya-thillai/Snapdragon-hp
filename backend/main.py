from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="SatyaShield AI Offline API")

# Allow frontend to access the backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tauri local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "offline_server_running", "qnn_ep_active": False} 

@app.post("/api/check_message")
async def check_message(image: UploadFile = File(...)):
    # TODO: Integrate local PaddleOCR + Quantized LLM via ml_pipeline.py
    return {
        "verdict": "Likely Scam", 
        "explanation": "This matches a known 'Fake KYC' pattern.", 
        "pattern_matched": "Fake KYC"
    }

@app.post("/api/check_call")
async def check_call(audio: UploadFile = File(...)):
    # TODO: Integrate Whisper + Quantized LLM via ml_pipeline.py
    return {
        "verdict": "Uncertain", 
        "explanation": "Transcription complete. Checking against scam scripts...", 
        "pattern_matched": None
    }

@app.post("/api/check_document")
async def check_document(image: UploadFile = File(...)):
    # TODO: Integrate OCR + RAG for Govt Schemes via rag_store.py
    return {
        "verdict": "Looks Genuine", 
        "explanation": "This appears to be a valid PM-Kisan notice. Here is what to do next...", 
        "scheme_matched": "PM-Kisan"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

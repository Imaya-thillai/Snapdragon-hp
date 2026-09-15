from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our new Turtle services
from services.ml_pipeline import ml_pipeline
from services.hedera_agent import hedera_agent

app = FastAPI(title="Project Turtle API")

# Allow frontend to access the backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "offline_server_running", "project": "Turtle"} 

@app.post("/api/verify_eco_claim")
async def verify_eco_claim(image: UploadFile = File(...), claim_type: str = Form(...)):
    """
    1. Runs the image through the local AI vision model.
    2. If verified, hands it to the Hedera Agent to queue for DLT sync.
    """
    # Step 1: Offline AI Verification
    verification_result = ml_pipeline.verify_ecological_claim(image.filename, claim_type)
    
    if verification_result["verified"]:
        # Step 2: Queue for Hedera Sync
        claim_record = {
            "claim_type": claim_type,
            "filename": image.filename,
            "ai_confidence": verification_result["confidence"],
            "ai_analysis": verification_result["analysis"]
        }
        queued_item = hedera_agent.add_to_queue(claim_record)
        return {"status": "success", "message": "Claim verified and queued for Hedera sync.", "data": queued_item}
    else:
        return {"status": "rejected", "message": verification_result["analysis"], "data": None}

@app.get("/api/queue_status")
def queue_status():
    """Returns the current state of the offline queue."""
    queue = hedera_agent.get_queue()
    pending = [item for item in queue if item['status'] == 'pending_sync']
    synced = [item for item in queue if item['status'] == 'synced']
    return {"pending_count": len(pending), "synced_count": len(synced), "queue": queue}

@app.post("/api/sync_hedera")
def sync_hedera():
    """Triggers the agent to push pending claims to the Hedera network."""
    result = hedera_agent.sync_to_hedera()
    return {"status": "success", "message": f"Synced {result['synced_count']} items to Hedera DLT.", "data": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

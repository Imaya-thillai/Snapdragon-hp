# Project Turtle 🐢

**An offline-first, AI-driven sustainability agent network integrating the Hedera DLT with Snapdragon NPU edge processing.**

Built for the Hedera Hackathon, **Project Turtle** solves the connectivity problem in ecological data collection. It empowers environmental workers (tree planters, ocean cleanup crews) in remote, offline areas to verify their ecological impact using local AI. Once connected to the internet, the autonomous agent syncs with the Hedera network to log immutable proofs and issue tokenized micro-rewards (DeFi).

### Hackathon Themes Addressed:
*   **Theme 1: AI & Agents:** An autonomous background agent manages the queue and handles Hedera interactions.
*   **Theme 2: DeFi & Tokenization:** Ecological actions are tokenized into micro-rewards upon consensus.
*   **Theme 3: Sustainability:** Incentivizes and cryptographically verifies regenerative actions.

---


## 🏗️ Architecture & Flowchart

The system operates on an offline-first paradigm. Data is verified on-device using the Snapdragon NPU, queued locally, and synced asynchronously when an internet connection is established.

```mermaid
graph TD
    classDef user fill:#2c3e50,stroke:#34495e,color:#ecf0f1;
    classDef ui fill:#27ae60,stroke:#2ecc71,color:#fff;
    classDef backend fill:#8e44ad,stroke:#9b59b6,color:#fff;
    classDef ai fill:#c0392b,stroke:#e74c3c,color:#fff;
    classDef hedera fill:#2980b9,stroke:#3498db,color:#fff;

    A[Worker in Remote Area]:::user -->|Uploads Photo Offline| B(Tauri + React UI):::ui
    B -->|Sends Data| C{FastAPI Backend}:::backend
    C -->|Verifies Image| D[Snapdragon NPU ONNX Model]:::ai
    D -->|Confidence > 90%| E[(Local SQLite Queue)]:::backend
    E -.->|Internet Connection Restored| F((Hedera Sync Agent)):::hedera
    F -->|Logs Immutable Proof| G[Hedera Consensus Service]:::hedera
    F -->|Mints Micro-Rewards| H[Hedera Token Service]:::hedera
    H -->|Tokens Distributed| I[Worker's Wallet]:::user
```

---

## 🗺️ Roadmap

1.  **Phase 1: Proof of Concept (Current)**
    *   Offline Vision Verification Mockup.
    *   Local Queue Management.
    *   Hedera Sync Agent Simulation.
2.  **Phase 2: Hardware Acceleration**
    *   Full Snapdragon NPU integration via QNN Execution Provider.
    *   Optimized on-device models for diverse ecological verification.
3.  **Phase 3: Smart Contract & DeFi Integration**
    *   Live Hedera Testnet integration.
    *   Automated token issuance (HTS) based on HCS consensus.
4.  **Phase 4: Mobile Edge Deployment**
    *   Porting the React+Tauri architecture to mobile platforms (Android/iOS) for field workers.

---

## 📁 File Structure

```text
Snapdragon-hp/
├── backend/                    # Python Backend (FastAPI)
│   ├── main.py                 # Core API endpoints & server
│   └── services/
│       ├── hedera_agent.py     # Background agent syncing to Hedera (HCS/HTS)
│       └── ml_pipeline.py      # ONNX Runtime logic for NPU vision verification
├── frontend/                   # User Interface (React + Tauri)
│   ├── src/
│   │   ├── App.jsx             # Main dashboard (Offline queue, uploads)
│   │   ├── main.jsx            # React entry point
│   ├── package.json            # Frontend dependencies
├── filecore/                   # File Security Engine (Sibling module)
└── README.md                   # Project documentation
```
<img width="1297" height="670" alt="image" src="https://github.com/user-attachments/assets/ccee1abc-f82b-4791-9925-75fa339396f2" />

---

## 🚀 Setup Instructions

1.  **Start the Backend (AI & Hedera Agent):**
    ```bash
    python backend/main.py
    ```
2.  **Start the Frontend (UI):**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

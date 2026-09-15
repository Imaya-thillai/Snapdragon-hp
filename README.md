# Project Turtle 🐢

An **offline-first**, AI-driven sustainability agent network integrating the **Hedera DLT** with **Snapdragon NPU** edge processing. 

Built for the Hedera Hackathon, Project Turtle solves the connectivity problem in ecological data collection. It empowers environmental workers (tree planters, ocean cleanup crews) in remote, offline areas to verify their ecological impact using local AI. Once connected to the internet, the autonomous agent syncs with the Hedera network to log immutable proofs and issue tokenized micro-rewards (DeFi).

## Hackathon Themes Addressed
1. **Theme 1: AI & Agents** - An autonomous background agent manages the queue and handles Hedera interactions.
2. **Theme 2: DeFi & Tokenization** - Ecological actions are tokenized into micro-rewards upon consensus.
3. **Theme 3: Sustainability** - Incentivizes and cryptographically verifies regenerative actions.

## Architecture
* **Frontend:** React + Tauri (Offline-capable desktop/web shell)
* **Backend:** Local FastAPI server
* **Offline AI (Snapdragon):** ONNX Runtime (QNN Execution Provider) for on-device computer vision verification.
* **Agent Integration:** Python-based autonomous agent syncing offline queues to Hedera via simulated HCS and Token Services.

## Setup Instructions
1. Run `python backend/main.py` to start the offline AI and Hedera Agent.
2. Run `cd frontend && npm run dev` to start the UI.

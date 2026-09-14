# SatyaShield AI

An **offline-only**, on-device assistant designed for Snapdragon-powered PCs. It empowers everyday Indian users to detect scams (via messages or calls) and understand government documents without sacrificing privacy, running entirely without an internet connection.

## Architecture
* **Frontend:** React + Tauri (Voice-first, accessible UI)
* **Backend:** Local FastAPI server
* **Inference:** ONNX Runtime with the **Qualcomm Neural Network (QNN) Execution Provider**.
* **Vector Store:** ChromaDB (local persistence).

## Features
1. **Check a Message:** OCR + LLM vs known scam text patterns.
2. **Check a Call:** Whisper ASR + LLM vs known scam scripts.
3. **Check a Document:** OCR + RAG vs genuine government scheme database.

## Setup Instructions
*(Coming Soon - Full local build instructions)*

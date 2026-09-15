"""
FileCore Local AI Runtime Abstraction
Wraps any local inference engine (ONNX, llama.cpp, etc.).
Application gracefully degrades when no model is installed.
"""
import os


class LocalAIRuntime:
    """
    Abstraction layer for local AI inference.
    Replace the backend (ONNX session, llama.cpp binding, etc.)
    without changing any calling code.
    """

    def __init__(self):
        self.model_loaded = False
        self.model_name = None
        self._try_load()

    def _try_load(self):
        """Attempt to load a local model. Silently skip if not found."""
        model_path = os.environ.get("FILECORE_MODEL_PATH", "")
        if model_path and os.path.exists(model_path):
            try:
                import onnxruntime as ort
                self._session = ort.InferenceSession(
                    model_path,
                    providers=["QNNExecutionProvider", "CPUExecutionProvider"]
                )
                self.model_loaded = True
                self.model_name = os.path.basename(model_path)
                print(f"[AI] Local model loaded: {self.model_name}")
            except Exception as e:
                print(f"[AI] Model load failed: {e}. Degraded mode active.")
        else:
            print("[AI] No local model configured. Operating in offline degraded mode.")

    def is_available(self) -> bool:
        return self.model_loaded

    def summarize(self, text: str) -> str:
        """Generate a summary using the local model or fallback to extractive."""
        if not self.model_loaded:
            # Graceful degradation — local extractive summarization
            from filecore.core.document_intel import extract_keywords
            sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]
            return ". ".join(sentences[:5]) + "." if sentences else text[:300]

        # TODO: Tokenize, run inference via self._session, decode
        return "[LLM Output Placeholder — model session active]"

    def get_status(self) -> dict:
        return {
            "model_loaded": self.model_loaded,
            "model_name": self.model_name or "None",
            "mode": "LOCAL_LLM" if self.model_loaded else "DEGRADED_OFFLINE",
            "note": "Set FILECORE_MODEL_PATH env var to an ONNX model to enable full AI."
        }


# Singleton
ai_runtime = LocalAIRuntime()

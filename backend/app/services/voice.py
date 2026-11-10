"""Optional fully local speech-to-text adapter. No network model downloads are performed."""
import os
from pathlib import Path
from threading import Lock

_MODEL = None
_LOCK = Lock()

def _load_model():
    global _MODEL
    with _LOCK:
        if _MODEL is not None:
            return _MODEL
        configured = os.getenv("VOICE_MODEL_PATH", "models/faster-whisper-small")
        model_path = Path(configured)
        if not model_path.is_absolute():
            model_path = Path(__file__).resolve().parents[2] / model_path
        if not model_path.exists():
            raise FileNotFoundError(
                f"Offline speech model not found at {model_path}. Place a compatible "
                "faster-whisper model there and set VOICE_MODEL_PATH if needed."
            )
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel(str(model_path), device="cpu", compute_type="int8", local_files_only=True)
        return _MODEL

def transcribe_file(audio_path: str):
    model = _load_model()
    segments, info = model.transcribe(audio_path, beam_size=3, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return {"text": text, "language": info.language, "language_probability": round(float(info.language_probability), 3)}

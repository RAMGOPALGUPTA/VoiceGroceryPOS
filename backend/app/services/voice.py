"""Offline faster-whisper speech-to-text adapter.

The model is deliberately loaded from disk only. No inference-time downloads or
remote speech services are used.
"""
import importlib.util
import os
from pathlib import Path
from threading import Lock

_MODEL = None
_LOCK = Lock()


def configured_model_path() -> Path:
    configured = os.getenv("VOICE_MODEL_PATH", "models/faster-whisper-small")
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return path.resolve()


def voice_status() -> dict:
    model_path = configured_model_path()
    package_available = importlib.util.find_spec("faster_whisper") is not None
    model_available = model_path.is_dir() and any(model_path.iterdir())
    return {
        "enabled": package_available and model_available,
        "package_available": package_available,
        "model_available": model_available,
        "model_path": str(model_path),
        "message": (
            "Offline voice is ready."
            if package_available and model_available
            else "Install backend/requirements-voice.txt and run "
                 "python -m scripts.setup_voice_model to enable offline voice."
        ),
    }


def _load_model():
    global _MODEL
    with _LOCK:
        if _MODEL is not None:
            return _MODEL
        status = voice_status()
        if not status["package_available"]:
            raise ImportError(
                "Offline speech package is missing. Run: "
                "pip install -r requirements-voice.txt"
            )
        model_path = configured_model_path()
        if not status["model_available"]:
            raise FileNotFoundError(
                f"Offline speech model not found at {model_path}. "
                "Run: python -m scripts.setup_voice_model"
            )
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel(
            str(model_path),
            device=os.getenv("VOICE_DEVICE", "cpu"),
            compute_type=os.getenv("VOICE_COMPUTE_TYPE", "int8"),
            local_files_only=True,
        )
        return _MODEL


def transcribe_file(audio_path: str):
    model = _load_model()
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return {
        "text": text,
        "language": info.language,
        "language_probability": round(float(info.language_probability), 3),
    }

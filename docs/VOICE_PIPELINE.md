# Offline voice pipeline

## Runtime path

1. The desktop app requests microphone permission and records push-to-talk audio.
2. The audio is sent only to the local FastAPI process at 127.0.0.1.
3. The optional faster-whisper adapter loads a model from local disk with `local_files_only=True`.
4. The transcript is interpreted against product names, SKUs, brands and configured aliases.
5. Candidate lines are shown to the cashier. The cashier must explicitly add them to the cart.

## Install and prepare the offline runtime

Run these commands from `backend` with its virtual environment activated. The model download is a one-time setup step and requires internet access; speech recognition itself is local.

```powershell
pip install -r requirements-voice.txt
python -m scripts.setup_voice_model
```

The setup script downloads the multilingual `Systran/faster-whisper-small` model into `backend/models/faster-whisper-small`. Keep this folder on the same computer as the application. The runtime loads it with `local_files_only=True` and does not contact a model host.

The faster-whisper runtime uses PyAV for media decoding; a separate FFmpeg installation is normally not required. If a machine has a codec-related error, check the exact error before installing additional codecs.

Check readiness at `http://127.0.0.1:8000/api/v1/voice/status`. It reports whether the Python package and local model are both present. The desktop microphone control shows `LOCAL` when ready and `SETUP` when the optional voice runtime is missing.

If using a different local model directory, set `VOICE_MODEL_PATH` to that directory before starting the backend. Do not put model files in Git; they are large binary assets.

## Language and accuracy

Whisper multilingual models include Hindi (`hi`) and Punjabi (`pa`) language support, but mixed Punjabi/Hindi/English grocery phrases, local accents, brand names, numbers and units require a store-specific evaluation set. Do not enable unattended item insertion. Record anonymized evaluation phrases only with the store operator's consent; avoid retaining customer conversations.

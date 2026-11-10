# Offline voice pipeline

## Runtime path

1. The desktop app requests microphone permission and records push-to-talk audio.
2. The audio is sent only to the local FastAPI process at 127.0.0.1.
3. The optional faster-whisper adapter loads a model from local disk with `local_files_only=True`.
4. The transcript is interpreted against product names, SKUs, brands and configured aliases.
5. Candidate lines are shown to the cashier. The cashier must explicitly add them to the cart.

## Install the optional runtime

From the backend virtual environment:

```powershell
pip install -r requirements-voice.txt
```

Download/prepare a compatible faster-whisper model separately while internet is available and place its model files in `backend/models/faster-whisper-small`. Set `VOICE_MODEL_PATH` in the backend environment if using another local directory. Install FFmpeg and ensure it is available on PATH for WebM/MP3 decoding.

The application never downloads a speech model at runtime. If the model or optional package is missing, the voice API returns a clear 503 error and normal manual billing remains available.

## Language and accuracy

Whisper multilingual models include Hindi (`hi`) and Punjabi (`pa`) language support, but mixed Punjabi/Hindi/English grocery phrases, local accents, brand names, numbers and units require a store-specific evaluation set. Do not enable unattended item insertion. Record anonymized evaluation phrases only with the store operator's consent; avoid retaining customer conversations.

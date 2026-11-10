"""Download the multilingual faster-whisper model for offline use.

Run once while internet is available:
    python -m scripts.setup_voice_model
The desktop app then performs inference from local files only.
"""
from pathlib import Path


def main() -> None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "Missing model downloader. Run: pip install -r requirements-voice.txt"
        ) from exc

    destination = Path(__file__).resolve().parents[1] / "models" / "faster-whisper-small"
    destination.mkdir(parents=True, exist_ok=True)
    print("Downloading multilingual faster-whisper Small model (one-time setup)...")
    snapshot_download(
        repo_id="Systran/faster-whisper-small",
        local_dir=str(destination),
    )
    print(f"Model ready at: {destination}")
    print("Voice inference will run locally; no model download is performed at runtime.")


if __name__ == "__main__":
    main()

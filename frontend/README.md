# Desktop frontend

React + Vite renderer and Electron Windows shell for VoiceGroceryPOS.

## Development

1. Start the backend from `backend/` using `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
2. In this directory run `npm install`.
3. Run `npm run dev` for the browser UI, or `npm run desktop:dev` for Electron.

The initial renderer includes a catalogue view, local API health indicator, add-product form, and an in-memory cart. Checkout, voice capture, and printer controls remain disabled until their backend modules are implemented and tested.

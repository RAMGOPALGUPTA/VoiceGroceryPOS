from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.routes import router
from app.core.config import settings
from app.database.session import engine

app = FastAPI(title=settings.app_name, version='0.1.0', description='Offline grocery POS backend')
# The Electron renderer runs on a different local origin in development and
# file:// in packaged builds. No cookies or credentials are used by this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=False,
)
app.include_router(router, prefix='/api/v1')

@app.get('/health')
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        state = 'connected'
    except Exception as exc:
        state = 'unavailable'
    return {'status': 'ok' if state == 'connected' else 'degraded', 'database': state}

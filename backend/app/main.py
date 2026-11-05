from fastapi import FastAPI
from sqlalchemy import text
from app.api.routes import router
from app.core.config import settings
from app.database.session import engine

app = FastAPI(title=settings.app_name, version='0.1.0', description='Offline grocery POS backend')
app.include_router(router, prefix='/api/v1')

@app.get('/health')
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        state = 'connected'
    except Exception:
        state = 'unavailable'
    return {'status': 'ok' if state == 'connected' else 'degraded', 'database': state}

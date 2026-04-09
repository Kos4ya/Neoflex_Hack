from fastapi import FastAPI
from app.api.ws import router as ws_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(ws_router)


@app.get("/health")
async def healthcheck():
    return {"status": "ok", "service": settings.APP_NAME}
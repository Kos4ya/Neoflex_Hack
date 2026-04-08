from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .handlers import (
    sessions,
    code,
    notes,
    metrics
)

app = FastAPI(
    title="Session Service API",
    description="Микросервис управления сессиями интервью (код, заметки, метрики)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация роутеров
app.include_router(sessions.router)
app.include_router(code.router)
app.include_router(notes.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    return {
        "service": "Session Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .handlers import vacancies

from .database.session import init_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()


app = FastAPI(
    title="Vacancy Service API",
    description="Микросервис управления вакансиями",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vacancies.router)


@app.get("/")
async def root():
    return {"service": "Vacancy Service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
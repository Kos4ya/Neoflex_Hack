from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.handlers import auth, users

app = FastAPI(
    title="User Service API",
    description="Микросервис управления пользователями",
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

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"service": "User Service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
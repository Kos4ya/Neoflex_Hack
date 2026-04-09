from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .gateway import gateway

from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("API Gateway starting...")
    yield
    # Shutdown
    await gateway.close()
    logger.info("API Gateway stopped")


app = FastAPI(
    title="API Gateway",
    description="API Gateway для Neo Coding Board",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)


@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def users_proxy(request: Request, path: str):
    """Прокси для User Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.USER_SERVICE_URL,
        path=f"/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def auth_proxy(request: Request, path: str):
    """Прокси для аутентификации (User Service)"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.USER_SERVICE_URL,
        path=f"/auth/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/room/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def sessions_proxy(request: Request, path: str):
    """Прокси для Room Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.SESSION_SERVICE_URL,
        path=f"/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/vacancies/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def vacancies_proxy(request: Request, path: str):
    """Прокси для Vacancies Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.VACANCIES_SERVICE_URL,
        path=f"/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/candidates/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def candidates_proxy(request: Request, path: str):
    """Прокси для Candidates (через Vacancies Service)"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.VACANCIES_SERVICE_URL,
        path=f"/candidates/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/rooms/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def rooms_proxy(request: Request, path: str):
    """Прокси для Room Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.ROOM_SERVICE_URL,
        path=f"/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/interviews/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def interviews_proxy(request: Request, path: str):
    """Прокси для Interview Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.INTERVIEW_SERVICE_URL,
        path=f"/{path}",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.api_route("/api/v1/interviews", methods=["GET", "POST"])
async def interviews_root_proxy(request: Request):
    """Прокси для корневого эндпоинта Interview Service"""
    response = await gateway.proxy(
        request=request,
        service_url=settings.INTERVIEW_SERVICE_URL,
        path="/",
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.get("/health")
async def health():
    return {
        "service": settings.SERVICE_NAME,
        "status": "healthy",
        "services": {
            "user": settings.USER_SERVICE_URL,
            "session": settings.SESSION_SERVICE_URL,
            "vacancies": settings.VACANCIES_SERVICE_URL,
            "feedback": settings.FEEDBACK_SERVICE_URL,
        }
    }


@app.get("/")
async def root():
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "users": "/api/v1/users/*",
            "auth": "/api/v1/auth/*",
            "sessions": "/api/v1/rooms/*",
            "vacancies": "/api/v1/vacancies/*",
            "candidates": "/api/v1/candidates/*",
        }
    }
